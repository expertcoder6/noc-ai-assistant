import re
import hashlib
import structlog
from sqlalchemy import text
from .blocked_patterns import BLOCKED_PATTERNS

logger = structlog.get_logger()

async def scan_query(user_query: str, user_id: str, db_session=None) -> dict:
    """Normalize the user query, scan for prompt/SQL injection patterns, and log violations.
    
    If blocked:
      - Logs a security warning.
      - Attempts to write an audit_log record with error_message='BLOCKED:{pattern_type}'.
      - Returns {"blocked": True, "pattern_type": pattern_type}.
    """
    # 1. Normalize query: lowercase and collapse whitespace
    normalized = " ".join(user_query.lower().split())
    
    # 2. Check each compiled pattern case-insensitively
    for pattern, pattern_type in BLOCKED_PATTERNS:
        if re.search(pattern, normalized, re.IGNORECASE):
            # Calculate 16-char SHA-256 hash of the query for tracking
            query_hash = hashlib.sha256(user_query.encode("utf-8")).hexdigest()[:16]
            logger.warning(
                "security_blocked_query",
                user_id=user_id,
                query_hash=query_hash,
                pattern_type=pattern_type
            )
            
            # Write to audit_log table if db_session is provided
            if db_session:
                try:
                    stmt = text("""
                        INSERT INTO audit_log (user_id, user_question, error_message)
                        VALUES (:user_id, :user_question, :error_message)
                    """)
                    await db_session.execute(stmt, {
                        "user_id": user_id,
                        "user_question": user_query,
                        "error_message": f"BLOCKED:{pattern_type}"
                    })
                    await db_session.commit()
                except Exception as exc:
                    logger.error("security_audit_log_insert_failed", error=str(exc))
                    
            return {"blocked": True, "pattern_type": pattern_type}
            
    return {"blocked": False, "pattern_type": None}
