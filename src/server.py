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
from src.tools.precedent_search import search_precedents
from src.tools.case_law_finder import find_case_laws
from src.tools.document_analyzer import analyze_legal_document
from src.tools.legal_research import conduct_legal_research
from src.tools.deep_research import deep_research
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

        elif name == "deep_research":
            # Build a progress callback that sends MCP log notifications
            async def _progress_cb(current: int, total: int, message: str):
                try:
                    ctx = app.request_context
                    if ctx and ctx.session:
                        await ctx.session.send_log_message(
                            level="info", data=message
                        )
                except Exception:
                    pass  # best-effort; don't break the tool

            result = await deep_research(
                **arguments, progress_callback=_progress_cb
            )
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
    resources = [
        {
            "uri": "template://legal-notice",
            "name": "Legal Notice Template",
            "description": "Standard template for legal notices in India",
            "mimeType": "text/plain"
        },
        {
            "uri": "template://petition",
            "name": "Petition Template",
            "description": "Template for drafting petitions",
            "mimeType": "text/plain"
        },
        {
            "uri": "guide://ipc-sections",
            "name": "IPC Sections Guide",
            "description": "Quick reference for Indian Penal Code sections",
            "mimeType": "text/plain"
        },
        {
            "uri": "guide://crpc-sections",
            "name": "CrPC Sections Guide",
            "description": "Quick reference for Criminal Procedure Code sections",
            "mimeType": "text/plain"
        },
        {
            "uri": "guide://limitation-act",
            "name": "Limitation Act Reference",
            "description": "Reference guide for Limitation Act, 1963",
            "mimeType": "text/plain"
        }
    ]
    
    logger.info(f"Listed {len(resources)} available resources")
    return resources


@app.list_prompts()
async def list_prompts() -> list[dict]:
    """
    List available prompt templates for common legal tasks
    """
    prompts = [
        {
            "name": "analyze_case_strength",
            "description": "Analyze the strength of a legal case based on facts and evidence",
            "arguments": [
                {
                    "name": "facts",
                    "description": "Factual background of the case",
                    "required": True
                },
                {
                    "name": "evidence",
                    "description": "Available evidence",
                    "required": True
                }
            ]
        },
        {
            "name": "draft_arguments",
            "description": "Draft legal arguments for a case",
            "arguments": [
                {
                    "name": "case_type",
                    "description": "Type of case",
                    "required": True
                },
                {
                    "name": "facts",
                    "description": "Factual background",
                    "required": True
                },
                {
                    "name": "legal_issues",
                    "description": "Key legal issues",
                    "required": True
                }
            ]
        },
        {
            "name": "legal_opinion",
            "description": "Provide a legal opinion on a matter",
            "arguments": [
                {
                    "name": "query",
                    "description": "Legal query or situation",
                    "required": True
                }
            ]
        }
    ]
    
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
