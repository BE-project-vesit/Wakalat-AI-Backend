# Vector Database Integration

This document describes the vector database integration for case law and precedent retrieval in Wakalat-AI Backend.

## Overview

The vector database service provides semantic search capabilities for legal case laws and precedents. It uses ChromaDB for efficient storage and retrieval of embeddings, enabling similarity-based searches that understand the meaning and context of legal queries.

## Features

- **Semantic Search**: Find similar cases based on meaning, not just keywords
- **Persistent Storage**: ChromaDB stores embeddings on disk for fast retrieval
- **Embedding Generation**: Converts legal text into vector representations
- **Metadata Filtering**: Filter results by court, year, jurisdiction, etc.
- **Fallback Mode**: Works offline with basic embeddings when ML models unavailable

## Architecture

```
┌─────────────┐
│  User Query │
└──────┬──────┘
       │
       ▼
┌──────────────────┐
│ Precedent Search │
│   or Case Finder │
└──────┬───────────┘
       │
       ▼
┌──────────────────┐
│  VectorDBService │
│  - generate_embedding()
│  - search_cases()
│  - add_case()
└──────┬───────────┘
       │
       ▼
┌──────────────────┐
│    ChromaDB      │
│  (Persistent)    │
└──────────────────┘
```

## Usage

### Initializing the Vector Database

```python
from src.services.vector_db import get_vector_db

# Get the singleton instance
vector_db = get_vector_db()

# Check collection stats
stats = vector_db.get_collection_stats()
print(f"Total documents: {stats['total_documents']}")
```

### Adding Case Laws

```python
# Prepare case data
case_data = {
    "case_name": "State v. Defendant",
    "citation": "AIR 2023 SC 1234",
    "court": "Supreme Court of India",
    "year": 2023,
    "summary": "This case deals with...",
    "headnotes": ["Key point 1", "Key point 2"],
    "sections_involved": ["Section 302 IPC"],
    "judges": ["Justice A", "Justice B"],
    "full_text_url": "https://example.com/case"
}

# Add to vector database
success = vector_db.add_case(
    case_id="AIR_2023_SC_1234",
    case_data=case_data
)
```

### Searching for Cases

```python
# Semantic search
results = vector_db.search_cases(
    query="breach of contract damages",
    n_results=10
)

for result in results:
    print(f"Case: {result['case_name']}")
    print(f"Relevance: {result['relevance_score']}")
    print(f"Citation: {result['citation']}")
```

### Filtering Results

```python
# Search with metadata filters
results = vector_db.search_cases(
    query="employment law",
    n_results=5,
    filters={"court": "Supreme Court of India"}
)
```

### Retrieving Specific Cases

```python
# Get case by ID
case = vector_db.get_case_by_id("AIR_2023_SC_1234")
if case:
    print(f"Found: {case['case_name']}")
```

## Loading Sample Data

A utility script is provided to load sample case laws for testing:

```bash
python scripts/load_sample_data.py
```

This loads 5 sample Indian Supreme Court cases covering various legal topics:
- Contract law (breach and damages)
- Criminal law (Section 302 IPC)
- Specific performance
- Motor accident claims
- Environmental law

## Embedding Models

### Production Mode (with Transformers)

Set environment variable to enable sentence-transformers:

```bash
export USE_TRANSFORMERS=true
```

Uses `all-MiniLM-L6-v2` model (384-dimensional embeddings):
- High quality semantic representations
- Requires internet for initial download
- Better similarity matching

### Fallback Mode (Offline/Testing)

Default mode when transformers are unavailable:
- Uses deterministic hash-based embeddings
- Works completely offline
- Good for development and testing
- Adequate for basic similarity matching

## Configuration

Vector database settings in `src/config.py`:

```python
# Vector Database
chroma_persist_directory: Path = Path("./data/chroma")
chroma_collection_name: str = "legal_cases"
```

Environment variables:
- `USE_TRANSFORMERS`: Set to "true" to enable sentence-transformers
- `CHROMA_PERSIST_DIRECTORY`: Override default storage location
- `CHROMA_COLLECTION_NAME`: Override default collection name

