"""
Case Law Finder Tool
Finds specific case laws by citation, party names, or legal provisions using Supabase vector search
"""
import os
import json
from typing import Optional
from dotenv import load_dotenv
from supabase import create_client, Client
from sentence_transformers import SentenceTransformer
from src.utils.logger import setup_logger

load_dotenv()
logger = setup_logger(__name__)

# Initialize Supabase client and embedding model (lazy loading)
_supabase_client: Optional[Client] = None
_embedding_model: Optional[SentenceTransformer] = None


def get_supabase_client() -> Client:
    """Get or initialize Supabase client"""
    global _supabase_client
    if _supabase_client is None:
        supabase_url = os.getenv("SUPABASE_URL") or os.getenv("PUBLIC_SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_KEY") or os.getenv("PUBLIC_SUPABASE_ANON_KEY")
        
        if not supabase_url or not supabase_key:
            raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in .env file")
        
        _supabase_client = create_client(supabase_url, supabase_key)
        logger.info("Supabase client initialized")
    
    return _supabase_client


def get_embedding_model() -> SentenceTransformer:
    """Get or initialize embedding model"""
    global _embedding_model
    if _embedding_model is None:
        logger.info("Loading embedding model (Supabase/gte-small)...")
        _embedding_model = SentenceTransformer("Supabase/gte-small")
        logger.info("Embedding model loaded successfully")
    
    return _embedding_model


async def find_case_laws(
    citation: Optional[str] = None,
    party_name: Optional[str] = None,
    legal_provision: Optional[str] = None,
    include_summary: bool = True,
    max_results: int = 5
) -> str:
    """
    Find specific case laws using Supabase vector search
    
    Args:
        citation: Case citation (e.g., 'AIR 2020 SC 1234')
        party_name: Name of party in the case
        legal_provision: Legal provision or section (e.g., 'Section 420 IPC')
        include_summary: Whether to include content preview
        max_results: Maximum number of results to return (default: 5)
    
    Returns:
        JSON string with matching Indian legal acts and their relevance scores
    """
    logger.info(f"Finding case laws - citation: {citation}, party: {party_name}, provision: {legal_provision}")
    
    try:
        # Build search query from provided parameters
        search_query_parts = []
        if citation:
            search_query_parts.append(citation)
        if party_name:
            search_query_parts.append(f"case involving {party_name}")
        if legal_provision:
            search_query_parts.append(legal_provision)
        
        if not search_query_parts:
            return json.dumps({
                "error": "At least one search parameter (citation, party_name, or legal_provision) must be provided"
            }, indent=2)
        
        search_query = " ".join(search_query_parts)
        logger.info(f"Search query: {search_query}")
        
        # Initialize clients
        supabase = get_supabase_client()
        model = get_embedding_model()
        
        # Generate embedding for the search query
        logger.info("Generating embedding for search query...")
        query_embedding = model.encode(search_query, normalize_embeddings=True)
        
        # Perform vector similarity search using Supabase RPC function
        logger.info("Performing vector search in Supabase...")
        response = supabase.rpc(
            'match_documents',
            {
                'query_embedding': query_embedding.tolist(),
                'match_threshold': 0.5,  # Minimum similarity threshold
                'match_count': max_results
            }
        ).execute()
        
        # Process results
        documents = response.data if response.data else []
        
        formatted_cases = []
        for doc in documents:
            # Extract act name from metadata
            metadata = doc.get('metadata', {})
            act_name = metadata.get('file', 'Unknown Act')
            
            # Remove .pdf extension if present
            if act_name.endswith('.pdf'):
                act_name = act_name[:-4]
            
            formatted_case = {
                "act_name": act_name,
                "relevance_score": round(doc.get('similarity', 0.0), 4),
                "content_preview": doc.get('content', '')[:500] + "..." if include_summary else None,
                "metadata": metadata,
                "document_id": doc.get('id')
            }
            formatted_cases.append(formatted_case)
        
        result = {
            "search_parameters": {
                "citation": citation,
                "party_name": party_name,
                "legal_provision": legal_provision,
                "search_query": search_query
            },
            "acts_found": formatted_cases,
            "total_found": len(formatted_cases),
            "search_method": "supabase_vector_search",
            "embedding_model": "Supabase/gte-small"
        }
        
        logger.info(f"Found {len(formatted_cases)} matching acts")
        return json.dumps(result, indent=2)
    
    except Exception as e:
        logger.error(f"Error finding case laws: {str(e)}", exc_info=True)
        return json.dumps({
            "error": str(e),
            "error_type": type(e).__name__
        }, indent=2)
