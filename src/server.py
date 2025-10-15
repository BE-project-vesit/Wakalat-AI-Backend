"""
Main MCP Server Implementation for Wakalat-AI
Provides tools and resources for legal assistance to lawyers in India
"""
import asyncio
from typing import Any, Sequence
from mcp.server import Server
from mcp.types import (
    Tool,
    TextContent,
    ImageContent,
    EmbeddedResource,
    LoggingLevel
)
from mcp.server.stdio import stdio_server

from src.config import settings
from src.models.mcp_catalog import get_prompts, get_resources
from src.tools.precedent_search import search_precedents
from src.tools.case_law_finder import find_case_laws
from src.tools.document_analyzer import analyze_legal_document
from src.tools.legal_research import conduct_legal_research
from src.utils.logger import setup_logger

# Initialize logger
logger = setup_logger(__name__)

# Initialize MCP server
app = Server(settings.mcp_server_name)


@app.list_tools()
async def list_tools() -> list[Tool]:
    """
    List all available tools for the MCP server
    These tools are designed to assist lawyers with case preparation
    """
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
    
    logger.info(f"Listed {len(tools)} available tools")
    return tools


@app.call_tool()
async def call_tool(name: str, arguments: Any) -> Sequence[TextContent | ImageContent | EmbeddedResource]:
    """
    Handle tool calls from the MCP client
    Routes requests to appropriate tool handlers
    """
    logger.info(f"Tool called: {name} with arguments: {arguments}")
    
    try:
        if name == "search_precedents":
            result = await search_precedents(**arguments)
            return [TextContent(type="text", text=result)]
        
        elif name == "find_case_laws":
            result = await find_case_laws(**arguments)
            return [TextContent(type="text", text=result)]
        
        elif name == "analyze_document":
            result = await analyze_legal_document(**arguments)
            return [TextContent(type="text", text=result)]
        
        elif name == "legal_research":
            result = await conduct_legal_research(**arguments)
            return [TextContent(type="text", text=result)]
        
        elif name == "draft_legal_notice":
            from src.tools.document_drafter import draft_notice
            result = await draft_notice(**arguments)
            return [TextContent(type="text", text=result)]
        
        elif name == "check_limitation":
            from src.tools.limitation_checker import check_limitation_period
            result = await check_limitation_period(**arguments)
            return [TextContent(type="text", text=result)]
        
        else:
            error_msg = f"Unknown tool: {name}"
            logger.error(error_msg)
            return [TextContent(type="text", text=error_msg)]
    
    except Exception as e:
        error_msg = f"Error executing tool {name}: {str(e)}"
        logger.error(error_msg, exc_info=True)
        return [TextContent(type="text", text=error_msg)]


@app.list_resources()
async def list_resources() -> list[dict]:
    """
    List available resources (templates, guidelines, etc.)
    """
    resources = get_resources()
    logger.info(f"Listed {len(resources)} available resources")
    return resources


@app.list_prompts()
async def list_prompts() -> list[dict]:
    """
    List available prompt templates for common legal tasks
    """
    prompts = get_prompts()
    logger.info(f"Listed {len(prompts)} available prompts")
    return prompts


async def main():
    """
    Main entry point for the MCP server
    """
    logger.info(f"Starting {settings.mcp_server_name} v{settings.mcp_server_version}")
    
    try:
        # Run the server using stdio transport
        async with stdio_server() as (read_stream, write_stream):
            await app.run(
                read_stream,
                write_stream,
                app.create_initialization_options()
            )
    except KeyboardInterrupt:
        logger.info("Server shutdown requested")
    except Exception as e:
        logger.error(f"Server error: {e}", exc_info=True)
        raise


def cli_main():
    """
    CLI entry point for uv/pip installations
    """
    asyncio.run(main())


if __name__ == "__main__":
    cli_main()
