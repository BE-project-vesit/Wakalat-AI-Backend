"""
Deep Research Tool
Conducts deep legal research using Gemini (AI reasoning) and Firecrawl (web scraping).

Pipeline:
  1. Gemini decomposes the query into targeted sub-questions + search terms
  2. Firecrawl scrapes multiple Indian legal sources in parallel
  3. Gemini extracts structured legal content from each scraped page
  4. Gemini synthesizes all extractions into a final research report
"""
import asyncio
import json
from typing import Any, Callable, Coroutine, Literal, Optional

from src.config import settings
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

# Legal sources to crawl
LEGAL_SOURCES = [
    "https://indiankanoon.org/search/?formInput={query}",
    "https://www.indiacode.nic.in/handle/123456789/1362?locale=en&searchquery={query}",
]


# ---------------------------------------------------------------------------
# Pydantic schemas for structured Gemini output
# ---------------------------------------------------------------------------

DECOMPOSE_SCHEMA = {
    "type": "object",
    "properties": {
        "sub_questions": {
            "type": "array",
            "items": {"type": "string"},
            "description": "3-5 targeted sub-questions derived from the main query"
        },
        "search_terms": {
            "type": "array",
            "items": {"type": "string"},
            "description": "5-8 search terms/phrases optimised for IndianKanoon"
        },
        "key_statutes": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Acts or sections likely relevant to this query"
        }
    },
    "required": ["sub_questions", "search_terms", "key_statutes"]
}

EXTRACTION_SCHEMA = {
    "type": "object",
    "properties": {
        "relevant": {"type": "boolean"},
        "statutes": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "act_name": {"type": "string"},
                    "sections": {"type": "array", "items": {"type": "string"}},
                    "text": {"type": "string"},
                    "interpretation": {"type": "string"}
                },
                "required": ["act_name", "sections", "text", "interpretation"]
            }
        },
        "case_laws": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "case_name": {"type": "string"},
                    "citation": {"type": "string"},
                    "relevance": {"type": "string"},
                    "key_principles": {"type": "array", "items": {"type": "string"}},
                    "extract": {"type": "string"}
                },
                "required": ["case_name", "citation", "relevance", "key_principles", "extract"]
            }
        },
        "summary": {"type": "string"}
    },
    "required": ["relevant", "statutes", "case_laws", "summary"]
}

SYNTHESIS_SCHEMA = {
    "type": "object",
    "properties": {
        "executive_summary": {"type": "string"},
        "legal_analysis": {"type": "string"},
        "relevant_statutes": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "act_name": {"type": "string"},
                    "sections": {"type": "array", "items": {"type": "string"}},
                    "text": {"type": "string"},
                    "interpretation": {"type": "string"}
                },
                "required": ["act_name", "sections", "text", "interpretation"]
            }
        },
        "relevant_case_laws": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "case_name": {"type": "string"},
                    "citation": {"type": "string"},
                    "relevance": {"type": "string"},
                    "key_principles": {"type": "array", "items": {"type": "string"}},
                    "extract": {"type": "string"}
                },
                "required": ["case_name", "citation", "relevance", "key_principles", "extract"]
            }
        },
        "conclusion": {"type": "string"},
        "further_reading": {"type": "array", "items": {"type": "string"}}
    },
    "required": [
        "executive_summary", "legal_analysis", "relevant_statutes",
        "relevant_case_laws", "conclusion", "further_reading"
    ]
}


# ---------------------------------------------------------------------------
# Helper: Gemini client (lazy init)
# ---------------------------------------------------------------------------

def _get_gemini_client():
    try:
        from google import genai
        return genai.Client(api_key=settings.gemini_api_key)
    except ImportError:
        raise RuntimeError("google-genai package not installed. Run: pip install google-genai")


def _get_firecrawl_client():
    try:
        from firecrawl import FirecrawlApp
        return FirecrawlApp(api_key=settings.firecrawl_api_key)
    except ImportError:
        raise RuntimeError("firecrawl-py package not installed. Run: pip install firecrawl-py")


# ---------------------------------------------------------------------------
# Step 1: Decompose query
# ---------------------------------------------------------------------------

