# Quick Start Guide - Wakalat-AI Backend

Get up and running with Wakalat-AI MCP Server in 5 minutes!

## Prerequisites

- Python 3.12 or higher
- pip package manager
- (Optional) Docker for containerized deployment

## Installation Methods

### Method 1: Automated Setup (Recommended)

```bash
# Clone the repository
git clone https://github.com/BE-project-vesit/Wakalat-AI-Backend.git
cd Wakalat-AI-Backend

# Run the setup script
chmod +x scripts/setup.sh
./scripts/setup.sh

# Edit .env with your API keys
nano .env

# Run the server
./scripts/run_server.sh
```

### Method 2: Manual Setup

```bash
# 1. Clone the repository
git clone https://github.com/BE-project-vesit/Wakalat-AI-Backend.git
cd Wakalat-AI-Backend

# 2. Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
cp .env.example .env
# Edit .env and add your API keys

# 5. Create necessary directories
mkdir -p data/chroma data/documents logs

# 6. Run the server
python -m src.server
```

### Method 3: Docker

```bash
# Build the container
docker build -t wakalat-ai .

# Run the container
docker run -it --rm \
  -e OPENAI_API_KEY=your-key-here \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/logs:/app/logs \
  wakalat-ai

# Or use docker-compose
docker-compose up
```

## Configuration

### Essential Environment Variables

Edit `.env` and set these required variables:

```env
# Required: OpenAI API Key (or Anthropic)
OPENAI_API_KEY=sk-...

# Optional but recommended
OPENAI_MODEL=gpt-4-turbo-preview
LOG_LEVEL=INFO
```

### Optional Configurations

```env
# Use Anthropic Claude instead of OpenAI
# ANTHROPIC_API_KEY=sk-ant-...
# ANTHROPIC_MODEL=claude-3-opus-20240229

# Database (default: SQLite)
# DATABASE_URL=postgresql://user:pass@localhost/wakalat_db

# Vector Database
CHROMA_PERSIST_DIRECTORY=./data/chroma
CHROMA_COLLECTION_NAME=legal_cases
```

## Testing the Installation

### Test 1: Check Server Starts

```bash
python -m src.server
```

You should see:
```
Starting wakalat-ai-legal-assistant v1.0.0
```

### Test 2: Run Unit Tests

```bash
pytest tests/ -v
```

### Test 3: Test a Tool (Python)

```python
import asyncio
from src.tools.limitation_checker import check_limitation_period

async def test():
    result = await check_limitation_period(
        case_type="suit_for_money_lent",
        cause_of_action_date="2020-01-01"
    )
    print(result)

asyncio.run(test())
```

## Integration with MCP Clients

### With Claude Desktop

1. **Locate Claude Desktop config file:**
   - macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - Windows: `%APPDATA%\Claude\claude_desktop_config.json`

2. **Add Wakalat-AI server:**
   ```json
   {
     "mcpServers": {
       "wakalat-ai": {
         "command": "python",
         "args": ["-m", "src.server"],
         "cwd": "/full/path/to/Wakalat-AI-Backend",
         "env": {
           "OPENAI_API_KEY": "your-key-here"
         }
       }
     }
   }
   ```

3. **Restart Claude Desktop**

4. **Test the integration:**
   Open Claude and ask:
   ```
   "Check the limitation period for a suit for money lent with cause of action on January 1, 2021"
   ```

### With Custom MCP Client

```python
from mcp.client import Client
import asyncio

async def main():
    async with Client() as client:
        # Connect to Wakalat-AI server
        await client.connect(
            "python",
            ["-m", "src.server"],
            cwd="/path/to/Wakalat-AI-Backend"
        )
        
        # List available tools
        tools = await client.list_tools()
        print(f"Available tools: {[t.name for t in tools]}")
        
        # Call a tool
        result = await client.call_tool(
            "check_limitation",
            {
                "case_type": "suit_for_money_lent",
                "cause_of_action_date": "2021-01-01"
            }
        )
        print(f"Result: {result}")

asyncio.run(main())
```

## First Steps

### Example 1: Check Limitation Period

Ask the MCP client:
```
"Is a suit for recovery of money lent on March 15, 2021 still within the limitation period today?"
```

### Example 2: Search for Precedents

Ask:
```
"Find Supreme Court precedents on breach of contract and damages from the last 5 years"
```

### Example 3: Draft a Legal Notice

