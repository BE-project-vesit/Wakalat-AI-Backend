"""
Precedent Search Tool
Searches for legal precedents from Indian courts
"""
import json
import time
from typing import Optional
from src.utils.logger import setup_logger
from src.services.vector_db import get_vector_db

logger = setup_logger(__name__)


async def search_precedents(
    query: str,
    jurisdiction: str = "all",
    year_from: Optional[int] = None,
    year_to: Optional[int] = None,
    max_results: int = 10
) -> str:
    """
    Search for legal precedents relevant to a query
    
    Args:
        query: Legal issue or query to search
        jurisdiction: Court jurisdiction (supreme_court, high_court, all)
        year_from: Start year for filtering
        year_to: End year for filtering
        max_results: Maximum number of results
    
    Returns:
        JSON string with precedent results
    """
    logger.info(f"Searching precedents for query: {query}")
    
    try:
        start_time = time.time()
        
        # Get vector database instance
        vector_db = get_vector_db()
        
        # Build filters for metadata search
        filters = {}
        if jurisdiction != "all":
            # Map jurisdiction to court names
            jurisdiction_map = {
                "supreme_court": "Supreme Court of India",
                "high_court": "High Court"
            }
            if jurisdiction in jurisdiction_map:
                filters["court"] = jurisdiction_map[jurisdiction]
        
        # Search using vector database for semantic similarity
        search_results = vector_db.search_cases(
            query=query,
            n_results=max_results,
            filters=filters if filters else None
        )
        
        # Filter by year if specified
        if year_from or year_to:
            filtered_results = []
            for result in search_results:
                case_year = result.get('year', 0)
                if year_from and case_year < year_from:
                    continue
                if year_to and case_year > year_to:
                    continue
                filtered_results.append(result)
            search_results = filtered_results
        
        # Format results for response
        formatted_results = []
        for result in search_results:
            formatted_case = {
                "case_name": result.get('case_name', 'N/A'),
                "citation": result.get('citation', 'N/A'),
                "court": result.get('court', 'N/A'),
                "year": result.get('year', 0),
                "summary": result.get('summary', 'N/A'),
                "relevance_score": result.get('relevance_score', 0.0),
                "key_points": result.get('headnotes', []),
                "url": result.get('full_text_url', '')
            }
            formatted_results.append(formatted_case)
        
        search_time_ms = (time.time() - start_time) * 1000
        
        results = {
            "query": query,
            "jurisdiction": jurisdiction,
            "filters": {
                "year_from": year_from,
                "year_to": year_to
            },
            "total_found": len(formatted_results),
            "results": formatted_results,
            "search_metadata": {
                "search_time_ms": round(search_time_ms, 2),
                "semantic_search_used": True,
                "vector_db_enabled": True
            }
        }
        
        return json.dumps(results, indent=2)
    
    except Exception as e:
        logger.error(f"Error in precedent search: {str(e)}", exc_info=True)
        return json.dumps({"error": str(e)}, indent=2)
