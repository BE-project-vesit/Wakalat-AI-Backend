# Supabase Vector Search Setup Guide

## Overview

The `case_law_finder` tool has been updated to use Supabase vector search to find relevant Indian legal acts based on your query.

## Setup Steps

### 1. Update Your `.env` File

Make sure your `.env` file has the Supabase credentials:

```bash
# Supabase Configuration
SUPABASE_URL=https://mfaebogwihppaoyyclzs.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im1mYWVib2d3aWhwcGFveXljbHpzIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTYwNDA0NjYsImV4cCI6MjA3MTYxNjQ2Nn0.KpTdxA0hc1owxIXKhsSAzLzvn1QUZhiMowuDz8ZOpFc

# Or use these alternative names (tool supports both)
PUBLIC_SUPABASE_URL=https://mfaebogwihppaoyyclzs.supabase.co
PUBLIC_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im1mYWVib2d3aWhwcGFveXljbHpzIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTYwNDA0NjYsImV4cCI6MjA3MTYxNjQ2Nn0.KpTdxA0hc1owxIXKhsSAzLzvn1QUZhiMowuDz8ZOpFc
```

### 2. Create the Vector Search Function in Supabase

1. Open your Supabase Dashboard
2. Go to **SQL Editor**
3. Run the SQL in `supabase_vector_search_function.sql`

This creates the `match_documents()` function that performs vector similarity search.

### 3. Verify Your Table Schema

Your `documents` table should match:

```sql
CREATE TABLE public.documents (
  id bigint PRIMARY KEY,
  content text,
  embedding vector(384),  -- Supabase/gte-small embeddings
  metadata jsonb
);
```

### 4. Test the Tool

The tool now accepts these parameters:

- **`legal_provision`**: The main search query (e.g., "Section 420 IPC", "contract law", "property disputes")
- **`citation`**: Optional case citation
- **`party_name`**: Optional party name
- **`include_summary`**: Whether to include content preview (default: true)
- **`max_results`**: Number of results to return (default: 5)

## How It Works

1. **Query Generation**: Combines your search parameters into a single query string
2. **Embedding**: Generates a 384-dimensional embedding using `Supabase/gte-small` model
3. **Vector Search**: Uses Supabase's `match_documents()` RPC function to find similar documents
4. **Results**: Returns matching acts with:
   - Act name (extracted from filename in metadata)
   - Relevance score (0-1, higher = more relevant)
   - Content preview (first 500 characters)
   - Full metadata

## Example Usage in Claude

When connected to Claude Desktop, you can ask:

- _"Find case laws related to Section 420 IPC"_
- _"Search for laws about breach of contract"_
- _"What acts cover property disputes?"_
- _"Find legal provisions for cyber crimes"_

Claude will automatically use the `find_case_laws` tool and return the most relevant Indian legal acts from your Supabase database.

## Response Format

```json
{
  "search_parameters": {
    "citation": null,
    "party_name": null,
    "legal_provision": "Section 420 IPC",
    "search_query": "Section 420 IPC"
  },
  "acts_found": [
    {
      "act_name": "Indian Penal Code 1860",
      "relevance_score": 0.8542,
      "content_preview": "Section 420: Cheating and dishonestly inducing delivery of property...",
      "metadata": {
        "file": "Indian Penal Code 1860.pdf",
        "num_pages": 345
      },
      "document_id": 123
    }
  ],
  "total_found": 1,
  "search_method": "supabase_vector_search",
  "embedding_model": "Supabase/gte-small"
}
```

## Troubleshooting

### Error: "SUPABASE_URL and SUPABASE_KEY must be set"

- Make sure your `.env` file exists and has the credentials
- Run `uv sync` to reload environment

### Error: "function match_documents() does not exist"

- Run the SQL in `supabase_vector_search_function.sql` in Supabase SQL Editor

### Slow Performance

- Make sure you created the vector index (included in the SQL file)
- Check your Supabase plan limits

### No Results Found

- Try lowering the `match_threshold` in the code (currently 0.5)
- Check that your embeddings are normalized (they should be)
- Verify embeddings were created with the same model (`Supabase/gte-small`)

## Dependencies Added

- ✅ `supabase>=2.0.0` - Supabase Python client
- ✅ `sentence-transformers>=2.2.0` - For generating embeddings (already installed)

## Notes

- The tool uses **lazy loading** for the Supabase client and embedding model (only loads when first used)
- Embeddings are generated with **normalization** (same as your ingestion script)
- The model `Supabase/gte-small` produces **384-dimensional** embeddings
- Results are sorted by **cosine similarity** (higher = more relevant)
