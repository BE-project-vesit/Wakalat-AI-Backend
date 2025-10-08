# Wakalat-AI Backend Development Scripts

## Quick Start with uv

### 1. Initialize uv environment

```bash
uv sync
```

### 2. Run the MCP server

```bash
uv run main.py
```

### 3. Run with development dependencies

```bash
uv sync --extra dev
uv run main.py
```

### 4. Install as package and run

```bash
uv pip install -e .
uv run wakalat-ai
```

## Development Commands

### Code formatting

```bash
uv run black src/ tests/
uv run ruff check src/ tests/
uv run ruff check --fix src/ tests/
```

### Type checking

```bash
uv run mypy src/
```

### Testing

```bash
uv run pytest
uv run pytest -v
uv run pytest tests/test_specific.py
```

### Install additional dependencies

```bash
# Add a new dependency
uv add package-name

# Add development dependency
uv add --dev package-name

# Install optional web dependencies
uv sync --extra web
```

## Environment Management

### Create .env file for configuration

```bash
cp .env.example .env
# Edit .env with your API keys and settings
```

### Check environment

```bash
uv run python -c "from src.config import settings; print(f'Server: {settings.mcp_server_name}')"
```

## Production Usage

### Install from git

```bash
uv pip install git+https://github.com/BE-project-vesit/Wakalat-AI-Backend.git
```

### Run installed package

```bash
wakalat-ai
```
