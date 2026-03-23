"""
HTTP MCP Server Implementation for Wakalat-AI
Provides the same tools as stdio server but over HTTP/WebSocket/SSE
Includes JWT authentication and MCP SSE transport for Claude Code integration
"""
import asyncio
import json
from typing import Any, Dict, List, Optional
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from starlette.requests import Request
import uvicorn

from mcp.server.sse import SseServerTransport
from src.server import app as mcp_app  # MCP Server instance for SSE transport
from src.config import settings
from src.auth import create_access_token, get_current_user, verify_token_from_header
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
    description="HTTP MCP Server for Legal Assistant Tools with JWT Auth and SSE MCP Transport",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# SSE transport for MCP protocol over HTTP
sse_transport = SseServerTransport("/messages/")


@app.get("/sse")
async def handle_sse(request: Request):
    """SSE endpoint for MCP protocol communication (used by SSEClientTransport)"""
    # Verify auth — token must be passed via query param or header
    auth_header = request.headers.get("authorization")
    if auth_header:
        user = verify_token_from_header(auth_header)
        logger.info(f"[{user['sub']}] SSE MCP connection established")

    async with sse_transport.connect_sse(
        request.scope, request.receive, request._send
    ) as (read_stream, write_stream):
        await mcp_app.run(
            read_stream,
            write_stream,
            mcp_app.create_initialization_options(),
        )


app.mount("/messages/", app=sse_transport.handle_post_message)


# ── Pydantic models ──────────────────────────────────────────────────────────

class TokenRequest(BaseModel):
    email: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    email: str


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


# ── MCP Tool definitions ─────────────────────────────────────────────────────

