"""
Case and Legal Document Models
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


class Party(BaseModel):
    """Model for a party in a legal case"""
    name: str
    party_type: str  # petitioner, respondent, appellant, etc.
    address: Optional[str] = None
    advocate: Optional[str] = None


class CaseLaw(BaseModel):
    """Model for a case law/precedent"""
    case_name: str
    citation: str
    court: str
    year: int
    date_of_judgment: Optional[datetime] = None
    bench: Optional[str] = None
    judges: List[str] = Field(default_factory=list)
    summary: Optional[str] = None
    headnotes: List[str] = Field(default_factory=list)
    sections_involved: List[str] = Field(default_factory=list)
    precedents_cited: List[str] = Field(default_factory=list)
    full_text_url: Optional[str] = None
    pdf_url: Optional[str] = None
    relevance_score: Optional[float] = None


class LegalDocument(BaseModel):
    """Model for a legal document"""
    document_id: str
    document_type: str  # petition, affidavit, notice, etc.
    title: str
    file_path: str
    file_format: str  # pdf, docx, txt
    size_bytes: int
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    parties_involved: List[Party] = Field(default_factory=list)
    case_number: Optional[str] = None
    court: Optional[str] = None


class ResearchQuery(BaseModel):
    """Model for a legal research query"""
    query_id: str
    query_text: str
    query_type: str  # precedent_search, case_law, statute, general
    filters: dict = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.now)


class ResearchResult(BaseModel):
    """Model for research results"""
    query_id: str
    results: List[dict]
    total_found: int
    search_time_ms: float
    metadata: dict = Field(default_factory=dict)
