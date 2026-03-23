"""
Minimal HTTP MCP Server for testing - without heavy dependencies
"""
import asyncio
import json
from typing import Any, Dict, List, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

from src.config import settings
from src.utils.logger import setup_logger

# Initialize logger
logger = setup_logger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Wakalat-AI MCP Server (Minimal)",
    description="Minimal HTTP MCP Server for Legal Assistant Tools",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for testing
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Pydantic models
class ToolCall(BaseModel):
    name: str
    arguments: Dict[str, Any]


class ToolResponse(BaseModel):
    success: bool
    result: Optional[str] = None
    error: Optional[str] = None


class Tool(BaseModel):
    name: str
    description: str
    inputSchema: Dict[str, Any]


class ListToolsResponse(BaseModel):
    tools: List[Tool]


# Mock implementations of tools (for testing without dependencies)
async def mock_search_precedents(**kwargs) -> str:
    """Mock precedent search"""
    query = kwargs.get("query", "unknown")
    return json.dumps({
        "query": query,
        "results": [
            {
                "case_name": "Sample Case v. Test Party",
                "citation": "AIR 2023 SC 123",
                "court": "Supreme Court of India",
                "year": 2023,
                "summary": f"Mock precedent for query: {query}",
                "relevance_score": 0.95
            }
        ],
        "total_found": 1,
        "mock": True
    }, indent=2)


async def mock_find_case_laws(**kwargs) -> str:
    """Mock case law finder"""
    citation = kwargs.get("citation", "unknown")
    return json.dumps({
        "citation": citation,
        "case_name": "Mock Case Name",
        "summary": f"Mock case law for citation: {citation}",
        "mock": True
    }, indent=2)


async def mock_legal_research(**kwargs) -> str:
    """Mock legal research"""
    query = kwargs.get("research_query", "unknown")
    return json.dumps({
        "research_query": query,
        "findings": f"Mock legal research results for: {query}",
        "mock": True
    }, indent=2)


# Tool definitions
def get_available_tools() -> List[Tool]:
    """Get list of available MCP tools"""
    return [
        Tool(
            name="search_precedents",
            description="Search for legal precedents (Mock Implementation)",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The legal issue to search for"
                    },
                    "max_results": {
                        "type": "integer",
                        "default": 5
                    }
                },
                "required": ["query"]
            }
        ),
        Tool(
            name="find_case_laws",
            description="Find case laws by citation (Mock Implementation)",
            inputSchema={
                "type": "object",
                "properties": {
                    "citation": {
                        "type": "string",
                        "description": "Case citation"
                    }
                },
                "required": ["citation"]
            }
        ),
        Tool(
            name="legal_research",
            description="Conduct legal research (Mock Implementation)",
            inputSchema={
                "type": "object",
                "properties": {
                    "research_query": {
                        "type": "string",
                        "description": "Legal research question"
                    }
                },
                "required": ["research_query"]
            }
        )
    ]


async def execute_tool(name: str, arguments: Dict[str, Any]) -> str:
    """Execute a tool and return the result"""
    logger.info(f"Executing tool: {name} with arguments: {arguments}")
    
    if name == "search_precedents":
        return await mock_search_precedents(**arguments)
    elif name == "find_case_laws":
        return await mock_find_case_laws(**arguments)
    elif name == "legal_research":
        return await mock_legal_research(**arguments)
    else:
        raise ValueError(f"Unknown tool: {name}")


# API Endpoints
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "server": "wakalat-ai-minimal",
        "version": "1.0.0",
        "type": "minimal-http-mcp-server"
    }


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Wakalat-AI Minimal HTTP MCP Server",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "tools": "/tools",
            "tools_execute": "/tools/execute",
            "docs": "/docs"
        },
        "note": "This is a minimal server for testing without heavy dependencies"
    }


@app.get("/tools", response_model=ListToolsResponse)
async def list_tools():
    """List all available tools"""
    tools = get_available_tools()
    logger.info(f"Listed {len(tools)} available tools")
    return ListToolsResponse(tools=tools)


@app.post("/tools/execute", response_model=ToolResponse)
async def execute_tool_endpoint(tool_call: ToolCall):
    """Execute a specific tool"""
    try:
        result = await execute_tool(tool_call.name, tool_call.arguments)
        return ToolResponse(success=True, result=result)
    except Exception as e:
        logger.error(f"Tool execution failed: {str(e)}")
        return ToolResponse(success=False, error=str(e))


@app.get("/tools/{tool_name}")
async def get_tool_info(tool_name: str):
    """Get information about a specific tool"""
    tools = get_available_tools()
    tool = next((t for t in tools if t.name == tool_name), None)
    
    if not tool:
        raise HTTPException(status_code=404, detail=f"Tool '{tool_name}' not found")
    
    return tool


def main():
    """Main entry point"""
    logger.info("Starting Minimal HTTP MCP Server")
    logger.info(f"Server will be available at: http://localhost:{settings.mcp_server_port}")
    logger.info(f"API Documentation: http://localhost:{settings.mcp_server_port}/docs")
    
    try:
        config = uvicorn.Config(
            app=app,
            host="0.0.0.0",
            port=settings.mcp_server_port,
            log_level="info",
            reload=False
        )
        server = uvicorn.Server(config)
        asyncio.run(server.serve())
    except KeyboardInterrupt:
        logger.info("Server shutdown requested")
    except Exception as e:
        logger.error(f"Server error: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    main()