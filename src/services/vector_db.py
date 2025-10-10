"""
Vector Database Service for Case Law and Precedent Retrieval
Uses ChromaDB for efficient semantic search of legal documents
"""
import time
from typing import List, Dict, Optional, Any
import chromadb
from chromadb.config import Settings as ChromaSettings

# Make sentence-transformers import optional
try:
    from sentence_transformers import SentenceTransformer
    HAS_TRANSFORMERS = True
except ImportError:
    SentenceTransformer = None
    HAS_TRANSFORMERS = False

from src.config import settings
from src.utils.logger import setup_logger
from src.models.case import CaseLaw

logger = setup_logger(__name__)


class VectorDBService:
    """
    Service class for managing vector database operations
    Handles embedding generation and semantic search for case laws
    """
    
    def __init__(self):
        """Initialize the vector database service"""
        self.client = None
        self.collection = None
        self.embedding_model = None
        self._initialized = False
    
    def initialize(self):
        """Initialize ChromaDB client and embedding model"""
        if self._initialized:
            return
        
        try:
            logger.info("Initializing Vector Database Service...")
            
            # Initialize ChromaDB client
            self.client = chromadb.PersistentClient(
                path=str(settings.chroma_persist_directory),
                settings=ChromaSettings(
                    anonymized_telemetry=False,
                    allow_reset=True
                )
            )
            
            # Get or create collection
            self.collection = self.client.get_or_create_collection(
                name=settings.chroma_collection_name,
                metadata={"description": "Legal cases and precedents for Indian law"}
            )
            
            # Initialize embedding model
            # Try to use sentence-transformers if available and model exists locally
            logger.info("Checking for sentence-transformers model...")
            try:
                # Only try to load if running in production or explicitly configured
                import os
                use_transformers = os.environ.get('USE_TRANSFORMERS', 'false').lower() == 'true'
                
                if use_transformers and HAS_TRANSFORMERS and SentenceTransformer is not None:
                    self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
                    logger.info("Sentence-transformers model loaded successfully")
                else:
                    logger.info("Using fallback embedding method (transformers disabled or unavailable)")
                    self.embedding_model = None
            except Exception as model_error:
                logger.warning(f"Could not load sentence-transformers model: {model_error}")
                logger.warning("Using fallback embedding method (basic text hashing)")
                self.embedding_model = None
            
            self._initialized = True
            logger.info(f"Vector DB initialized. Collection: {settings.chroma_collection_name}, "
                       f"Documents: {self.collection.count()}")
            
        except Exception as e:
            logger.error(f"Failed to initialize Vector DB: {str(e)}", exc_info=True)
            raise
    
    def generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding vector for given text
        
        Args:
            text: Text to embed
            
        Returns:
            List of floats representing the embedding vector
        """
        if not self._initialized:
            self.initialize()
        
        try:
            if self.embedding_model is not None:
                # Use sentence-transformers model if available
                embedding = self.embedding_model.encode(text, convert_to_tensor=False)
                return embedding.tolist()
            else:
                # Fallback: simple hash-based embedding for testing/offline mode
                logger.debug("Using fallback embedding method")
                return self._generate_fallback_embedding(text)
        except Exception as e:
            logger.error(f"Error generating embedding: {str(e)}", exc_info=True)
            # Try fallback if primary method fails
            return self._generate_fallback_embedding(text)
    
    def _generate_fallback_embedding(self, text: str, dimension: int = 384) -> List[float]:
        """
        Generate a simple fallback embedding when sentence-transformers is unavailable
        Uses basic text features and hashing
        
        Args:
            text: Text to embed
            dimension: Dimension of embedding vector
            
        Returns:
            List of floats representing a basic embedding
        """
        import hashlib
        import math
        
        # Normalize text
        text = text.lower().strip()
        
        # Create a deterministic embedding based on text content
        embedding = [0.0] * dimension
        
        # Use multiple hash functions to distribute values
        for i in range(dimension):
            seed = f"{text}_{i}"
            hash_val = int(hashlib.md5(seed.encode()).hexdigest(), 16)
            # Convert to float in range [-1, 1]
            embedding[i] = (hash_val % 10000) / 5000.0 - 1.0
        
        # Normalize the vector
        magnitude = math.sqrt(sum(x * x for x in embedding))
        if magnitude > 0:
            embedding = [x / magnitude for x in embedding]
        
        return embedding
    
    def add_case(
        self,
        case_id: str,
        case_data: Dict[str, Any],
        generate_embedding_from: Optional[str] = None
    ) -> bool:
        """
        Add a case to the vector database
        
        Args:
            case_id: Unique identifier for the case
            case_data: Dictionary containing case information
            generate_embedding_from: Text to generate embedding from (defaults to summary)
            
        Returns:
            True if successful
        """
        if not self._initialized:
            self.initialize()
        
        try:
            # Prepare text for embedding
            if generate_embedding_from:
                text_to_embed = generate_embedding_from
            else:
                # Create comprehensive text from case data
                text_parts = []
                if case_data.get('case_name'):
                    text_parts.append(case_data['case_name'])
                if case_data.get('summary'):
                    text_parts.append(case_data['summary'])
                if case_data.get('headnotes'):
                    text_parts.extend(case_data['headnotes'])
                text_to_embed = " ".join(text_parts)
            
            # Generate embedding
            embedding = self.generate_embedding(text_to_embed)
            
            # ChromaDB metadata must be simple types (str, int, float, bool)
            # Convert lists to JSON strings
            sanitized_metadata = {}
            for key, value in case_data.items():
                if isinstance(value, list):
                    # Convert list to comma-separated string
                    sanitized_metadata[key] = ", ".join(str(v) for v in value)
                elif isinstance(value, dict):
                    # Convert dict to JSON string
                    import json
                    sanitized_metadata[key] = json.dumps(value)
                elif value is None:
                    sanitized_metadata[key] = ""
                else:
                    sanitized_metadata[key] = value
            
            # Add to collection
            self.collection.add(
                ids=[case_id],
                embeddings=[embedding],
                documents=[text_to_embed],
                metadatas=[sanitized_metadata]
            )
            
            logger.info(f"Added case {case_id} to vector database")
            return True
            
        except Exception as e:
            logger.error(f"Error adding case to vector DB: {str(e)}", exc_info=True)
            return False
    
    def search_cases(
        self,
        query: str,
        n_results: int = 10,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for cases using semantic similarity
        
        Args:
            query: Search query
            n_results: Maximum number of results to return
            filters: Optional metadata filters (e.g., {'jurisdiction': 'supreme_court'})
            
        Returns:
            List of matching cases with relevance scores
        """
        if not self._initialized:
            self.initialize()
        
        try:
            start_time = time.time()
            
            # Generate query embedding
            query_embedding = self.generate_embedding(query)
            
            # Build where clause for filtering
            where_clause = None
            if filters:
                where_clause = filters
            
            # Search in collection
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results,
                where=where_clause,
                include=["documents", "metadatas", "distances"]
            )
            
            # Format results
            formatted_results = []
            if results and results['ids'] and len(results['ids'][0]) > 0:
                for i in range(len(results['ids'][0])):
                    # ChromaDB returns distances (lower is better), convert to similarity score
                    distance = results['distances'][0][i]
                    relevance_score = 1 / (1 + distance)  # Convert distance to similarity
                    
                    result_data = {
                        'case_id': results['ids'][0][i],
                        'relevance_score': round(relevance_score, 4),
                        'distance': round(distance, 4),
                        **results['metadatas'][0][i]
                    }
                    formatted_results.append(result_data)
            
            search_time = (time.time() - start_time) * 1000
            logger.info(f"Vector search completed in {search_time:.2f}ms, found {len(formatted_results)} results")
            
            return formatted_results
            
        except Exception as e:
            logger.error(f"Error searching vector DB: {str(e)}", exc_info=True)
            return []
    
    def get_case_by_id(self, case_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a case by its ID
        
        Args:
            case_id: Unique identifier for the case
            
        Returns:
            Case data if found, None otherwise
        """
        if not self._initialized:
            self.initialize()
        
        try:
            result = self.collection.get(
                ids=[case_id],
                include=["metadatas", "documents"]
            )
            
            if result and result['ids']:
                return result['metadatas'][0]
            return None
            
        except Exception as e:
            logger.error(f"Error retrieving case from vector DB: {str(e)}", exc_info=True)
            return None
    
    def delete_case(self, case_id: str) -> bool:
        """
        Delete a case from the vector database
        
        Args:
            case_id: Unique identifier for the case
            
        Returns:
            True if successful
        """
        if not self._initialized:
            self.initialize()
        
        try:
            self.collection.delete(ids=[case_id])
            logger.info(f"Deleted case {case_id} from vector database")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting case from vector DB: {str(e)}", exc_info=True)
            return False
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the vector database collection
        
        Returns:
            Dictionary with collection statistics
        """
        if not self._initialized:
            self.initialize()
        
        try:
            count = self.collection.count()
            return {
                "collection_name": settings.chroma_collection_name,
                "total_documents": count,
                "persist_directory": str(settings.chroma_persist_directory)
            }
        except Exception as e:
            logger.error(f"Error getting collection stats: {str(e)}", exc_info=True)
            return {}
    
    def reset_collection(self) -> bool:
        """
        Reset (clear) the collection - USE WITH CAUTION
        
        Returns:
            True if successful
        """
        if not self._initialized:
            self.initialize()
        
        try:
            self.client.delete_collection(name=settings.chroma_collection_name)
            self.collection = self.client.create_collection(
                name=settings.chroma_collection_name,
                metadata={"description": "Legal cases and precedents for Indian law"}
            )
            logger.warning("Vector database collection has been reset!")
            return True
            
        except Exception as e:
            logger.error(f"Error resetting collection: {str(e)}", exc_info=True)
            return False


# Global instance
_vector_db_instance = None


def get_vector_db() -> VectorDBService:
    """
    Get or create the global VectorDBService instance
    
    Returns:
        VectorDBService instance
    """
    global _vector_db_instance
    if _vector_db_instance is None:
        _vector_db_instance = VectorDBService()
        _vector_db_instance.initialize()
    return _vector_db_instance
