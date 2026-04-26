"""
Precedent Search Tool
Searches for legal precedents from Indian courts.

Primary: Indian Kanoon official API (api.indiankanoon.org) — token auth, JSON, no scraping.
  Spec: https://api.indiankanoon.org/documentation/
Fallback: Firecrawl against the public indiankanoon.org site (may hit bot/CAPTCHA pages).
"""
import json
import os
import re
from typing import Any, Optional
from urllib.parse import quote_plus, urlencode

import requests
from dotenv import load_dotenv

from src.config import settings
from src.utils.logger import setup_logger

load_dotenv()
logger = setup_logger(__name__)

# Search endpoint; auth and query params per https://api.indiankanoon.org/documentation/
IK_API_SEARCH = "https://api.indiankanoon.org/search/"

# Heuristics: public site returned a challenge page instead of results
_BOT_BLOCK_PATTERNS = re.compile(
    r"(captcha|verify\s+you\s+are\s+human|security\s+check|"
    r"attention\s+required|enable\s+javascript|cf-browser-verification|"
    r"just\s+a\s+moment)",
    re.IGNORECASE,
)


def _ik_token() -> Optional[str]:
    return (settings.indiankanoon_api_token or os.getenv("INDIANKANOON_API_TOKEN") or "").strip() or None


def _build_form_input(
    query: str,
    jurisdiction: str,
    year_from: Optional[int],
    year_to: Optional[int],
) -> str:
    # formInput syntax: https://api.indiankanoon.org/documentation/ (matches IKAPI spacing)
    q = query.strip()
    if jurisdiction == "supreme_court":
        q = f"{q} doctypes: supremecourt"
    elif jurisdiction == "high_court":
        q = f"{q} doctypes: highcourts"
    # fromdate / todate: DD-MM-YYYY
    if year_from is not None:
        q = f"{q} fromdate: 1-1-{year_from}"
    if year_to is not None:
        q = f"{q} todate: 31-12-{year_to}"
    return q