Ask:
```
"Draft a legal notice for recovery of Rs. 50,000 owed for professional services provided"
```

## Common Issues and Solutions

### Issue 1: ModuleNotFoundError

**Problem:** `ModuleNotFoundError: No module named 'mcp'`

**Solution:**
```bash
pip install mcp
# Or reinstall all dependencies
pip install -r requirements.txt
```

### Issue 2: No API Key

**Problem:** Tools fail with "API key not configured"

**Solution:**
```bash
# Make sure .env file exists
cp .env.example .env

# Edit .env and add your API key
echo "OPENAI_API_KEY=sk-your-key-here" >> .env
```

### Issue 3: Permission Denied

**Problem:** `Permission denied` when creating directories

**Solution:**
```bash
# Create directories manually
mkdir -p data/chroma data/documents logs
chmod 755 data logs
```

### Issue 4: Port Already in Use

**Problem:** Port 8000 already in use (if using FastAPI mode)

**Solution:**
```bash
# Change port in .env
echo "MCP_SERVER_PORT=8001" >> .env
```

## Next Steps

1. **Explore Examples**: Check `EXAMPLES.md` for more usage examples
2. **Read Architecture**: See `ARCHITECTURE.md` for system design
3. **Contribute**: Read `CONTRIBUTING.md` to contribute
4. **Customize**: Modify tools in `src/tools/` for your needs
5. **Deploy**: Use Docker or Kubernetes for production deployment

## Getting Help

- **Documentation**: Read the `README.md` and other docs
- **Issues**: Open an issue on GitHub
- **Discussions**: Start a discussion for questions
- **Email**: Contact the development team

## Useful Commands

```bash
# Activate virtual environment
source venv/bin/activate

# Run server
python -m src.server

# Run tests
pytest tests/ -v

# Format code
black src/

# Lint code
flake8 src/

# Type check
mypy src/

# Update dependencies
pip install -r requirements.txt --upgrade

# Clean up
rm -rf data/ logs/ __pycache__/ .pytest_cache/
```

## Development Mode

For development with auto-reload:

```bash
# Install development dependencies
pip install watchdog

# Run with auto-reload (if using uvicorn)
uvicorn src.server:app --reload

# Or use nodemon equivalent for Python
pip install watchfiles
watchfiles "python -m src.server" src/
```

## Production Deployment

### Docker Production

```bash
# Build production image
docker build -t wakalat-ai:prod -f Dockerfile .

# Run in production mode
docker run -d \
  --name wakalat-ai-prod \
  --restart unless-stopped \
  -e OPENAI_API_KEY=your-key \
  -v /var/data/wakalat:/app/data \
  -v /var/logs/wakalat:/app/logs \
  wakalat-ai:prod
```

### Kubernetes Deployment

```bash
# Create namespace
kubectl create namespace wakalat-ai

# Create secret for API keys
kubectl create secret generic wakalat-secrets \
  --from-literal=openai-api-key=your-key \
  -n wakalat-ai

# Deploy application
kubectl apply -f k8s/deployment.yaml -n wakalat-ai
```

## Monitoring

```bash
# View logs
tail -f logs/wakalat-ai.log

# In Docker
docker logs -f wakalat-ai-prod

# In Kubernetes
kubectl logs -f deployment/wakalat-ai -n wakalat-ai
```

## Performance Tips

1. **Enable Caching**: Set `ENABLE_CACHE=true` in .env
2. **Use GPU**: For faster embeddings, use GPU-enabled transformers
3. **Optimize Database**: Use PostgreSQL instead of SQLite for production
4. **Rate Limiting**: Configure `RATE_LIMIT_PER_MINUTE` appropriately
5. **Concurrent Requests**: Tune `MAX_CONCURRENT_REQUESTS`

## Security Checklist

- [ ] Changed `SECRET_KEY` in production
- [ ] API keys stored securely (not in code)
- [ ] HTTPS enabled for production
- [ ] Rate limiting configured
- [ ] Input validation enabled
- [ ] Logs don't contain sensitive data
- [ ] Regular security updates

---

**You're all set!** 🎉

Start exploring the power of AI-assisted legal research with Wakalat-AI.

For more information, see:
- `README.md` - Full documentation
- `EXAMPLES.md` - Usage examples
- `ARCHITECTURE.md` - System architecture
- `CONTRIBUTING.md` - How to contribute
