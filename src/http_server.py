"""
HTTP MCP Server Implementation for Wakalat-AI
Provides the same tools as stdio server but over HTTP/WebSocket
"""
import asyncio
import json
from typing import Any, Dict, List, Optional
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from starlette.requests import Request
import uvicorn

from mcp.server.sse import SseServerTransport
from src.config import settings
from src.server import app as mcp_server
from src.tools.precedent_search import search_precedents
from src.tools.case_law_finder import find_case_laws
from src.tools.document_analyzer import analyze_legal_document
from src.tools.legal_research import conduct_legal_research
from src.tools.deep_research import deep_research
from src.utils.logger import setup_logger

# Initialize logger
logger = setup_logger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Wakalat-AI MCP Server",
    description="HTTP MCP Server for Legal Assistant Tools",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# SSE transport for MCP protocol over HTTP
sse_transport = SseServerTransport("/messages/")


@app.get("/sse")
async def handle_sse(request: Request):
    """SSE endpoint for MCP protocol communication"""
    async with sse_transport.connect_sse(
        request.scope, request.receive, request._send
    ) as (read_stream, write_stream):
        await mcp_server.run(
            read_stream,
            write_stream,
            mcp_server.create_initialization_options(),
        )


app.mount("/messages/", app=sse_transport.handle_post_message)


# Pydantic models for requests/responses
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


# MCP Tool definitions
def get_available_tools() -> List[Tool]:
    """Get list of available MCP tools"""
    tools = []
    
    if settings.enable_precedent_search:
        tools.append(Tool(
            name="search_precedents",
            description=(
                "Search for legal precedents relevant to a case. "
                "This tool searches through Indian Supreme Court and High Court judgments "
                "to find similar cases and their outcomes. Useful for building arguments "
                "based on established legal principles."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The legal issue or query to search for precedents"
                    },
                    "jurisdiction": {
                        "type": "string",
                        "enum": ["supreme_court", "high_court", "all"],
                        "description": "The court jurisdiction to search in",
                        "default": "all"
                    },
                    "year_from": {
                        "type": "integer",
                        "description": "Start year for filtering results (optional)"
                    },
                    "year_to": {
                        "type": "integer",
                        "description": "End year for filtering results (optional)"
                    },
                    "max_results": {
                        "type": "integer",
                        "description": "Maximum number of results to return",
                        "default": 10
                    }
                },
                "required": ["query"]
            }
        ))
    
    if settings.enable_case_law_search:
        tools.append(Tool(
            name="find_case_laws",
            description=(
                "Find specific case laws by citation, party names, or legal provisions. "
                "This tool retrieves full text of judgments from Indian courts and "
                "provides summaries, key points, and relevant sections."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "citation": {
                        "type": "string",
                        "description": "Case citation (e.g., 'AIR 2020 SC 1234')"
                    },
                    "party_name": {
                        "type": "string",
                        "description": "Name of party in the case"
                    },
                    "legal_provision": {
                        "type": "string",
                        "description": "Specific legal provision or section (e.g., 'Section 420 IPC')"
                    },
                    "include_summary": {
                        "type": "boolean",
                        "description": "Include AI-generated summary of the case",
                        "default": True
                    }
                },
                "required": []
            }
        ))
    
    if settings.enable_document_generation:
        tools.append(Tool(
            name="analyze_document",
            description=(
                "Analyze legal documents such as contracts, petitions, affidavits, etc. "
                "Extracts key information, identifies potential issues, and suggests improvements. "
                "Supports PDF, DOCX, and text formats."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "document_path": {
                        "type": "string",
                        "description": "Path to the document file to analyze"
                    },
                    "document_type": {
                        "type": "string",
                        "enum": ["petition", "affidavit", "contract", "agreement", "notice", "other"],
                        "description": "Type of legal document"
                    },
                    "analysis_type": {
                        "type": "string",
                        "enum": ["summary", "issues", "compliance", "full"],
                        "description": "Type of analysis to perform",
                        "default": "full"
                    }
                },
                "required": ["document_path", "document_type"]
            }
        ))
    
    if settings.enable_legal_research:
        tools.append(Tool(
            name="legal_research",
            description=(
                "Conduct comprehensive legal research on specific topics, statutes, or legal questions. "
                "Provides detailed analysis with references to relevant case laws, statutes, "
                "and legal commentary."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "research_query": {
                        "type": "string",
                        "description": "The legal question or topic to research"
                    },
                    "research_depth": {
                        "type": "string",
                        "enum": ["brief", "detailed", "comprehensive"],
                        "description": "Depth of research required",
                        "default": "detailed"
                    },
                    "include_statutes": {
                        "type": "boolean",
                        "description": "Include relevant statutory provisions",
                        "default": True
                    },
                    "include_case_laws": {
                        "type": "boolean",
                        "description": "Include relevant case law citations",
                        "default": True
                    }
                },
                "required": ["research_query"]
            }
        ))
    
    if settings.enable_deep_research:
        tools.append(Tool(
            name="deep_research",
            description=(
                "Conduct deep legal research using AI-powered web crawling of Indian legal sources. "
                "Automatically searches IndianKanoon and other legal databases, scrapes relevant "
                "judgments and statutes, and synthesizes a comprehensive research report. "
                "More thorough than legal_research — use when you need real, cited sources."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "research_query": {
                        "type": "string",
                        "description": "The legal question or topic to research"
                    },
                    "research_depth": {
                        "type": "string",
                        "enum": ["brief", "detailed", "comprehensive"],
                        "description": "Depth of research: brief (fast), detailed (default), comprehensive (thorough)",
                        "default": "detailed"
                    },
                    "include_statutes": {
                        "type": "boolean",
                        "description": "Include relevant statutory provisions",
                        "default": True
                    },
                    "include_case_laws": {
                        "type": "boolean",
                        "description": "Include relevant case law citations",
                        "default": True
                    }
                },
                "required": ["research_query"]
            }
        ))

    # Additional utility tools
    tools.extend([
        Tool(
            name="draft_legal_notice",
            description=(
                "Draft a legal notice based on provided facts and requirements. "
                "Generates a professionally formatted legal notice following Indian legal standards."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "notice_type": {
                        "type": "string",
                        "enum": ["demand", "cease_desist", "termination", "breach", "defamation", "other"],
                        "description": "Type of legal notice"
                    },
                    "facts": {
                        "type": "string",
                        "description": "Factual background and circumstances"
                    },
                    "relief_sought": {
                        "type": "string",
                        "description": "The remedy or action demanded"
                    },
                    "sender_details": {
                        "type": "object",
                        "description": "Details of the sender/client"
                    },
                    "recipient_details": {
                        "type": "object",
                        "description": "Details of the recipient"
                    }
                },
                "required": ["notice_type", "facts", "relief_sought"]
            }
        ),
        Tool(
            name="check_limitation",
            description=(
                "Check the limitation period for filing a case under Indian law. "
                "Calculates time limits based on the Limitation Act, 1963 and provides relevant sections."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "case_type": {
                        "type": "string",
                        "description": "Type of case or cause of action"
                    },
                    "cause_of_action_date": {
                        "type": "string",
                        "format": "date",
                        "description": "Date when cause of action arose (YYYY-MM-DD)"
                    },
                    "special_circumstances": {
                        "type": "string",
                        "description": "Any special circumstances that might affect limitation"
                    }
                },
                "required": ["case_type", "cause_of_action_date"]
            }
        )
    ])
    
    return tools


