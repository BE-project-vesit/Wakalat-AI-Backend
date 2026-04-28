# Wakalat-AI Backend - MCP Server


## 📝 To-Do

- [ ] Figure out what sql command was done in the supabase database also figure out the enditre   embeddings thing in general  
- [ ] make HTTP server 
- [ ] work on the other tools except precedent searcher




A **Model Context Protocol (MCP)** server for assisting lawyers in India with case preparation, precedent finding, case law research, and legal document processing. This backend is frontend-agnostic and designed to work with any MCP-compatible client.

## 🎯 Overview

Wakalat-AI is a specialized MCP server that provides AI-powered tools for legal professionals, specifically tailored for the Indian legal system. It offers:

- **Precedent Search**: Find relevant case laws and precedents from Indian Supreme Court and High Courts
- **Case Law Finder**: Retrieve specific judgments by citation, party names, or legal provisions
- **Document Analysis**: Analyze legal documents (petitions, contracts, notices) for issues and compliance
- **Legal Research**: Conduct comprehensive research on legal topics with statutory and case law references
- **Document Drafting**: Generate legal notices, petitions, and other legal documents
- **Limitation Checker**: Calculate limitation periods under the Limitation Act, 1963

## 🏗️ Architecture

This MCP server is built using:

- **MCP Protocol**: For frontend-agnostic communication
- **Python 3.12+**: Core implementation language
- **LangChain**: For document processing and RAG
- **Vector Database**: ChromaDB for semantic search of legal cases ✅ **IMPLEMENTED**
- **LLM Integration**: OpenAI/Anthropic for intelligent analysis

## 📁 Project Structure

```
Wakalat-AI-Backend/
├── src/
│   ├── __init__.py
│   ├── server.py              # Main MCP server implementation
│   ├── config.py              # Configuration management
│   ├── tools/                 # MCP tools implementations
│   │   ├── __init__.py
│   │   ├── precedent_search.py
│   │   ├── case_law_finder.py
│   │   ├── document_analyzer.py
│   │   ├── legal_research.py
│   │   ├── document_drafter.py
│   │   └── limitation_checker.py
│   ├── services/              # Service layer
│   │   ├── __init__.py
│   │   └── vector_db.py       # Vector database service
│   ├── utils/                 # Utility modules
│   │   ├── __init__.py
│   │   └── logger.py
│   └── models/                # Data models
│       ├── __init__.py
│       └── case.py
├── scripts/                    # Utility scripts
│   └── load_sample_data.py    # Load sample cases into vector DB
├── data/                      # Data storage directory
│   ├── chroma/               # Vector database
│   └── documents/            # Document storage
├── logs/                      # Application logs
├── requirements.txt           # Python dependencies
├── .env.example              # Environment variables template
├── .gitignore
└── README.md
```

## 🚀 Getting Started

### Server Types

This project provides **two MCP server implementations**:

#### **1. STDIO MCP Server** (`main.py`)

- **Use case**: Local development, Claude Desktop integration
- **Transport**: stdin/stdout pipes
- **Pros**: Lightweight, secure, standard MCP approach
- **Best for**: Desktop apps, local testing

#### **2. HTTP MCP Server** (`http_main.py`)

- **Use case**: Web applications, remote access, microservices
- **Transport**: HTTP/WebSocket
- **Pros**: Network accessible, RESTful endpoints, scalable
- **Best for**: Web apps, cloud deployment, API integration
- **Endpoints**:
  - `http://localhost:8000/mcp` - MCP protocol endpoint
  - `http://localhost:8000/health` - Health check
  - `http://localhost:8000/docs` - API documentation

### Prerequisites

- Python 3.12 or higher
- pip (Python package manager)
- Virtual environment (recommended)

### Installation

#### Option 1: Using uv (Recommended - Fast & Modern)

1. **Clone the repository**

   ```bash
   git clone https://github.com/BE-project-vesit/Wakalat-AI-Backend.git
   cd Wakalat-AI-Backend
   ```

2. **Install dependencies with uv**

   ```bash
   uv sync
   ```

3. **Configure environment variables**

   ```bash
   cp .env.example .env
   # Edit .env and add your API keys and configuration
   ```

4. **Load sample data** (optional but recommended)

   ```bash
   uv run python scripts/load_sample_data.py
   ```

5. **Run the MCP server**

   **Option A: STDIO MCP Server (for Claude Desktop)**

   ```bash
   uv run main.py
   ```

   **Option B: HTTP MCP Server (for web clients)**

   ```bash
   uv run http_main.py
   ```

   Server will be available at: `http://localhost:8000/mcp`

