# Wakalat-AI Backend - MCP Server

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
- **Vector Database**: ChromaDB for semantic search of legal cases
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
│   ├── utils/                 # Utility modules
│   │   ├── __init__.py
│   │   └── logger.py
│   └── models/                # Data models
│       ├── __init__.py
│       └── case.py
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

### Prerequisites

- Python 3.12 or higher
- pip (Python package manager)
- Virtual environment (recommended)

### Installation

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

5. **Run the MCP server**
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
Draft legal notices.

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
- [ ] Create embeddings for legal documents using sentence-transformers
- [ ] Build vector database with ChromaDB/Pinecone

### Phase 2: AI Enhancement
- [ ] Implement RAG pipeline with LangChain
- [ ] Fine-tune prompts for Indian legal context
- [ ] Add entity extraction (NER) for legal documents
- [ ] Implement semantic search for precedents

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