## Integration with Tools

### Precedent Search

The `search_precedents` tool uses vector database for semantic search:

```python
from src.tools.precedent_search import search_precedents

result = await search_precedents(
    query="breach of contract damages",
    jurisdiction="supreme_court",
    year_from=2015,
    year_to=2023,
    max_results=10
)
```

Features:
- Semantic similarity matching
- Jurisdiction filtering (supreme_court, high_court, all)
- Year range filtering
- Relevance scoring

### Case Law Finder

The `find_case_laws` tool searches by citation, party name, or provision:

```python
from src.tools.case_law_finder import find_case_laws

# Search by citation
result = await find_case_laws(
    citation="AIR 2020 SC 1234",
    include_summary=True
)

# Search by party name
result = await find_case_laws(
    party_name="State of Maharashtra",
    include_summary=True
)

# Search by legal provision
result = await find_case_laws(
    legal_provision="Section 302 IPC",
    include_summary=True
)
```

## Performance Optimization

### Indexing

ChromaDB uses HNSW (Hierarchical Navigable Small World) indexing for fast approximate nearest neighbor search:
- Sublinear search time complexity
- Efficient even with millions of documents
- Configurable accuracy/speed tradeoff

### Caching

- Embeddings are cached in the database
- Repeated queries for same text don't regenerate embeddings
- Collection persists to disk automatically

### Best Practices

1. **Batch Operations**: Add multiple cases at once when possible
2. **Meaningful IDs**: Use citation-based IDs for easy retrieval
3. **Rich Metadata**: Include all relevant fields for better filtering
4. **Comprehensive Text**: Combine case name, summary, and headnotes for better embeddings

## Testing

Run vector database tests:

```bash
# All vector DB tests
python -m pytest tests/test_vector_db.py -v

# Specific test
python -m pytest tests/test_vector_db.py::test_search_cases -v
```

Test coverage:
- Initialization
- Embedding generation
- Adding cases
- Searching cases
- Filtering
- Case retrieval
- Case deletion
- Collection statistics

## Troubleshooting

### Issue: No results from search

**Solution**: 
- Check if cases are loaded: `vector_db.get_collection_stats()`
- Try broader search terms
- Reduce filters

### Issue: Slow initialization

**Solution**:
- Use fallback mode (default) for development
- Download transformers model once in production
- Model cached after first download

### Issue: ChromaDB errors

**Solution**:
- Ensure `data/chroma` directory exists
- Check write permissions
- Delete and recreate: `vector_db.reset_collection()` (CAUTION: deletes all data)

### Issue: Metadata errors

**Solution**:
- Ensure metadata values are simple types (str, int, float, bool)
- Lists automatically converted to comma-separated strings
- Dicts converted to JSON strings

## Advanced Usage

### Custom Embedding Dimension

Modify the fallback embedding dimension:

```python
embedding = vector_db._generate_fallback_embedding(text, dimension=512)
```

### Resetting Collection

```python
# WARNING: Deletes all data
success = vector_db.reset_collection()
```

### Direct ChromaDB Access

```python
# Access underlying ChromaDB collection
collection = vector_db.collection

# Get all IDs
all_ids = collection.get()['ids']
```

## Future Enhancements

- [ ] Support for multiple languages (Hindi, regional languages)
- [ ] Integration with Indian Kanoon API
- [ ] Automatic case law scraping and indexing
- [ ] Fine-tuned legal domain embeddings
- [ ] Query expansion and reformulation
- [ ] Case clustering and categorization
- [ ] Temporal relevance scoring
- [ ] Citation network analysis

## References

- [ChromaDB Documentation](https://docs.trychroma.com/)
- [Sentence Transformers](https://www.sbert.net/)
- [Vector Search Explained](https://www.pinecone.io/learn/vector-search/)
- [Indian Kanoon](https://indiankanoon.org/)

## Support

For issues or questions:
1. Check existing tests in `tests/test_vector_db.py`
2. Review logs in `logs/wakalat-ai.log`
3. Open an issue on GitHub
