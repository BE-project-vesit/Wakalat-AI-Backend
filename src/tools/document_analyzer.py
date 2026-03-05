"""
Document Analyzer Tool
Analyzes legal documents and provides insights using LLM
"""
import json
from typing import Literal
from pathlib import Path
from src.tools.llm import call_llm
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


def _extract_text_from_file(doc_path: Path) -> str:
    """Extract text from PDF, DOCX, or TXT files."""
    suffix = doc_path.suffix.lower()

    if suffix == ".txt":
        return doc_path.read_text(encoding="utf-8", errors="replace")

    if suffix == ".pdf":
        try:
            import pdfplumber
            text_parts = []
            with pdfplumber.open(doc_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text_parts.append(page_text)
            return "\n\n".join(text_parts)
        except ImportError:
            try:
                from PyPDF2 import PdfReader
                reader = PdfReader(str(doc_path))
                return "\n\n".join(
                    page.extract_text() or "" for page in reader.pages
                )
            except ImportError:
                return "[Error: Install pdfplumber or PyPDF2 to read PDF files]"

    if suffix in (".docx", ".doc"):
        try:
            from docx import Document
            doc = Document(str(doc_path))
            return "\n\n".join(p.text for p in doc.paragraphs if p.text.strip())
        except ImportError:
            return "[Error: Install python-docx to read DOCX files]"

    return doc_path.read_text(encoding="utf-8", errors="replace")


async def analyze_legal_document(
    document_path: str,
    document_type: Literal["petition", "affidavit", "contract", "agreement", "notice", "other"],
    analysis_type: Literal["summary", "issues", "compliance", "full"] = "full"
) -> str:
    """
    Analyze a legal document using LLM.

    Args:
        document_path: Path to the document file
        document_type: Type of legal document
        analysis_type: Type of analysis to perform

    Returns:
        JSON string with analysis results
    """
    logger.info(f"Analyzing document: {document_path}, type: {document_type}")

    try:
        doc_path = Path(document_path)

        if not doc_path.exists():
            return json.dumps({"error": f"Document not found: {document_path}"}, indent=2)

        # Extract text
        text = _extract_text_from_file(doc_path)
        if not text or text.startswith("[Error:"):
            return json.dumps({"error": f"Could not extract text: {text}"}, indent=2)

        # Truncate very long documents for LLM context
        max_chars = 12000
        truncated = len(text) > max_chars
        text_for_analysis = text[:max_chars] if truncated else text

        # Build analysis prompt
        analysis_instructions = {
            "summary": "Provide a concise summary with key points, parties involved, dates, and monetary amounts mentioned.",
            "issues": "Identify potential legal issues, missing elements, ambiguous clauses, and suggestions for improvement.",
            "compliance": "Check format compliance with Indian legal standards, verify required elements are present, and assess language quality.",
            "full": (
                "Provide a comprehensive analysis including:\n"
                "1. Summary with key points, parties, dates, amounts\n"
                "2. Potential legal issues and risks\n"
                "3. Missing or ambiguous elements\n"
                "4. Compliance with Indian legal standards\n"
                "5. Specific suggestions for improvement\n"
                "6. Relevant statutory references"
            ),
        }

        prompt = (
            f"You are a senior Indian legal analyst. Analyze the following {document_type} document.\n\n"
            f"Analysis type: {analysis_type}\n"
            f"Instructions: {analysis_instructions[analysis_type]}\n\n"
            f"DOCUMENT TEXT:\n{text_for_analysis}\n\n"
            f"{'[Document was truncated due to length]' if truncated else ''}\n"
            f"Provide your analysis in a clear, structured format with sections and bullet points."
        )

        # Call LLM
        analysis_text = await call_llm(prompt, max_tokens=2000)

        result = {
            "document_info": {
                "path": document_path,
                "type": document_type,
                "size_bytes": doc_path.stat().st_size,
                "format": doc_path.suffix,
                "truncated": truncated,
            },
            "analysis_type": analysis_type,
            "analysis": analysis_text,
            "disclaimer": "This analysis is AI-generated. Always verify with qualified legal counsel.",
        }

        return json.dumps(result, indent=2)

    except Exception as e:
        logger.error(f"Error analyzing document: {str(e)}", exc_info=True)
        return json.dumps({"error": str(e)}, indent=2)