6. **Test with MCP Inspector**

   **For STDIO server:**

   ```bash
   npx @modelcontextprotocol/inspector uv run main.py
   ```

   **For HTTP server:**

   ```bash
   # Start HTTP server first
   uv run http_main.py

   # Then test with curl or browser
   curl http://localhost:8000/health
   ```

#### Option 2: Traditional pip/venv

1. **Clone the repository**

   ```bash
   git clone https://github.com/BE-project-vesit/Wakalat-AI-Backend.git
   cd Wakalat-AI-Backend
   ```

2. **Create a virtual environment**

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**

   ```bash
   cp .env.example .env
   # Edit .env and add your API keys and configuration
   ```

5. **Load sample data into vector database** (optional but recommended)

   ```bash
   python scripts/load_sample_data.py
   ```

6. **Run the MCP server**
   ```bash
   python -m src.server
   ```

## ⚙️ Configuration

Key environment variables in `.env`:

```env
# AI Model Configuration
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4-turbo-preview

# Database Configuration
DATABASE_URL=sqlite:///./data/wakalat.db
CHROMA_PERSIST_DIRECTORY=./data/chroma

# Vector Database (optional)
USE_TRANSFORMERS=false  # Set to true to use sentence-transformers for embeddings

# Indian Legal Resources
INDIANKANOON_BASE_URL=https://indiankanoon.org
SUPREME_COURT_API_URL=https://api.sci.gov.in

# Feature Flags
ENABLE_PRECEDENT_SEARCH=true
ENABLE_CASE_LAW_SEARCH=true
ENABLE_DOCUMENT_GENERATION=true
ENABLE_LEGAL_RESEARCH=true
```

## 🔧 Available MCP Tools

### 1. search_precedents

Search for legal precedents from Indian courts.

```json
{
  "query": "breach of contract damages",
  "jurisdiction": "supreme_court",
  "year_from": 2015,
  "max_results": 10
}
```

### 2. find_case_laws

Find specific case laws by citation or party name.

```json
{
  "citation": "AIR 2020 SC 1234",
  "include_summary": true
}
```

### 3. analyze_document

Analyze legal documents for issues and compliance.

```json
{
  "document_path": "/path/to/document.pdf",
  "document_type": "petition",
  "analysis_type": "full"
}
```

### 4. legal_research

Conduct comprehensive legal research.

```json
{
  "research_query": "vicarious liability under tort law",
  "research_depth": "detailed",
  "include_statutes": true,
  "include_case_laws": true
}
```

### 5. draft_legal_notice

Draft legal notices. Requires at least one of `GEMINI_API_KEY`, `OPENAI_API_KEY`, or `ANTHROPIC_API_KEY` in `.env` (see `.env.example`). Response is JSON with `drafted_notice` on success, or `error` if keys are missing or the LLM call fails.

```json
{
  "notice_type": "demand",
  "facts": "Payment due for services rendered...",
  "relief_sought": "Payment of Rs. 50,000 within 15 days"
}
```

### 6. check_limitation

Check limitation periods under Indian law.

```json
{
  "case_type": "suit_for_money_lent",
  "cause_of_action_date": "2021-06-15"
}
```

## 🗄️ Vector Database

The server includes a **vector database integration** for efficient semantic search of case laws and precedents:

### Features

- ✅ **ChromaDB Integration**: Persistent storage of case embeddings
- ✅ **Semantic Search**: Find similar cases based on meaning, not just keywords
- ✅ **Metadata Filtering**: Filter by court, year, jurisdiction
- ✅ **Fallback Mode**: Works offline with basic embeddings
- ✅ **Sample Data**: Includes 5 sample Indian Supreme Court cases

### Quick Start

```bash
# Load sample data
python scripts/load_sample_data.py

# Test vector search
python -c "
from src.services.vector_db import get_vector_db
vdb = get_vector_db()
results = vdb.search_cases('breach of contract', n_results=3)
for r in results:
    print(f'{r[\"case_name\"]}: {r[\"relevance_score\"]}')
"
```

For detailed documentation, see [docs/VECTOR_DATABASE.md](docs/VECTOR_DATABASE.md)

## 🔌 Integration with MCP Clients

This server follows the Model Context Protocol specification and can be integrated with any MCP-compatible client:

### With Claude Desktop

Add to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "wakalat-ai": {
      "command": "python",
      "args": ["-m", "src.server"],
      "env": {
        "OPENAI_API_KEY": "your-key-here"
      }
    }
  }
}
```

### With Custom Clients

Connect using stdio transport:

```python
from mcp.client import Client

async with Client() as client:
    await client.connect("python", ["-m", "src.server"])
    tools = await client.list_tools()
    result = await client.call_tool("search_precedents", {"query": "..."})
