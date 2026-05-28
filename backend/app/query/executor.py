import asyncio
import structlog
from typing import List, Dict

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from ..config import get_settings

logger = structlog.get_logger()

async def execute_query(sql: str, params: dict, session: AsyncSession) -> List[Dict]:
    """Execute the provided SQL with parameters using the given async session.

    The function respects the global ``QUERY_TIMEOUT_SECONDS`` setting and returns a list of
    dictionaries (one per row). An empty list is returned when the query yields no rows.
    """
    settings = get_settings()
    timeout = getattr(settings, "QUERY_TIMEOUT_SECONDS", 5)
    try:
        async with asyncio.timeout(timeout):
            result = await session.execute(text(sql), params)
            rows = result.fetchall()
            # Convert Row objects to plain dicts preserving column names.
            data = [dict(row._mapping) for row in rows]
            logger.info(
                "query_executed",
                sql=sql,
                params=params,
                row_count=len(data),
                duration_ms=int(result.elapsed.total_seconds() * 1000) if hasattr(result, "elapsed") else None,
            )
            return data
    except asyncio.TimeoutError:
        logger.error("query_timeout", timeout=timeout)
        raise
    except Exception as exc:
        logger.error("query_failed", error=str(exc), sql=sql, params=params)
        raise
