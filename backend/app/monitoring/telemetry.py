import uuid
import time
import structlog
from typing import Dict, Any, Optional

logger = structlog.get_logger()

class QueryTelemetry:
    def __init__(self, request_id: Optional[str] = None):
        self.request_id = request_id or str(uuid.uuid4())
        self.start_time = time.time()
        self.intent_ms = 0
        self.validation_ms = 0
        self.db_ms = 0
        self.format_ms = 0
        self.cache_hit = False
        self.total_ms = 0
        
    def mark_intent(self, duration_ms: int):
        self.intent_ms = duration_ms
        
    def mark_validation(self, duration_ms: int):
        self.validation_ms = duration_ms
        
    def mark_db(self, duration_ms: int):
        self.db_ms = duration_ms
        
    def mark_format(self, duration_ms: int):
        self.format_ms = duration_ms
        
    def mark_cache(self, hit: bool = True):
        self.cache_hit = hit
        
    def finalize(self) -> Dict[str, Any]:
        """Calculate total time, check SLA violations, and log structured metrics."""
        self.total_ms = int((time.time() - self.start_time) * 1000)
        sla_target = 3000
        sla_violation = self.total_ms > sla_target
        
        metrics = {
            "request_id": self.request_id,
            "intent_extraction_ms": self.intent_ms,
            "validation_ms": self.validation_ms,
            "db_query_ms": self.db_ms,
            "formatting_ms": self.format_ms,
            "total_ms": self.total_ms,
            "cache_hit": self.cache_hit,
            "sla_violation": sla_violation,
        }
        
        logger.info(
            "query_telemetry",
            **metrics
        )
        return metrics
