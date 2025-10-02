# Wakalat-AI Backend Architecture

## System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        MCP Client Layer                         │
│  (Claude Desktop, Custom Clients, Frontend Applications)        │
└────────────────────────┬────────────────────────────────────────┘
                         │ MCP Protocol (stdio/HTTP)
                         │
┌────────────────────────▼────────────────────────────────────────┐
│                    Wakalat-AI MCP Server                        │
│                        (src/server.py)                          │
├─────────────────────────────────────────────────────────────────┤
│  ┌───────────────────────────────────────────────────────────┐ │
│  │              Tool Registry & Router                       │ │
│  │  • list_tools()  • call_tool()  • list_resources()       │ │
│  └───────────────────────────────────────────────────────────┘ │
└─────────────────────────┬───────────────────────────────────────┘
                          │
      ┌───────────────────┼───────────────────┐
      │                   │                   │
      ▼                   ▼                   ▼
┌──────────┐      ┌──────────────┐    ┌─────────────┐
│ Tools    │      │   Utils      │    │   Models    │
│  Layer   │      │   Layer      │    │   Layer     │
└──────────┘      └──────────────┘    └─────────────┘
      │                   │                   │
      └───────────────────┴───────────────────┘
                          │
      ┌───────────────────┼───────────────────┐
      │                   │                   │
      ▼                   ▼                   ▼
┌──────────┐      ┌──────────────┐    ┌─────────────┐
│ LLM APIs │      │  Vector DB   │    │  Document   │
│ (OpenAI/ │      │  (ChromaDB)  │    │  Storage    │
│Anthropic)│      │              │    │             │
└──────────┘      └──────────────┘    └─────────────┘
      │                   │                   │
      └───────────────────┴───────────────────┘
                          │
                          ▼
              ┌───────────────────────┐
              │ External Legal APIs   │
              │ • Indian Kanoon       │
              │ • Supreme Court API   │
              │ • High Court APIs     │
              └───────────────────────┘
```

## Component Architecture

### 1. MCP Server Core (`src/server.py`)

The main server implements the Model Context Protocol specification:

- **Protocol Handlers**:
  - `list_tools()`: Exposes available legal assistance tools
  - `call_tool()`: Routes tool requests to appropriate handlers
  - `list_resources()`: Provides legal templates and references
  - `list_prompts()`: Offers prompt templates for common tasks

- **Transport**: Uses stdio transport for client communication

### 2. Tools Layer (`src/tools/`)

Six specialized tools for legal assistance:

#### a) Precedent Search (`precedent_search.py`)
```
Input: Legal query, filters (jurisdiction, year)
  ↓
Semantic search in vector DB
  ↓
Retrieve relevant precedents
  ↓
Output: Ranked list of cases with relevance scores
```

#### b) Case Law Finder (`case_law_finder.py`)
```
Input: Citation/Party name/Legal provision
  ↓
Search legal databases (Indian Kanoon, Court APIs)
  ↓
Fetch full judgment text
  ↓
Generate AI summary (LLM)
  ↓
Output: Case details with summary and key points
```

#### c) Document Analyzer (`document_analyzer.py`)
```
Input: Document file (PDF/DOCX)
  ↓
Parse document (PyPDF2/python-docx)
  ↓
Extract text and structure
  ↓
Analyze with LLM (issues, compliance, suggestions)
  ↓
Output: Comprehensive analysis report
```

#### d) Legal Research (`legal_research.py`)
```
Input: Research query
  ↓
RAG Pipeline:
  1. Retrieve relevant documents from vector DB
  2. Search statutes and case laws
  3. LLM synthesis and analysis
  ↓
Output: Comprehensive research report
```

#### e) Document Drafter (`document_drafter.py`)
```
Input: Notice type, facts, relief sought
  ↓
Template selection
  ↓
LLM-based content generation
  ↓
Format according to Indian legal standards
  ↓
Output: Professional legal notice
```

#### f) Limitation Checker (`limitation_checker.py`)
```
Input: Case type, cause of action date
  ↓
Match with Limitation Act provisions
  ↓
Calculate time periods
  ↓
Check special circumstances
  ↓
Output: Limitation analysis with deadline
```

### 3. Configuration Layer (`src/config.py`)

- **Environment Management**: Uses pydantic-settings for type-safe config
- **Settings Categories**:
  - Server configuration
  - AI model settings (OpenAI/Anthropic)
  - Database connections
  - API endpoints
  - Feature flags

### 4. Utils Layer (`src/utils/`)

#### Logger (`logger.py`)
- Structured logging with loguru
- Console and file outputs
- Configurable log levels
- Automatic log rotation

### 5. Models Layer (`src/models/`)

Data models using Pydantic:
- `CaseLaw`: Case law/precedent representation
- `LegalDocument`: Document metadata
- `Party`: Case parties
- `ResearchQuery`: Research request tracking
- `ResearchResult`: Research output structure

## Data Flow

### Example: Precedent Search Flow

```
1. Client Request
   ↓
   {
     "tool": "search_precedents",
     "query": "breach of contract damages",
     "jurisdiction": "supreme_court"
   }

2. MCP Server receives request
   ↓
   server.py: call_tool()
   
3. Route to tool handler
   ↓
   precedent_search.py: search_precedents()
   
4. Process query
   ↓
   • Embed query using sentence-transformers
   • Semantic search in ChromaDB
   • Retrieve top-k similar cases
   
5. Enhance results
   ↓
   • Fetch full case details from Indian Kanoon
   • Calculate relevance scores
   • Format results
   