async def _decompose_query(client, query: str) -> dict:
    """Use Gemini to break the query into sub-questions and search terms."""
    prompt = (
        "You are an expert Indian lawyer and legal researcher.\n"
        "Analyse the following legal research query and return a JSON object with:\n"
        "- sub_questions: 3-5 specific sub-questions that together answer the main query\n"
        "- search_terms: 5-8 search phrases optimised for IndianKanoon (use legal terminology)\n"
        "- key_statutes: Acts/Codes likely relevant (e.g. 'Indian Penal Code', 'CPC 1908')\n\n"
        f"Query: {query}"
    )

    loop = asyncio.get_event_loop()
    response = await loop.run_in_executor(
        None,
        lambda: client.models.generate_content(
            model=settings.gemini_model,
            contents=prompt,
            config={
                "response_mime_type": "application/json",
                "response_schema": DECOMPOSE_SCHEMA,
            }
        )
    )
    return json.loads(response.text)


# ---------------------------------------------------------------------------
# Step 2: Crawl legal sources with Firecrawl
# ---------------------------------------------------------------------------

async def _crawl_single_url(firecrawl, url: str) -> dict | None:
    """Scrape a single URL, return {url, markdown} or None on failure."""
    try:
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None,
            lambda: firecrawl.scrape_url(url, params={"formats": ["markdown"]})
        )
        markdown = result.get("markdown") or ""
        if len(markdown.strip()) < 100:
            return None
        return {"url": url, "markdown": markdown[:8000]}  # cap per-page tokens
    except Exception as e:
        logger.warning(f"Firecrawl failed for {url}: {e}")
        return None


async def _crawl_sources(firecrawl, search_terms: list[str], depth: str) -> list[dict]:
    """Build URLs and crawl them in parallel. Returns list of {url, markdown}."""
    urls = []

    # IndianKanoon search for each term
    for term in search_terms[:5]:  # limit to 5 terms
        encoded = term.replace(" ", "+")
        urls.append(f"https://indiankanoon.org/search/?formInput={encoded}&pagenum=0")

    if depth == "comprehensive":
        # Add more terms
        for term in search_terms[5:]:
            encoded = term.replace(" ", "+")
            urls.append(f"https://indiankanoon.org/search/?formInput={encoded}&pagenum=0")

    tasks = [_crawl_single_url(firecrawl, url) for url in urls]
    results = await asyncio.gather(*tasks)
    return [r for r in results if r is not None]


# ---------------------------------------------------------------------------
# Step 3: Extract structured legal content from each page
# ---------------------------------------------------------------------------

async def _extract_from_page(client, page: dict, original_query: str) -> dict | None:
    """Ask Gemini to extract statutes and case laws from one scraped page."""
    prompt = (
        "You are an expert Indian lawyer. Analyse the following scraped legal text.\n"
        f"Original research query: {original_query}\n\n"
        "Extract all relevant information and return a JSON with:\n"
        "- relevant: true if this page contains useful information for the query\n"
        "- statutes: list of relevant statutory provisions found\n"
        "- case_laws: list of case citations found with key principles\n"
        "- summary: 2-3 sentence summary of what this page contributes\n\n"
        f"Source URL: {page['url']}\n\n"
        f"--- SCRAPED TEXT ---\n{page['markdown']}\n--- END ---"
    )

    try:
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None,
            lambda: client.models.generate_content(
                model=settings.gemini_model,
                contents=prompt,
                config={
                    "response_mime_type": "application/json",
                    "response_schema": EXTRACTION_SCHEMA,
                }
            )
        )
        data = json.loads(response.text)
        if not data.get("relevant"):
            return None
        return data
    except Exception as e:
        logger.warning(f"Extraction failed for {page['url']}: {e}")
        return None


# ---------------------------------------------------------------------------
# Step 4: Synthesize final report
# ---------------------------------------------------------------------------

