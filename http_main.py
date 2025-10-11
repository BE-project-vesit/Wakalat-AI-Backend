#!/usr/bin/env python3
"""
HTTP MCP Server entry point for Wakalat-AI
Can be run directly or via uv
"""
import sys
import asyncio
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.http_server import main

if __name__ == "__main__":
    main()