def get_available_tools() -> List[Tool]:
    """Get list of available MCP tools"""
    tools = []

    if settings.enable_precedent_search:
        tools.append(Tool(
            name="search_precedents",
            description=(
                "Indian Kanoon precedent search (api.indiankanoon.org when INDIANKANOON_API_TOKEN is set). "
                "USE WHEN the user wants judgments, comparable cases, how courts treated an issue, or "
                "issue-based research—not a known citation. Prefer over legal_research when finding "
                "real cases is the main goal. DO NOT USE for a specific citation or party lookup "
                "(use find_case_laws), for uploaded document review (use analyze_document), or as a "
                "substitute for deep_research when the user explicitly wants exhaustive multi-source "
                "crawling. Query syntax: phrase quotes, ANDD/ORR/NOTT, IK filters per "
                "https://api.indiankanoon.org/documentation/ ; jurisdiction maps to supremecourt/highcourts."
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
                        "description": "Maximum number of results to return (default 5)",
                        "default": 5
                    }
                },
                "required": ["query"]
            }
        ))

    if settings.enable_case_law_search:
        tools.append(Tool(
            name="find_case_laws",
            description=(
                "Retrieve a specific judgment or case by citation, party name, or legal provision reference. "
                "USE WHEN the user names a case, citation, party, or asks to pull up a particular decision. "
                "DO NOT USE for open-ended 'cases on topic X' searches—use search_precedents. "
                "DO NOT USE for general legal explanations without a target case—use legal_research."
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
                "Analyze a legal document file (contracts, petitions, affidavits, notices). "
                "USE WHEN the user provides or refers to a document path and wants extraction, issues, "
                "compliance, or revision guidance. DO NOT USE for pure legal Q&A without a document "
                "(use legal_research or search_precedents as appropriate)."
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
                "LLM-based synthesis on Indian legal topics: statutes, tests, elements, procedure, and "
                "doctrine. USE WHEN the user needs structured legal analysis or statutory framework and "
                "judgment retrieval is secondary. Prefer search_precedents first when the priority is "
                "finding comparable Supreme Court or High Court cases. Prefer deep_research (if available) "
                "when the user wants maximum source-backed crawling and citations. Do not call both "
                "legal_research and deep_research for the same narrow question in one turn unless the user "
                "asks for two distinct outputs."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "research_query": {
                        "type": "string",
                        "description": "Focused legal question or topic (short phrase or one sentence preferred)"
                    },
                    "research_depth": {
                        "type": "string",
                        "enum": ["brief", "detailed", "comprehensive"],
                        "description": (
                            "brief = quick overview; detailed = default balanced analysis; "
                            "comprehensive = deepest (slower, timeout risk—use sparingly). "
                            "Prefer brief or detailed unless the user explicitly needs maximum depth."
                        ),
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
                "Heavyweight research: crawls Indian legal sources (e.g. Indian Kanoon), gathers real "
                "judgments and statutes, and synthesizes a cited report. USE WHEN the user asks for the "
                "most thorough, source-backed answer, a research memo, or exhaustive treatment—not for "
                "a quick statute recap (legal_research brief) or a single known citation (find_case_laws). "
                "Slower than legal_research; prefer legal_research for fast doctrine-only explanations "
                "unless source-grounding is explicitly required."
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
                "Draft a formal legal notice (demand, cease and desist, termination, breach, defamation). "
                "USE ONLY when the user explicitly wants notice text drafted from facts. "
                "DO NOT USE for general legal research or precedent search."
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
                "Compute limitation under the Limitation Act, 1963 from case type and cause-of-action date. "
                "USE WHEN the user asks about filing deadlines, limitation, or whether a claim may be barred. "
                "DO NOT USE for unrelated legal research without a limitation question."
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


# ── Public endpoints (no auth) ───────────────────────────────────────────────

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
            "auth_token": "POST /auth/token",
            "tools": "/tools (auth required)",
            "tools_execute": "POST /tools/execute (auth required)",
            "mcp_sse": "/sse (auth required, for Claude Code)",
            "docs": "/docs"
        },
        "description": "HTTP-based MCP server for Indian legal assistant tools"
    }


@app.post("/auth/token", response_model=TokenResponse)
async def generate_token(request: TokenRequest):
    """Generate an access token for the given email. Use this token to access all protected endpoints."""
    if not request.email or "@" not in request.email:
        raise HTTPException(status_code=400, detail="Valid email is required")

    token = create_access_token(request.email)
    return TokenResponse(
        access_token=token,
        email=request.email,
    )


# ── Protected endpoints (auth required) ──────────────────────────────────────

@app.get("/tools", response_model=ListToolsResponse)
async def list_tools(user: dict = Depends(get_current_user)):
    """List all available tools (auth required)"""
    tools = get_available_tools()
    logger.info(f"[{user['sub']}] Listed {len(tools)} available tools")
    return ListToolsResponse(tools=tools)


@app.post("/tools/execute", response_model=ToolResponse)
async def execute_tool_endpoint(tool_call: ToolCall, user: dict = Depends(get_current_user)):
    """Execute a specific tool (auth required)"""
    try:
        logger.info(f"[{user['sub']}] Executing tool: {tool_call.name}")
        result = await execute_tool(tool_call.name, tool_call.arguments)
        return ToolResponse(success=True, result=result)
    except Exception as e:
        logger.error(f"Tool execution failed: {str(e)}")
        return ToolResponse(success=False, error=str(e))


@app.get("/tools/{tool_name}")
async def get_tool_info(tool_name: str, user: dict = Depends(get_current_user)):
    """Get information about a specific tool (auth required)"""
    tools = get_available_tools()
    tool = next((t for t in tools if t.name == tool_name), None)

    if not tool:
        raise HTTPException(status_code=404, detail=f"Tool '{tool_name}' not found")

    return tool



# NOTE: The SSE MCP transport is handled by SseServerTransport at the top of this file.
# GET /sse → handle_sse() uses sse_transport.connect_sse + mcp_app
# POST /messages/ → mounted via sse_transport.handle_post_message
# This properly implements the MCP SSE protocol so SSEClientTransport works correctly.


# ── WebSocket endpoint ────────────────────────────────────────────────────────

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time MCP communication"""
    await websocket.accept()
    logger.info("WebSocket connection established")

    try:
        while True:
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
    import os
    port = int(os.environ.get("PORT", settings.mcp_server_port))
    logger.info(f"Starting HTTP MCP Server: {settings.mcp_server_name} v{settings.mcp_server_version}")
    logger.info(f"Server will be available at: http://0.0.0.0:{port}")
    logger.info(f"API Documentation: http://0.0.0.0:{port}/docs")

    try:
        config = uvicorn.Config(
            app=app,
            host="0.0.0.0",
            port=port,
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
