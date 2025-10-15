"""Shared MCP catalog definitions for tools, resources, and prompts."""

from typing import Any, Dict, List


def get_resources() -> List[Dict[str, Any]]:
    """Return static MCP resource metadata."""

    return [
        {
            "uri": "template://legal-notice",
            "name": "Legal Notice Template",
            "description": "Standard template for legal notices in India",
            "mimeType": "text/plain",
        },
        {
            "uri": "template://petition",
            "name": "Petition Template",
            "description": "Template for drafting petitions",
            "mimeType": "text/plain",
        },
        {
            "uri": "guide://ipc-sections",
            "name": "IPC Sections Guide",
            "description": "Quick reference for Indian Penal Code sections",
            "mimeType": "text/plain",
        },
        {
            "uri": "guide://crpc-sections",
            "name": "CrPC Sections Guide",
            "description": "Quick reference for Criminal Procedure Code sections",
            "mimeType": "text/plain",
        },
        {
            "uri": "guide://limitation-act",
            "name": "Limitation Act Reference",
            "description": "Reference guide for Limitation Act, 1963",
            "mimeType": "text/plain",
        },
    ]


def get_prompts() -> List[Dict[str, Any]]:
    """Return static MCP prompt template metadata."""

    return [
        {
            "name": "analyze_case_strength",
            "description": "Analyze the strength of a legal case based on facts and evidence",
            "arguments": [
                {
                    "name": "facts",
                    "description": "Factual background of the case",
                    "required": True,
                },
                {
                    "name": "evidence",
                    "description": "Available evidence",
                    "required": True,
                },
            ],
        },
        {
            "name": "draft_arguments",
            "description": "Draft legal arguments for a case",
            "arguments": [
                {
                    "name": "case_type",
                    "description": "Type of case",
                    "required": True,
                },
                {
                    "name": "facts",
                    "description": "Factual background",
                    "required": True,
                },
                {
                    "name": "legal_issues",
                    "description": "Key legal issues",
                    "required": True,
                },
            ],
        },
        {
            "name": "legal_opinion",
            "description": "Provide a legal opinion on a matter",
            "arguments": [
                {
                    "name": "query",
                    "description": "Legal query or situation",
                    "required": True,
                }
            ],
        },
    ]


