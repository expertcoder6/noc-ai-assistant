import re
from typing import Dict, Any, List

class SecurityValidationError(Exception):
    """Raised when query fails security hardening policy."""

PROMPT_INJECTION_KEYWORDS = [
    r"ignore\s+previous\s+instructions",
    r"reveal\s+system\s+prompt",
    r"bypass\s+security",
    r"drop\s+database",
    r"show\s+hidden\s+schema",
    r"override\s+role",
    r"you\s+are\s+now\s+an?\s+admin"
]

SQL_INJECTION_KEYWORDS = [
    r"\bUNION\b",
    r"\bDROP\b",
    r"\bDELETE\b",
    r"\bINSERT\b",
    r"\bUPDATE\b",
    r"\bALTER\b",
    r";",
    r"--"
]

def scan_prompt_injection(message: str) -> None:
    """Scan the natural language query for injection patterns.
    
    Raises SecurityValidationError if a pattern matches.
    """
    message_lower = message.lower()
    for pattern in PROMPT_INJECTION_KEYWORDS:
        if re.search(pattern, message_lower):
            raise SecurityValidationError("Request blocked by security policy.")

def sanitize_filters(filters: Any) -> None:
    """Sanitize extracted filter keys and values against SQL injection and unsafe patterns."""
    if hasattr(filters, "model_dump"):
        filters_dict = filters.model_dump()
    elif hasattr(filters, "dict"):
        filters_dict = filters.dict()
    elif isinstance(filters, dict):
        filters_dict = filters
    else:
        # Not a Pydantic model or dict, nothing to sanitize
        return

    for key, value in filters_dict.items():
        # Validate that values don't contain raw SQL keywords
        if isinstance(value, str):
            value_upper = value.upper()
            for kw in SQL_INJECTION_KEYWORDS:
                if re.search(kw, value_upper):
                    raise SecurityValidationError("Request blocked by security policy due to unsafe parameters.")
        elif isinstance(value, dict):
            # Recurse if filters are nested
            sanitize_filters(value)
        elif hasattr(value, "model_dump") or hasattr(value, "dict"):
            # Recurse if nested filter is a Pydantic model
            sanitize_filters(value)

