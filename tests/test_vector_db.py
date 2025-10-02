"""
Tests for Vector Database Service
"""
import pytest
from src.services.vector_db import VectorDBService


@pytest.fixture
def vector_db():
    """Create a fresh vector database instance for testing"""
    service = VectorDBService()
    service.initialize()
    # Reset collection for clean tests
    service.reset_collection()
    return service


def test_vector_db_initialization(vector_db):
    """Test that vector database initializes correctly"""
    assert vector_db._initialized is True
    assert vector_db.client is not None
    assert vector_db.collection is not None
    # embedding_model can be None in fallback mode (offline/testing)


def test_generate_embedding(vector_db):
    """Test embedding generation"""
    text = "This is a test case about contract law"
    embedding = vector_db.generate_embedding(text)
    
    assert embedding is not None
    assert isinstance(embedding, list)
    assert len(embedding) > 0
    assert all(isinstance(x, float) for x in embedding)


def test_add_case(vector_db):
    """Test adding a case to vector database"""
    case_data = {
        "case_name": "Test Case v. Example",
        "citation": "AIR 2023 TEST 001",
        "court": "Test Court",
        "year": 2023,
        "summary": "This is a test case for breach of contract"
    }
    
    result = vector_db.add_case("test_case_001", case_data)
    assert result is True
    
    # Verify case was added
    stats = vector_db.get_collection_stats()
    assert stats["total_documents"] == 1


def test_search_cases(vector_db):
    """Test semantic search for cases"""
    # Add sample cases
    cases = [
        {
            "case_id": "case_001",
            "data": {
                "case_name": "Contract Breach Case",
                "citation": "AIR 2023 SC 001",
                "court": "Supreme Court of India",
                "year": 2023,
                "summary": "Case about breach of contract and damages"
            }
        },
        {
            "case_id": "case_002",
            "data": {
                "case_name": "Criminal Murder Case",
                "citation": "AIR 2023 SC 002",
                "court": "Supreme Court of India",
                "year": 2023,
                "summary": "Case about murder under Section 302 IPC"
            }
        }
    ]
    
    for case in cases:
        vector_db.add_case(case["case_id"], case["data"])
    
    # Search for contract-related cases
    results = vector_db.search_cases("breach of contract", n_results=5)
    
    assert len(results) > 0
    # Check that we got results with the expected fields
    assert "case_name" in results[0]
    assert "relevance_score" in results[0]
    # Check that at least one contract-related case is in results
    case_names = [r["case_name"] for r in results]
    assert "Contract Breach Case" in case_names


def test_get_case_by_id(vector_db):
    """Test retrieving a case by ID"""
    case_data = {
        "case_name": "Test Case",
        "citation": "AIR 2023 TEST 001",
        "summary": "Test summary"
    }
    
    vector_db.add_case("test_case_id", case_data)
    
    retrieved = vector_db.get_case_by_id("test_case_id")
    assert retrieved is not None
    assert retrieved["case_name"] == "Test Case"
    assert retrieved["citation"] == "AIR 2023 TEST 001"


def test_delete_case(vector_db):
    """Test deleting a case"""
    case_data = {
        "case_name": "To Be Deleted",
        "citation": "AIR 2023 DEL 001",
        "summary": "This case will be deleted"
    }
    
    vector_db.add_case("delete_me", case_data)
    assert vector_db.get_collection_stats()["total_documents"] == 1
    
    result = vector_db.delete_case("delete_me")
    assert result is True
    assert vector_db.get_collection_stats()["total_documents"] == 0


def test_search_with_filters(vector_db):
    """Test search with metadata filters"""
    # Add cases from different courts
    vector_db.add_case("sc_case", {
        "case_name": "Supreme Court Case",
        "court": "Supreme Court of India",
        "summary": "Test case about contracts"
    })
    
    vector_db.add_case("hc_case", {
        "case_name": "High Court Case",
        "court": "High Court",
        "summary": "Test case about contracts"
    })
    
    # Search with court filter
    results = vector_db.search_cases(
        query="contracts",
        n_results=5,
        filters={"court": "Supreme Court of India"}
    )
    
    assert len(results) == 1
    assert results[0]["court"] == "Supreme Court of India"


def test_get_collection_stats(vector_db):
    """Test getting collection statistics"""
    stats = vector_db.get_collection_stats()
    
    assert "collection_name" in stats
    assert "total_documents" in stats
    assert "persist_directory" in stats
    assert stats["total_documents"] == 0
