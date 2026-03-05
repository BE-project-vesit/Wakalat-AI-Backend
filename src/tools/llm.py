"""
Shared LLM helper — Gemini by default, OpenAI/Anthropic as fallbacks.
"""
from src.config import settings


async def call_llm(prompt: str, max_tokens: int = 3000) -> str:
    """Call Gemini (default), falling back to OpenAI then Anthropic."""

    # 1. Gemini (primary)
    if settings.gemini_api_key:
        from google import genai

        client = genai.Client(api_key=settings.gemini_api_key)
        response = client.models.generate_content(
            model=settings.gemini_model,
            contents=prompt,
        )
        return response.text or ""

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
