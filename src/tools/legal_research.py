"""
Legal Research Tool
Conducts comprehensive legal research on topics using LLM
"""
import json
from typing import Literal
from src.tools.llm import call_llm
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


async def conduct_legal_research(
    research_query: str,
    research_depth: Literal["brief", "detailed", "comprehensive"] = "detailed",
    include_statutes: bool = True,
    include_case_laws: bool = True
) -> str:
    """
    Conduct legal research on a topic using LLM.

    Args:
        research_query: The legal question or topic
        research_depth: Depth of research
        include_statutes: Include statutory provisions
        include_case_laws: Include case law citations

    Returns:
        JSON string with research results
    """
    logger.info(f"Conducting legal research: {research_query}, depth: {research_depth}")

    try:
        depth_instructions = {
            "brief": "Provide a concise 2-3 paragraph overview covering the key legal position and most important provisions.",
            "detailed": (
                "Provide a thorough analysis including:\n"
                "1. Executive summary\n"
                "2. Relevant statutory provisions with section numbers\n"
                "3. Key case law principles\n"
                "4. Practical implications\n"
                "5. Conclusion and recommendations"
            ),
            "comprehensive": (
                "Provide an exhaustive legal research memo including:\n"
                "1. Executive summary\n"
                "2. Complete statutory framework with all relevant Acts and sections\n"
                "3. Detailed case law analysis with citations and ratio decidendi\n"
                "4. Conflicting judicial opinions if any\n"
                "5. Historical evolution of the legal position\n"
                "6. Practical implications and procedural guidance\n"
                "7. Recent amendments or pending bills\n"
                "8. Conclusion with specific recommendations"
            ),
        }

        sections_to_include = []
        if include_statutes:
            sections_to_include.append("- Relevant statutory provisions (Act name, section numbers, and their text/interpretation)")
        if include_case_laws:
            sections_to_include.append("- Relevant case laws (case name, citation, court, year, key principles, and how they apply)")

        include_text = "\n".join(sections_to_include) if sections_to_include else "- General legal analysis"

        prompt = (
            f"You are a senior Indian legal researcher. Conduct thorough legal research on the following query.\n\n"
            f"RESEARCH QUERY: {research_query}\n\n"
            f"DEPTH: {research_depth}\n"
            f"INSTRUCTIONS: {depth_instructions[research_depth]}\n\n"
            f"MUST INCLUDE:\n{include_text}\n\n"
            f"IMPORTANT:\n"
            f"- Focus on Indian law (IPC, CrPC, CPC, Constitution, specific Acts)\n"
            f"- Cite specific sections and case laws with proper citations (AIR, SCC, etc.)\n"
            f"- Distinguish between Supreme Court and High Court rulings\n"
            f"- Note any recent amendments or changes in legal position\n"
            f"- Provide practical, actionable guidance\n\n"
            f"Provide your research in a clear, structured format."
        )

        research_text = await call_llm(prompt)

        result = {
            "research_query": research_query,
            "research_depth": research_depth,
            "include_statutes": include_statutes,
            "include_case_laws": include_case_laws,
            "research_results": research_text,
            "disclaimer": "This research is AI-generated. Always verify citations and consult qualified legal counsel.",
        }

        return json.dumps(result, indent=2)

    except Exception as e:
        logger.error(f"Error conducting legal research: {str(e)}", exc_info=True)
        return json.dumps({"error": str(e)}, indent=2)


