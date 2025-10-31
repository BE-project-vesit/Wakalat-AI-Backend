"""
Precedent Search Tool
Searches for legal precedents from Indian courts using Firecrawl API
"""
import json
import os
from typing import Optional
import requests
from dotenv import load_dotenv
from src.utils.logger import setup_logger

load_dotenv()
logger = setup_logger(__name__)


async def search_precedents(
    query: str,
    jurisdiction: str = "all",
    year_from: Optional[int] = None,
    year_to: Optional[int] = None,
    max_results: int = 5
) -> str:
    """
    Search for legal precedents using Firecrawl API to scrape IndianKanoon
    
    Args:
        query: Legal issue or query to search (e.g., "Section 420 IPC")
        jurisdiction: Court jurisdiction (supreme_court, high_court, all)
        year_from: Start year for filtering
        year_to: End year for filtering
        max_results: Maximum number of results (default: 5)
    
    Returns:
        JSON string with precedent results from IndianKanoon
    """
    logger.info(f"Searching precedents for: {query}")
    
    try:
        # Get Firecrawl API key from environment
        firecrawl_api_key = os.getenv("FIRECRAWL_API_KEY")
        if not firecrawl_api_key:
            return json.dumps({
                "error": "FIRECRAWL_API_KEY not found in .env file",
                "instructions": "Get your API key from https://firecrawl.dev and add it to .env"
            }, indent=2)
        
        # Build IndianKanoon search URL
        search_url = f"https://indiankanoon.org/search/?formInput={query.replace(' ', '+')}"
        
        # Add jurisdiction filter if specified
        if jurisdiction == "supreme_court":
            search_url += "+doctypes:+supremecourt"
        elif jurisdiction == "high_court":
            search_url += "+doctypes:+highcourt"
        
        logger.info(f"Scraping URL: {search_url}")
        
        # Use Firecrawl to scrape the search results
        firecrawl_url = "https://api.firecrawl.dev/v1/scrape"
        headers = {
            "Authorization": f"Bearer {firecrawl_api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "url": search_url,
            "formats": ["markdown", "html"],
            "onlyMainContent": True
        }
        
        response = requests.post(firecrawl_url, json=payload, headers=headers, timeout=30)
        
        if response.status_code != 200:
            return json.dumps({
                "error": f"Firecrawl API error: {response.status_code}",
                "message": response.text
            }, indent=2)
        
        data = response.json()
        content = data.get("data", {}).get("markdown", "")
        
        if not content:
            return json.dumps({
                "query": query,
                "jurisdiction": jurisdiction,
                "total_found": 0,
                "results": [],
                "message": "No results found or content could not be extracted"
            }, indent=2)
        
        # Parse the results (simplified - returns the scraped content)
        results = {
            "query": query,
            "jurisdiction": jurisdiction,
            "filters": {
                "year_from": year_from,
                "year_to": year_to
            },
            "source": "IndianKanoon via Firecrawl",
            "search_url": search_url,
            "content": content[:2000] + "..." if len(content) > 2000 else content,
            "full_content_length": len(content),
            "search_metadata": {
                "api_used": "Firecrawl",
                "source_website": "indiankanoon.org"
            }
        }
        
        logger.info(f"Successfully scraped {len(content)} characters")
        return json.dumps(results, indent=2)
    
    except requests.Timeout:
        logger.error("Firecrawl API timeout")
        return json.dumps({
            "error": "Request timeout",
            "message": "The search took too long. Try a more specific query."
        }, indent=2)
    
    except Exception as e:
        logger.error(f"Error in precedent search: {str(e)}", exc_info=True)
        return json.dumps({
            "error": str(e),
            "error_type": type(e).__name__
        }, indent=2)