async def _synthesize_report(
    client,
    query: str,
    decomposition: dict,
    extractions: list[dict],
    depth: str,
    include_statutes: bool,
    include_case_laws: bool,
) -> dict:
    """Gemini synthesizes all extracted content into a final research report."""

    # Deduplicate and flatten statutes + case laws from all extractions
    all_statutes = []
    all_cases = []
    all_summaries = []

    for ext in extractions:
        all_statutes.extend(ext.get("statutes", []))
        all_cases.extend(ext.get("case_laws", []))
        all_summaries.append(ext.get("summary", ""))

    context = json.dumps({
        "sub_questions": decomposition.get("sub_questions", []),
        "key_statutes_identified": decomposition.get("key_statutes", []),
        "extracted_statutes": all_statutes if include_statutes else [],
        "extracted_case_laws": all_cases if include_case_laws else [],
        "source_summaries": all_summaries,
    }, indent=2)

    depth_instruction = {
        "brief": "Provide a concise 1-page research brief.",
        "detailed": "Provide a detailed research memo with thorough analysis.",
        "comprehensive": "Provide a comprehensive legal research report with exhaustive analysis, all relevant case laws, and statutory references.",
    }[depth]

    prompt = (
        "You are a senior Indian lawyer preparing a legal research report.\n"
        f"Research Query: {query}\n\n"
        f"{depth_instruction}\n\n"
        "Using the extracted information below, synthesize a final research report as JSON.\n"
        "Deduplicate case citations. Rank statutes and cases by relevance.\n"
        "Ensure the conclusion directly answers the research query.\n\n"
        f"--- EXTRACTED DATA ---\n{context}\n--- END ---"
    )

    loop = asyncio.get_event_loop()
    response = await loop.run_in_executor(
        None,
        lambda: client.models.generate_content(
            model=settings.gemini_model,
            contents=prompt,
            config={
                "response_mime_type": "application/json",
                "response_schema": SYNTHESIS_SCHEMA,
            }
        )
    )
    return json.loads(response.text)


# ---------------------------------------------------------------------------
# Main public function
# ---------------------------------------------------------------------------

async def deep_research(
    research_query: str,
    research_depth: Literal["brief", "detailed", "comprehensive"] = "detailed",
    include_statutes: bool = True,
    include_case_laws: bool = True,
    progress_callback: Optional[Callable[..., Coroutine]] = None,
) -> str:
    """
    Conduct deep legal research using Gemini + Firecrawl.

    Args:
        research_query: The legal question or topic to research
        research_depth: Depth of research — brief | detailed | comprehensive
        include_statutes: Include statutory provisions in report
        include_case_laws: Include case law citations in report
        progress_callback: Optional async callback(progress, total, message) for progress reporting

    Returns:
        JSON string with structured research report
    """
    logger.info(f"Deep research started: '{research_query}' depth={research_depth}")

    async def _report(current: int, total: int, message: str):
        logger.info(message)
        if progress_callback:
            try:
                await progress_callback(current, total, message)
            except Exception as e:
                logger.warning(f"Progress callback failed: {e}")

    if not settings.gemini_api_key:
        return json.dumps({"error": "GEMINI_API_KEY not configured."})
    if not settings.firecrawl_api_key:
        return json.dumps({"error": "FIRECRAWL_API_KEY not configured."})

    try:
        gemini = _get_gemini_client()
        firecrawl = _get_firecrawl_client()

        # Step 1: Decompose
        await _report(1, 4, "Step 1/4: Decomposing query with Gemini...")
        decomposition = await _decompose_query(gemini, research_query)
        await _report(1, 4, f"Step 1/4 complete: Generated {len(decomposition.get('search_terms', []))} search terms")

        # Step 2: Crawl
        await _report(2, 4, "Step 2/4: Crawling legal sources with Firecrawl...")
        pages = await _crawl_sources(firecrawl, decomposition.get("search_terms", []), research_depth)
        await _report(2, 4, f"Step 2/4 complete: Scraped {len(pages)} pages successfully")

        if not pages:
            logger.warning("No pages scraped; falling back to Gemini-only synthesis")

        # Step 3: Extract (parallel)
        await _report(3, 4, f"Step 3/4: Extracting legal content from {len(pages)} pages...")
        extraction_tasks = [
            _extract_from_page(gemini, page, research_query) for page in pages
        ]
        raw_extractions = await asyncio.gather(*extraction_tasks)
        extractions = [e for e in raw_extractions if e is not None]
        await _report(3, 4, f"Step 3/4 complete: Got {len(extractions)} relevant extractions out of {len(pages)} pages")

        # Step 4: Synthesize
        await _report(4, 4, "Step 4/4: Synthesizing final report with Gemini...")
        report = await _synthesize_report(
            gemini, research_query, decomposition, extractions,
            research_depth, include_statutes, include_case_laws
        )

        result = {
            "research_query": research_query,
            "research_depth": research_depth,
            "sources_scraped": len(pages),
            "sources_relevant": len(extractions),
            "research_results": report,
        }

        await _report(4, 4, "Deep research completed successfully")
        return json.dumps(result, indent=2)

    except Exception as e:
        logger.error(f"Deep research failed: {e}", exc_info=True)
        return json.dumps({"error": str(e)})
