"""
Case Law Finder Tool
Finds specific case laws by citation, party names, or legal provisions using PostgreSQL vector search
"""
import os
import json
from typing import Optional
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

# Lazy imports — these are heavy dependencies that may not be installed
_db_connection = None
_embedding_model = None

_HAS_PSYCOPG2 = None
_HAS_SENTENCE_TRANSFORMERS = None


def _check_deps():
    """Check if heavy dependencies are available (cached)."""
    global _HAS_PSYCOPG2, _HAS_SENTENCE_TRANSFORMERS
    if _HAS_PSYCOPG2 is None:
        try:
            import psycopg2  # noqa: F401
            _HAS_PSYCOPG2 = True
        except ImportError:
            _HAS_PSYCOPG2 = False
    if _HAS_SENTENCE_TRANSFORMERS is None:
        try:
            from sentence_transformers import SentenceTransformer  # noqa: F401
            _HAS_SENTENCE_TRANSFORMERS = True
        except ImportError:
            _HAS_SENTENCE_TRANSFORMERS = False
    return _HAS_PSYCOPG2, _HAS_SENTENCE_TRANSFORMERS


def get_db_connection():
    """Get or initialize PostgreSQL connection"""
    global _db_connection
    import psycopg2

    if _db_connection is None or _db_connection.closed:
        postgres_url = os.getenv("POSTGRES_URL")

        if not postgres_url:
            raise ValueError("POSTGRES_URL must be set in .env file")

        _db_connection = psycopg2.connect(postgres_url)
        logger.info("PostgreSQL connection established")

    return _db_connection


def get_embedding_model():
    """Get or initialize embedding model"""
    global _embedding_model
    from sentence_transformers import SentenceTransformer

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
    Find specific case laws using PostgreSQL vector search

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

    # Check dependencies first
    has_pg, has_st = _check_deps()

    if not has_pg:
        return json.dumps({
            "error": "psycopg2 is not installed",
            "message": "Case law vector search requires PostgreSQL. Install with: pip install psycopg2-binary",
            "search_parameters": {"citation": citation, "party_name": party_name, "legal_provision": legal_provision},
        }, indent=2)

    if not has_st:
        return json.dumps({
            "error": "sentence-transformers is not installed",
            "message": "Case law vector search requires sentence-transformers. Install with: pip install sentence-transformers",
            "search_parameters": {"citation": citation, "party_name": party_name, "legal_provision": legal_provision},
        }, indent=2)

    postgres_url = os.getenv("POSTGRES_URL")
    if not postgres_url:
        return json.dumps({
            "error": "POSTGRES_URL not configured",
            "message": "Set POSTGRES_URL in your .env file to enable case law vector search.",
            "search_parameters": {"citation": citation, "party_name": party_name, "legal_provision": legal_provision},
        }, indent=2)

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
        conn = get_db_connection()
        model = get_embedding_model()

        # Generate embedding for the search query
        logger.info("Generating embedding for search query...")
        query_embedding = model.encode(search_query, normalize_embeddings=True)

        # Perform vector similarity search using the match_documents function
        logger.info("Performing vector search via PostgreSQL...")
        with conn.cursor() as cur:
            cur.execute(
                "SELECT * FROM match_documents(%s::vector, %s::float, %s::int)",
                (query_embedding.tolist(), 0.5, max_results)
            )
            columns = [desc[0] for desc in cur.description]
            documents = [dict(zip(columns, row)) for row in cur.fetchall()]

        # Process results
        formatted_cases = []
        for doc in documents:
            # Extract act name from metadata
            metadata = doc.get('metadata', {})
            if isinstance(metadata, str):
                metadata = json.loads(metadata)
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
            "search_method": "postgresql_vector_search",
            "embedding_model": "Supabase/gte-small"
        }

        logger.info(f"Found {len(formatted_cases)} matching acts")
        return json.dumps(result, indent=2)

    except Exception as e:
        logger.error(f"Error finding case laws: {str(e)}", exc_info=True)
        # Reset connection on error so it reconnects next time
        global _db_connection
        if _db_connection and not _db_connection.closed:
            try:
                _db_connection.close()
            except Exception:
                pass
        _db_connection = None
        return json.dumps({
            "error": str(e),
            "error_type": type(e).__name__
        }, indent=2)
