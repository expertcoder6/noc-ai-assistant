import json
import structlog
import time
import asyncio
from typing import List, Dict

import google.generativeai as genai
from google.generativeai.types import GenerationConfig
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from ..config import get_settings
from .prompts import INTENT_EXTRACTION_SYSTEM_PROMPT, RESPONSE_FORMATTING_SYSTEM_PROMPT

logger = structlog.get_logger()

class IntentExtractionError(Exception):
    """Raised when intent extraction from Gemini fails after retries."""

class ResponseFormattingError(Exception):
    """Raised when formatting the final response with Gemini fails after retries."""

class GeminiClient:
    def __init__(self) -> None:
        settings = get_settings()
        genai.configure(api_key=settings.GEMINI_API_KEY)
        # Intent extraction model – strict JSON output
        self.intent_model = genai.GenerativeModel(
            model_name=settings.GEMINI_MODEL,
            system_instruction=INTENT_EXTRACTION_SYSTEM_PROMPT,
            generation_config=GenerationConfig(
                temperature=0,
                response_mime_type="application/json",
                max_output_tokens=256,
            ),
        )
        # Response formatting model – more creative
        self.response_model = genai.GenerativeModel(
            model_name=settings.GEMINI_MODEL,
            system_instruction=RESPONSE_FORMATTING_SYSTEM_PROMPT,
            generation_config=GenerationConfig(
                temperature=0.3,
                max_output_tokens=512,
            ),
        )

    async def extract_intent(self, question: str) -> Dict:
        """Call Gemini to extract intent JSON from a natural‑language question.

        Uses a custom retry loop with specific delays and parses JSON robustly,
        stripping markdown fences if needed.
        """
        settings = get_settings()
        
        # Override config parameters as requested
        generation_config = GenerationConfig(
            temperature=0,
            top_p=0.1,
            max_output_tokens=300,
            response_mime_type="application/json"
        )
        
        delays = [0.0, 0.5, 1.0]
        last_exception = None
        
        for attempt in range(3):
            if delays[attempt] > 0.0:
                await asyncio.sleep(delays[attempt])
                
            start = time.time()
            try:
                # Call the Generative API synchronously in execution thread
                response = self.intent_model.generate_content(
                    [question],
                    generation_config=generation_config
                )
                latency_ms = int((time.time() - start) * 1000)
                logger.info("intent_extraction", latency_ms=latency_ms, question=question, attempt=attempt+1)
                
                text = response.text.strip()
                
                # Attempt 1: Raw JSON parse
                try:
                    result = json.loads(text)
                    return result
                except json.JSONDecodeError:
                    # Attempt 2: Clean markdown code fences and try again
                    cleaned_text = text
                    if cleaned_text.startswith("```"):
                        lines = cleaned_text.splitlines()
                        if lines[0].startswith("```"):
                            lines = lines[1:]
                        if lines and lines[-1].startswith("```"):
                            lines = lines[:-1]
                        cleaned_text = "\n".join(lines).strip()
                    
                    try:
                        result = json.loads(cleaned_text)
                        return result
                    except json.JSONDecodeError as exc:
                        raise IntentExtractionError(f"Failed to parse intent JSON: {exc}")
                        
            except Exception as exc:
                logger.warning("intent_extraction_attempt_failed", attempt=attempt+1, error=str(exc))
                last_exception = exc
                
        raise IntentExtractionError(f"Intent extraction failed after 3 attempts: {last_exception}")

    @retry(
        stop=stop_after_attempt(2),
        wait=wait_exponential(min=1, max=2),
        retry=retry_if_exception_type(Exception),
        reraise=True,
    )
    async def format_response(self, question: str, data: List[Dict], intent: str) -> str:
        """Format a final user‑facing answer using Gemini.

        The prompt includes the original question, the filtered data rows, and a system prompt
        describing the desired formatting. Returns the raw text response.
        """
        settings = get_settings()
        start = time.time()
        data_json = json.dumps(data, default=str, indent=2)
        prompt = f"Question: {question}\n\nData ({len(data)} rows):\n{data_json}\n\nAnswer:"
        response = self.response_model.generate_content([prompt])
        latency_ms = int((time.time() - start) * 1000)
        logger.info("response_formatting", latency_ms=latency_ms, question=question, rows=len(data))
        return response.text.strip()
