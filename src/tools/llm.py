"""
Shared LLM helper — Gemini by default, OpenAI/Anthropic as fallbacks.
Includes retry logic for transient 503/429 errors from Gemini.
"""
import asyncio
from src.config import settings
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

MAX_RETRIES = 3


async def call_llm(prompt: str, max_tokens: int = 3000) -> str:
    """Call Gemini (default), falling back to OpenAI then Anthropic.
    Retries automatically on transient 503/429 errors."""

    # 1. Gemini (primary)
    if settings.gemini_api_key:
        from google import genai

        client = genai.Client(
            api_key=settings.gemini_api_key,
            http_options={"api_version": "v1beta"},
        )

        last_error = None
        for attempt in range(MAX_RETRIES):
            try:
                response = client.models.generate_content(
                    model=settings.gemini_model,
                    contents=prompt,
                )
                return response.text or ""
            except Exception as e:
                last_error = e
                err_str = str(e).lower()
                is_retryable = "503" in err_str or "429" in err_str or "overloaded" in err_str or "resource exhausted" in err_str
                if is_retryable and attempt < MAX_RETRIES - 1:
                    wait_secs = (2 ** attempt) * 2  # 2s, 4s, 8s
                    logger.warning(f"Gemini API returned transient error (attempt {attempt + 1}/{MAX_RETRIES}). Retrying in {wait_secs}s... Error: {e}")
                    await asyncio.sleep(wait_secs)
                    continue
                else:
                    logger.error(f"Gemini API call failed after {attempt + 1} attempt(s): {e}")
                    raise last_error

    # 2. OpenAI (fallback)
    if settings.openai_api_key:
        from openai import AsyncOpenAI

        client = AsyncOpenAI(api_key=settings.openai_api_key)
        response = await client.chat.completions.create(
            model=settings.openai_model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=max_tokens,
        )
        return response.choices[0].message.content or ""

    # 3. Anthropic (fallback)
    if settings.anthropic_api_key:
        from anthropic import AsyncAnthropic

        client = AsyncAnthropic(api_key=settings.anthropic_api_key)
        response = await client.messages.create(
            model=settings.anthropic_model,
            max_tokens=max_tokens,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.content[0].text

    return "[No LLM API key configured. Set GEMINI_API_KEY in .env to enable AI-powered features.]"
