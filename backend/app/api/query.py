import time
from collections import defaultdict, deque
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from ..dependencies import get_db
from ..query.orchestrator import QueryOrchestrator
from ..auth.middleware import get_current_user
from ..auth.roles import has_permission
from ..security.protection import scan_prompt_injection, sanitize_filters, SecurityValidationError
from ..query.cache import global_query_cache
from ..monitoring.telemetry import QueryTelemetry
from ..query.intent_validator import ParsedIntent
from ..query.sql_builder import build_query
from ..query.executor import execute_query
from ..query.formatter import format_deterministic_response
from ..llm.prompts import OUT_OF_SCOPE_RESPONSE, NO_RESULTS_RESPONSE

router = APIRouter()

# Per-user sliding-window rate limiter (no external dependency)
# key: username -> deque of request timestamps (floats)
_request_log: dict = defaultdict(deque)

def _check_rate_limit(username: str, limit: int) -> None:
    """Enforce a per-user rate limit using a 60-second sliding window.

    Raises HTTP 429 if the user has exceeded ``limit`` requests in the last
    60 seconds. Thread-safe for a single-process Uvicorn worker.
    """
    now = time.time()
    window = _request_log[username]
    # Evict timestamps older than 60 s
    while window and window[0] < now - 60:
        window.popleft()
    if len(window) >= limit:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Rate limit exceeded: max {limit} queries per minute. Please wait before retrying.",
        )
    window.append(now)


class QueryRequest(BaseModel):
    message: str

@router.post("/query")
async def run_query(
    payload: QueryRequest,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Execute a natural language query with enterprise security, caching, and timing."""
    from ..security.prompt_guard import scan_query
    from ..config import get_settings

    username = current_user.get("username", "unknown")

    # 0. Rate limit check — must run before any expensive processing
    settings = get_settings()
    _check_rate_limit(username, settings.RATE_LIMIT_PER_MINUTE)

    guard_res = await scan_query(payload.message, username, db)
    if guard_res["blocked"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "Request blocked by security policy.",
                "code": "SECURITY_BLOCKED"
            }
        )

    # 1. Telemetry and Security Checks
    telemetry = QueryTelemetry()
    
    try:
        scan_prompt_injection(payload.message)
    except SecurityValidationError as exc:
        metrics = telemetry.finalize()
        return {
            "answer": str(exc),
            "intent": {"intent": "out_of_scope", "filters": {}},
            "data": [],
            "timing": {
                **metrics,
                "cache_hit": False
            }
        }

    user_role = current_user.get("role", "network_operator")
    
    # 2. Cache Lookup
    cached_response = global_query_cache.get(user_role, payload.message)
    if cached_response:
        telemetry.mark_cache(True)
        metrics = telemetry.finalize()
        # Return deep copy with updated timing metrics
        return {
            **cached_response,
            "cache_hit": True,
            "timing": {
                **metrics,
                "cache_hit": True
            }
        }

    orchestrator = QueryOrchestrator()
    
    # 3. Intent Extraction
    start_intent = time.time()
    from ..llm.client import IntentExtractionError
    try:
        raw_intent = await orchestrator.llm.extract_intent(payload.message)
    except IntentExtractionError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={"error": "AI service temporarily unavailable. Please try again."}
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to understand the query intent."
        )
    intent_ms = int((time.time() - start_intent) * 1000)
    telemetry.mark_intent(intent_ms)
    
    # 4. Validate Intent format
    try:
        parsed = ParsedIntent(**raw_intent)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid intent structure returned by analysis."
        )
        
    # 5. Role-Based Access Control (RBAC) Enforcement
    if not has_permission(user_role, parsed.intent):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Forbidden: Operator role '{user_role.upper()}' does not have permission to query '{parsed.intent}' telemetry."
        )
        
    # 6. Sanitize Filter Values (SQL Injection Check)
    try:
        sanitize_filters(parsed.validated_filters)
    except SecurityValidationError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc)
        )
        
    # 7. Out of Scope Check
    if parsed.intent == "out_of_scope":
        metrics = telemetry.finalize()
        response_payload = {
            "answer": OUT_OF_SCOPE_RESPONSE,
            "intent": raw_intent,
            "data": [],
            "cache_hit": False,
            "timing": {
                **metrics,
                "cache_hit": False
            }
        }
        global_query_cache.set(user_role, payload.message, response_payload)
        return response_payload
        
    # 8. Build SQL Query
    try:
        sql, params = build_query(parsed.intent, parsed.validated_filters)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to formulate operational database query."
        )
        
    # 9. Execute DB Query
    start_db = time.time()
    try:
        rows = await execute_query(sql, params, db)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Operational database query execution failed."
        )
    db_ms = int((time.time() - start_db) * 1000)
    telemetry.mark_db(db_ms)
    
    # 10. Handle no results
    if not rows:
        metrics = telemetry.finalize()
        response_payload = {
            "answer": NO_RESULTS_RESPONSE,
            "intent": raw_intent,
            "data": [],
            "cache_hit": False,
            "timing": {
                **metrics,
                "cache_hit": False
            }
        }
        global_query_cache.set(user_role, payload.message, response_payload)
        return response_payload
        
    # 11. Deterministic Python Formatting (Replaces 2nd Gemini LLM call)
    from ..llm.response_formatter import format_response as format_response_py
    
    filters_dict = {}
    if parsed.validated_filters:
        if hasattr(parsed.validated_filters, "model_dump"):
            filters_dict = parsed.validated_filters.model_dump()
        elif hasattr(parsed.validated_filters, "dict"):
            filters_dict = parsed.validated_filters.dict()
        elif isinstance(parsed.validated_filters, dict):
            filters_dict = parsed.validated_filters

    answer, format_ms = format_response_py(parsed.intent, rows, filters_dict)
    telemetry.mark_format(format_ms)
    
    # 12. Finalize & Cache Response
    metrics = telemetry.finalize()
    response_payload = {
        "answer": answer,
        "intent": raw_intent,
        "data": rows,
        "cache_hit": False,
        "timing": {
            **metrics,
            "cache_hit": False
        }
    }
    
    global_query_cache.set(user_role, payload.message, response_payload)
    return response_payload


