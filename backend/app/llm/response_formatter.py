import time
from ..query.response_templates import format_response as py_format_response

def format_response(intent: str, rows: list, filters: dict) -> tuple[str, int]:
    """Format operational database results using a pure Python response builder.
    
    Returns a tuple of (formatted_answer_string, elapsed_ms).
    """
    start = time.perf_counter()
    answer = py_format_response(intent, rows, filters)
    elapsed_ms = int((time.perf_counter() - start) * 1000)
    if elapsed_ms == 0:
        elapsed_ms = 1  # Standard 1ms minimum display
    return answer, elapsed_ms