def _search_indiankanoon_api(
    query: str,
    jurisdiction: str,
    year_from: Optional[int],
    year_to: Optional[int],
    max_results: int,
    token: str,
) -> dict[str, Any]:
    form_input = _build_form_input(query, jurisdiction, year_from, year_to)
    # IK search: pagenum starts at 0; maxpages caps how many result pages in one call
    maxpages = max(1, min((max_results + 9) // 10, 10))
    qs = urlencode(
        {
            "formInput": form_input,
            "pagenum": "0",
            "maxpages": str(maxpages),
        }
    )
    url = f"{IK_API_SEARCH}?{qs}"
    headers = {
        "Authorization": f"Token {token}",
        "Accept": "application/json",
    }
    logger.info("Indian Kanoon API search (POST)")
    response = requests.post(url, headers=headers, timeout=60)
    if response.status_code == 403:
        return {
            "error": "Indian Kanoon API returned 403",
            "hint": "Check INDIANKANOON_API_TOKEN; see https://api.indiankanoon.org/documentation/",
        }
    if response.status_code != 200:
        return {
            "error": f"Indian Kanoon API error: {response.status_code}",
            "message": response.text[:2000],
        }
    try:
        data = response.json()
    except json.JSONDecodeError as e:
        return {"error": "Invalid JSON from Indian Kanoon API", "details": str(e)}

    if isinstance(data, dict) and data.get("errmsg"):
        return {
            "query": query,
            "jurisdiction": jurisdiction,
            "error": data.get("errmsg"),
            "source": "Indian Kanoon API",
        }

    docs_raw = data.get("docs") if isinstance(data, dict) else None
    if not isinstance(docs_raw, list):
        return {
            "query": query,
            "jurisdiction": jurisdiction,
            "total_found": 0,
            "results": [],
            "message": "No results in API response",
            "source": "Indian Kanoon API",
            "raw_keys": list(data.keys()) if isinstance(data, dict) else [],
        }

    trimmed: list[dict[str, Any]] = []
    for doc in docs_raw[:max_results]:
        if not isinstance(doc, dict):
            continue
        tid = doc.get("tid")
        trimmed.append(
            {
                "tid": tid,
                "title": doc.get("title"),
                "headline": doc.get("headline"),
                "docsource": doc.get("docsource"),
                "publishdate": doc.get("publishdate"),
                "docsize": doc.get("docsize"),
                "numcites": doc.get("numcites"),
                "numcitedby": doc.get("numcitedby"),
                "url": f"https://indiankanoon.org/doc/{tid}/" if tid is not None else None,
            }
        )

    found = data.get("found") if isinstance(data, dict) else None
    categories = data.get("categories") if isinstance(data, dict) else None
    encoded = data.get("encodedformInput") if isinstance(data, dict) else None
    out: dict[str, Any] = {
        "query": query,
        "jurisdiction": jurisdiction,
        "filters": {"year_from": year_from, "year_to": year_to},
        "total_found": found,
        "results": trimmed,
        "source": "Indian Kanoon API",
        "search_metadata": {
            "api": "api.indiankanoon.org",
            "formInput": form_input,
        },
    }
    if encoded is not None:
        out["search_metadata"]["encodedformInput"] = encoded
    if categories:
        out["categories"] = categories
    return out


def _search_firecrawl_fallback(
    query: str,
    jurisdiction: str,
    year_from: Optional[int],
    year_to: Optional[int],
) -> dict[str, Any]:
    firecrawl_api_key = os.getenv("FIRECRAWL_API_KEY")
    if not firecrawl_api_key:
        logger.info("No FIRECRAWL_API_KEY found, returning mock precedent data for demo.")
        return {
            "query": query,
            "jurisdiction": jurisdiction,
            "filters": {"year_from": year_from, "year_to": year_to},
            "source": "Mock Legal Database (Demo Mode)",
            "search_url": "https://indiankanoon.org/search/?formInput=mock",
            "content": """
**1. Satish Chander Ahuja vs Sneha Ahuja (Supreme Court of India, 2020)**
**Citation:** (2021) 1 SCC 414
**Summary:** The Supreme Court held that the right to residence under Section 19 of the Domestic Violence Act is not restricted to a household owned or tenanted by the husband alone. If the wife has lived in a domestic relationship in a house owned by her father-in-law, it constitutes a "shared household" under Section 2(s) of the DV Act. The daughter-in-law has the right to reside there and cannot be evicted except in accordance with the procedure established by law. 

**2. S.R. Batra vs Taruna Batra (Supreme Court of India, 2006)**
**Citation:** (2007) 3 SCC 169
**Summary:** Earlier, the Court observed that a wife is only entitled to claim a right to residence in a shared household, and a 'shared household' would only mean the house belonging to or taken on rent by the husband. However, this definition was later expanded in the Satish Chander Ahuja case to include the father-in-law's property if she resided there in a domestic relationship.

**3. Prabha Tyagi vs Kamlesh Devi (Supreme Court of India, 2022)**
**Citation:** Criminal Appeal No. 511 of 2022
**Summary:** The Supreme Court affirmed that a domestic relationship can exist even if the aggrieved person is not physically residing in the shared household at the exact time of filing the complaint. The right of residence continues to be legally protected under the Domestic Violence Act.
            """,
            "full_content_length": 1500,
            "search_metadata": {
                "api_used": "Mock Demo",
                "source_website": "indiankanoon.org (simulated)",
            },
        }

    search_url = f"https://indiankanoon.org/search/?formInput={quote_plus(query)}"
    if jurisdiction == "supreme_court":
        search_url += "+doctypes:+supremecourt"
    elif jurisdiction == "high_court":
        search_url += "+doctypes:+highcourts"
    if year_from is not None:
        search_url += f"+fromdate:+1-1-{year_from}"
    if year_to is not None:
        search_url += f"+todate:+31-12-{year_to}"

    logger.info(f"Firecrawl fallback URL: {search_url}")
    firecrawl_url = "https://api.firecrawl.dev/v1/scrape"
    headers = {
        "Authorization": f"Bearer {firecrawl_api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "url": search_url,
        "formats": ["markdown", "html"],
        "onlyMainContent": True,
    }
    response = requests.post(firecrawl_url, json=payload, headers=headers, timeout=30)
    if response.status_code != 200:
        return {
            "error": f"Firecrawl API error: {response.status_code}",
            "message": response.text[:2000],
        }

    data = response.json()
    content = data.get("data", {}).get("markdown", "") or ""

    if not content.strip():
        return {
            "query": query,
            "jurisdiction": jurisdiction,
            "total_found": 0,
            "results": [],
            "message": "No results found or content could not be extracted",
            "hint": (
                "The public site may have blocked automated access. "
                "Configure INDIANKANOON_API_TOKEN for reliable results."
            ),
        }

    if _BOT_BLOCK_PATTERNS.search(content):
        return {
            "query": query,
            "jurisdiction": jurisdiction,
            "error": "Indian Kanoon returned a bot/security challenge page to the scraper",
            "hint": (
                "Use the official API: add INDIANKANOON_API_TOKEN per "
                "https://api.indiankanoon.org/documentation/ (token auth avoids public-site CAPTCHAs)."
            ),
            "search_url": search_url,
        }

    return {
        "query": query,
        "jurisdiction": jurisdiction,
        "filters": {"year_from": year_from, "year_to": year_to},
        "source": "IndianKanoon via Firecrawl (fallback)",
        "search_url": search_url,
        "content": content[:5000] + "..." if len(content) > 5000 else content,
        "full_content_length": len(content),
        "search_metadata": {
            "api_used": "Firecrawl",
            "source_website": "indiankanoon.org",
        },
    }


async def search_precedents(
    query: str,
    jurisdiction: str = "all",
    year_from: Optional[int] = None,
    year_to: Optional[int] = None,
    max_results: int = 5,
) -> str:
    """
    Search for legal precedents.

    Prefer INDIANKANOON_API_TOKEN + official API; Firecrawl is only a fallback.
    """
    logger.info(f"Searching precedents for: {query}")

    try:
        token = _ik_token()
        if token:
            result = _search_indiankanoon_api(
                query, jurisdiction, year_from, year_to, max_results, token
            )
            return json.dumps(result, indent=2, ensure_ascii=False)

        result = _search_firecrawl_fallback(query, jurisdiction, year_from, year_to)
        return json.dumps(result, indent=2, ensure_ascii=False)

    except requests.Timeout:
        logger.error("Precedent search request timeout")
        return json.dumps(
            {
                "error": "Request timeout",
                "message": "The search took too long. Try a more specific query.",
            },
            indent=2,
        )

    except Exception as e:
        logger.error(f"Error in precedent search: {str(e)}", exc_info=True)
        return json.dumps(
            {"error": str(e), "error_type": type(e).__name__},
            indent=2,
        )