```

## 🔨 Development

### Testing with MCP Inspector

The **MCP Inspector** is a web-based testing tool that provides an interactive interface for testing MCP servers during development.

#### Quick Start with Inspector

1. **Install and run the inspector** (one command does everything):

   ```bash
   npx @modelcontextprotocol/inspector uv run main.py
   ```

2. **Open the web interface**:
   - The inspector will automatically open in your browser
   - URL: `http://localhost:6274`
   - Use the provided auth token in the URL

#### What the Inspector provides:

- **🛠️ Tool Testing**: Interactive interface to test all legal tools
- **📊 Real-time Debugging**: See JSON-RPC messages and responses
- **📝 Resource Browser**: View available legal templates and guides
- **🔍 Schema Validation**: Verify tool inputs and outputs

#### Testing Your Tools

In the Inspector web interface, you can test tools like:

```json
// Test precedent search
{
  "query": "breach of contract damages",
  "jurisdiction": "supreme_court",
  "max_results": 5
}

// Test case law finder
{
  "citation": "AIR 2020 SC 1234",
  "include_summary": true
}

// Test document analysis
{
  "document_path": "./data/documents/sample_contract.pdf",
  "document_type": "contract",
  "analysis_type": "full"
}
```

#### Alternative: Manual Server Testing

If you prefer to run the server manually:

```bash
# Terminal 1: Start the server
uv run main.py

# Terminal 2: Test with curl (example)
echo '{"jsonrpc":"2.0","method":"tools/list","id":1}' | uv run main.py
```

#### Inspector Features

- **📱 Responsive UI**: Test tools from any device
- **🔐 Secure Access**: Authentication tokens for security
- **📋 Request History**: Review previous tool calls
- **⚡ Hot Reload**: Restart server without losing session

#### Troubleshooting Inspector

If the inspector fails to connect:

1. **Check server imports**:

   ```bash
   uv run python -c "from src.server import main; print('✓ Server imports OK')"
   ```

2. **Verify tool implementations**:

   ```bash
   uv run python -c "from src.tools.precedent_search import search_precedents; print('✓ Tools OK')"
   ```

3. **Run with debug logging**:

   ```bash
   LOG_LEVEL=DEBUG npx @modelcontextprotocol/inspector uv run main.py
   ```

4. **Disable auth for testing**:
   ```bash
   DANGEROUSLY_OMIT_AUTH=true npx @modelcontextprotocol/inspector uv run main.py
   ```

### Running Tests

```bash
pytest tests/
```

### Code Quality

```bash
# Format code
black src/

# Lint code
flake8 src/

# Type checking
mypy src/
```

## 📚 Implementation Roadmap

This is a **template implementation**. To make it fully functional:

### Phase 1: Data Integration

- [ ] Integrate with Indian Kanoon API for case law retrieval
- [ ] Set up web scraping for Supreme Court/High Court websites
- [x] Create embeddings for legal documents using sentence-transformers
- [x] Build vector database with ChromaDB/Pinecone

### Phase 2: AI Enhancement

- [ ] Implement RAG pipeline with LangChain
- [ ] Fine-tune prompts for Indian legal context
- [ ] Add entity extraction (NER) for legal documents
- [x] Implement semantic search for precedents

### Phase 3: Document Processing

- [ ] Complete PDF parsing with pdfplumber
- [ ] Add DOCX support with python-docx
- [ ] Implement OCR for scanned documents
- [ ] Create document classification models

### Phase 4: Advanced Features

- [ ] Multi-language support (Hindi, regional languages)
- [ ] Case outcome prediction models
- [ ] Citation network analysis
- [ ] Real-time court case status tracking

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is part of the BE Project at VESIT.

## 🔗 Resources

- [Model Context Protocol Documentation](https://modelcontextprotocol.io)
- [Indian Kanoon](https://indiankanoon.org) - Indian case law database
- [Supreme Court of India](https://main.sci.gov.in)
- [LangChain Documentation](https://python.langchain.com)

## 💡 Use Cases

1. **Case Preparation**: Search for relevant precedents and build stronger arguments
2. **Legal Research**: Quickly research complex legal topics with AI assistance
3. **Document Review**: Analyze contracts and legal documents for potential issues
4. **Limitation Tracking**: Never miss a deadline with automatic limitation calculation
5. **Document Drafting**: Generate professional legal notices and petitions

## ⚠️ Disclaimer

This tool is designed to assist legal professionals and should not replace qualified legal advice. Always verify all information and consult with appropriate legal counsel before taking any legal action.

## 📧 Contact

For questions or support, please open an issue on GitHub or contact the development team at VESIT.

---

**Built with ❤️ by BE Project Team, VESIT**