6. Return to client
   ↓
   {
     "results": [
       {
         "case_name": "...",
         "citation": "AIR 2020 SC 1234",
         "relevance_score": 0.95,
         "summary": "...",
         ...
       }
     ]
   }
```

## Technology Stack

### Core Technologies
- **Language**: Python 3.12+
- **Protocol**: Model Context Protocol (MCP)
- **Framework**: asyncio for async operations

### AI & ML
- **LLM Integration**: OpenAI GPT-4 / Anthropic Claude
- **Embeddings**: sentence-transformers
- **Orchestration**: LangChain
- **Vector DB**: ChromaDB / Pinecone

### Document Processing
- **PDF**: PyPDF2, pdfplumber
- **Word**: python-docx
- **OCR**: (Future) Tesseract

### Data & Storage
- **Database**: SQLAlchemy (SQLite/PostgreSQL)
- **Vector Store**: ChromaDB
- **File Storage**: Local filesystem

### External Integrations
- **Indian Kanoon**: Case law database
- **Court APIs**: Supreme Court, High Courts
- **Web Scraping**: BeautifulSoup, aiohttp

## Security Architecture

### Authentication & Authorization
- API key management via environment variables
- Secret key for JWT tokens (if using REST API)

### Data Protection
- Document encryption at rest (future)
- Secure API communication (HTTPS)
- Rate limiting per client
- Input validation with Pydantic

### Privacy
- No PII stored without consent
- Client data isolation
- Audit logging for all operations

## Scalability Considerations

### Current Architecture (Single Server)
```
Client → MCP Server (Python) → Tools → External APIs
```

### Future Scalable Architecture
```
                    ┌─────────────────┐
                    │  Load Balancer  │
                    └────────┬────────┘
                             │
          ┌──────────────────┼──────────────────┐
          │                  │                  │
    ┌─────▼─────┐     ┌─────▼─────┐     ┌─────▼─────┐
    │ MCP Server│     │ MCP Server│     │ MCP Server│
    │ Instance 1│     │ Instance 2│     │ Instance 3│
    └─────┬─────┘     └─────┬─────┘     └─────┬─────┘
          │                  │                  │
          └──────────────────┼──────────────────┘
                             │
                    ┌────────▼────────┐
                    │  Shared Storage │
                    │  • Vector DB    │
                    │  • Cache        │
                    │  • Database     │
                    └─────────────────┘
```

## Deployment Architecture

### Development
```
Local Machine
├── Python venv
├── SQLite database
├── Local ChromaDB
└── File-based storage
```

### Production (Docker)
```
Docker Container
├── Wakalat-AI Server
├── Environment variables
├── Volume mounts
│   ├── data/
│   ├── logs/
│   └── documents/
└── Network bridge
    └── External APIs
```

### Production (Kubernetes)
```
Kubernetes Cluster
├── Deployment (3 replicas)
├── Service (Load Balancer)
├── ConfigMap (Config)
├── Secret (API Keys)
├── PersistentVolume (Data)
└── Ingress (HTTPS)
```

## Performance Optimization

### Caching Strategy
1. **Query Cache**: Cache frequent search queries (Redis)
2. **Document Cache**: Cache parsed documents (Memory/Disk)
3. **API Response Cache**: Cache external API responses (TTL: 1 hour)

### Database Optimization
1. **Vector DB Indexing**: HNSW index for fast similarity search
2. **SQL Indexing**: Index on citation, date, court
3. **Connection Pooling**: Reuse database connections

### Async Operations
1. **Concurrent API Calls**: Use asyncio for parallel requests
2. **Background Tasks**: Queue long-running tasks (Celery)
3. **Streaming**: Stream large documents instead of loading fully

## Monitoring & Observability

### Metrics
- Request count and latency
- Tool usage statistics
- API call success/failure rates
- Cache hit rates

### Logging
- Structured logs (JSON format)
- Log levels: DEBUG, INFO, WARNING, ERROR
- Rotation: Daily or 10MB
- Retention: 30 days

### Alerting (Future)
- High error rate alerts
- API rate limit warnings
- Storage capacity alerts

## Extension Points

### Adding New Tools
```python
# src/tools/new_tool.py
async def new_tool_function(arg1: str, arg2: int) -> str:
    # Implementation
    return result

# src/server.py
@app.list_tools()
async def list_tools():
    tools.append(Tool(
        name="new_tool",
        description="...",
        inputSchema={...}
    ))

@app.call_tool()
async def call_tool(name: str, arguments: Any):
    if name == "new_tool":
        result = await new_tool_function(**arguments)
        return [TextContent(type="text", text=result)]
```

### Adding New Data Sources
```python
# src/utils/data_sources.py
class NewDataSource:
    async def search(self, query: str):
        # Implement search
        pass
    
    async def retrieve(self, id: str):
        # Implement retrieval
        pass
```

### Custom Models
```python
# src/models/custom.py
from pydantic import BaseModel

class CustomModel(BaseModel):
    field1: str
    field2: int
```

## Future Enhancements

1. **Multi-language Support**: Hindi, regional languages
2. **Advanced Analytics**: Case outcome prediction
3. **Real-time Updates**: Court case status tracking
4. **Collaborative Features**: Multi-user case management
5. **Mobile App**: Native iOS/Android clients
6. **Voice Interface**: Speech-to-text for queries
7. **Blockchain**: Immutable audit trail for legal documents

---

For implementation details, see individual module documentation.