async def execute_tool(name: str, arguments: Dict[str, Any]) -> str:
    """Execute a tool and return the result"""
    logger.info(f"Executing tool: {name} with arguments: {arguments}")
    
    try:
        if name == "search_precedents":
            return await search_precedents(**arguments)
        
        elif name == "find_case_laws":
            return await find_case_laws(**arguments)
        
        elif name == "analyze_document":
            return await analyze_legal_document(**arguments)
        
        elif name == "legal_research":
            return await conduct_legal_research(**arguments)

        elif name == "deep_research":
            return await deep_research(**arguments)

        elif name == "draft_legal_notice":
            from src.tools.document_drafter import draft_notice
            return await draft_notice(**arguments)
        
        elif name == "check_limitation":
            from src.tools.limitation_checker import check_limitation_period
            return await check_limitation_period(**arguments)
        
        else:
            raise ValueError(f"Unknown tool: {name}")
    
    except Exception as e:
        logger.error(f"Error executing tool {name}: {str(e)}", exc_info=True)
        raise


# API Endpoints
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "server": settings.mcp_server_name,
        "version": settings.mcp_server_version,
        "type": "http-mcp-server"
    }


@app.get("/")
async def root():
    """Root endpoint with server information"""
    return {
        "message": "Wakalat-AI HTTP MCP Server",
        "version": settings.mcp_server_version,
        "endpoints": {
            "health": "/health",
            "tools": "/tools",
            "tools_execute": "/tools/execute",
            "sse": "/sse",
            "messages": "/messages/",
            "docs": "/docs"
        },
        "description": "HTTP-based MCP server for Indian legal assistant tools"
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


# WebSocket endpoint for real-time communication
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time MCP communication"""
    await websocket.accept()
    logger.info("WebSocket connection established")
    
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            message = json.loads(data)
            
            if message.get("type") == "tool_call":
                tool_name = message.get("name")
                arguments = message.get("arguments", {})
                
                try:
                    result = await execute_tool(tool_name, arguments)
                    response = {
                        "type": "tool_response",
                        "success": True,
                        "result": result
                    }
                except Exception as e:
                    response = {
                        "type": "tool_response",
                        "success": False,
                        "error": str(e)
                    }
                
                await websocket.send_text(json.dumps(response))
            
            elif message.get("type") == "list_tools":
                tools = get_available_tools()
                response = {
                    "type": "tools_list",
                    "tools": [tool.dict() for tool in tools]
                }
                await websocket.send_text(json.dumps(response))
            
            else:
                await websocket.send_text(json.dumps({
                    "type": "error",
                    "message": "Unknown message type"
                }))
                
    except WebSocketDisconnect:
        logger.info("WebSocket client disconnected")
    except Exception as e:
        logger.error(f"WebSocket error: {str(e)}")


def main():
    """
    Main entry point for the HTTP MCP server
    """
    logger.info(f"Starting HTTP MCP Server: {settings.mcp_server_name} v{settings.mcp_server_version}")
    logger.info(f"Server will be available at: http://localhost:{settings.mcp_server_port}")
    logger.info(f"API Documentation: http://localhost:{settings.mcp_server_port}/docs")
    
    try:
        config = uvicorn.Config(
            app=app,
            host="0.0.0.0",
            port=settings.mcp_server_port,
            log_level=settings.log_level.lower(),
            reload=False,
            timeout_keep_alive=settings.tool_execution_timeout,
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