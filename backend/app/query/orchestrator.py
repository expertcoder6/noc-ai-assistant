# pyrefly: ignore [missing-import]
import structlog
import asyncio
from typing import List, Dict

from fastapi import HTTPException
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from ..config import get_settings
from ..llm.client import GeminiClient, IntentExtractionError, ResponseFormattingError
from ..llm.prompts import OUT_OF_SCOPE_RESPONSE, NO_RESULTS_RESPONSE
from .intent_validator import ParsedIntent
from .sql_builder import build_query
from .executor import execute_query

logger = structlog.get_logger()

class QueryOrchestrator:
    def __init__(self) -> None:
        self.llm = GeminiClient()
        self.settings = get_settings()

    async def process(self, question: str, db_session: AsyncSession) -> str:
        """Full pipeline: intent extraction → validation → DB query → response formatting.

        Returns a user‑facing string. Raises HTTPException for unrecoverable errors.
        """
        # 0. Prompt injection scan early-exit
        from ..security.prompt_guard import scan_query
        guard_res = await scan_query(question, "unknown", db_session)
        if guard_res["blocked"]:
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "Request blocked by security policy.",
                    "code": "SECURITY_BLOCKED"
                }
            )

        # 1. Extract intent (LLM call 1)
        try:
            raw_intent = await self.llm.extract_intent(question)
        except IntentExtractionError as exc:
            logger.error("intent_extraction_failed", error=str(exc))
            raise HTTPException(
                status_code=503,
                detail={"error": "AI service temporarily unavailable. Please try again."}
            )

        # 2. Validate intent JSON via Pydantic
        try:
            parsed: ParsedIntent = ParsedIntent(**raw_intent)
        except Exception as exc:
            logger.error("intent_validation_failed", error=str(exc))
            raise HTTPException(status_code=400, detail="Invalid intent format.")

        # 3. Handle out‑of‑scope early
        if parsed.intent == "out_of_scope":
            return OUT_OF_SCOPE_RESPONSE

        # 4. Build SQL and parameters
        try:
            sql, params = build_query(parsed.intent, parsed.validated_filters)
        except Exception as exc:
            logger.error("sql_build_failed", error=str(exc))
            raise HTTPException(status_code=500, detail="Failed to build query.")

        # 5. Execute query (may return empty list)
        try:
            rows: List[Dict] = await execute_query(sql, params, db_session)
        except asyncio.TimeoutError:
            logger.error("query_timeout")
            raise HTTPException(status_code=504, detail="Database query timed out.")
        except Exception as exc:
            logger.error("query_execution_failed", error=str(exc))
            raise HTTPException(status_code=500, detail="Database query failed.")

        # 6. If no rows, short‑circuit response
        if not rows:
            return NO_RESULTS_RESPONSE

        # 7. Format final answer via local Python Response Formatter (Replaces second Gemini call)
        from ..llm.response_formatter import format_response as format_response_py
        
        filters_dict = {}
        if parsed.validated_filters:
            if hasattr(parsed.validated_filters, "model_dump"):
                filters_dict = parsed.validated_filters.model_dump()
            elif hasattr(parsed.validated_filters, "dict"):
                filters_dict = parsed.validated_filters.dict()
            elif isinstance(parsed.validated_filters, dict):
                filters_dict = parsed.validated_filters

        answer, _ = format_response_py(parsed.intent, rows, filters_dict)
        return answer
