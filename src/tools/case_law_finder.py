"""
Case Law Finder Tool
Finds specific case laws by citation, party names, or legal provisions
"""
import json
from typing import Optional
from src.utils.logger import setup_logger
from src.services.vector_db import get_vector_db

logger = setup_logger(__name__)


async def find_case_laws(
    citation: Optional[str] = None,
    party_name: Optional[str] = None,
    legal_provision: Optional[str] = None,
    include_summary: bool = True
) -> str:
    """
    Find specific case laws
    
    Args:
        citation: Case citation (e.g., 'AIR 2020 SC 1234')
        party_name: Name of party in the case
        legal_provision: Legal provision or section
        include_summary: Whether to include AI-generated summary
    
    Returns:
        JSON string with case law details
    """
    logger.info(f"Finding case laws - citation: {citation}, party: {party_name}, provision: {legal_provision}")
    
    try:
        # Get vector database instance
        vector_db = get_vector_db()
        
        cases_found = []
        
        # If citation is provided, try exact match first
        if citation:
            # Search by citation in metadata
            search_results = vector_db.search_cases(
                query=citation,
                n_results=5
            )
            # Filter to those with matching citation
            for case in search_results:
                if case.get('citation', '').lower() == citation.lower():
                    cases_found.append(case)
        
        # If party name is provided, search semantically
        if party_name and not cases_found:
            search_results = vector_db.search_cases(
                query=f"case involving party {party_name}",
                n_results=10
            )
            cases_found = search_results
        
        # If legal provision is provided, search semantically
        if legal_provision and not cases_found:
            search_results = vector_db.search_cases(
                query=f"legal provision {legal_provision}",
                n_results=10
            )
            cases_found = search_results
        
        # Format results
        formatted_cases = []
        for case in cases_found:
            formatted_case = {
                "case_name": case.get('case_name', 'N/A'),
                "citation": case.get('citation', 'N/A'),
                "court": case.get('court', 'N/A'),
                "bench": case.get('bench', 'N/A'),
                "date": case.get('date', 'N/A'),
                "judges": case.get('judges', []),
                "summary": case.get('summary', 'N/A') if include_summary else None,
                "headnotes": case.get('headnotes', []),
                "sections_involved": case.get('sections_involved', []),
                "precedents_cited": case.get('precedents_cited', []),
                "full_text_url": case.get('full_text_url', ''),
                "pdf_url": case.get('pdf_url', ''),
                "relevance_score": case.get('relevance_score', 0.0)
            }
            formatted_cases.append(formatted_case)
        
        result = {
            "search_parameters": {
                "citation": citation,
                "party_name": party_name,
                "legal_provision": legal_provision
            },
            "cases_found": formatted_cases,
            "total_found": len(formatted_cases),
            "vector_db_enabled": True
        }
        
        return json.dumps(result, indent=2)
    
    except Exception as e:
        logger.error(f"Error finding case laws: {str(e)}", exc_info=True)
        return json.dumps({"error": str(e)}, indent=2)
