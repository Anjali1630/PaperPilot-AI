"""Pydantic request/response schemas."""
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, EmailStr, Field


# ---------- Auth ----------
class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=64)
    email: EmailStr
    password: str = Field(..., min_length=6)
    full_name: Optional[str] = None


class UserLogin(BaseModel):
    username: str
    password: str


class UserOut(BaseModel):
    id: int
    username: str
    email: str
    full_name: Optional[str]
    dark_mode: bool
    summary_length_pref: str
    created_at: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut


# ---------- Settings ----------
class SettingsUpdate(BaseModel):
    dark_mode: Optional[bool] = None
    summary_length_pref: Optional[str] = None
    full_name: Optional[str] = None


# ---------- Papers ----------
class PaperOut(BaseModel):
    id: int
    filename: str
    title: Optional[str]
    authors: Optional[str]
    abstract: Optional[str]
    status: str
    is_analyzed: bool
    difficulty_score: Optional[float]
    difficulty_label: Optional[str]
    estimated_reading_minutes: Optional[int]
    created_at: datetime

    class Config:
        from_attributes = True


class PaperDetail(PaperOut):
    sections_json: Optional[str]
    executive_summary: Optional[str]
    standard_summary: Optional[str]
    detailed_summary: Optional[str]
    simplified_explanation: Optional[str]
    key_contributions: Optional[str]
    research_gaps: Optional[str]
    future_scope: Optional[str]
    methodology_json: Optional[str]
    keywords_json: Optional[str]
    flashcards_json: Optional[str]
    viva_questions_json: Optional[str]
    ppt_outline_json: Optional[str]
    citations_json: Optional[str]
    error_message: Optional[str]


# ---------- Chat ----------
class ChatRequest(BaseModel):
    question: str


class ChatMessageOut(BaseModel):
    id: int
    role: str
    content: str
    created_at: datetime

    class Config:
        from_attributes = True


# ---------- Compare ----------
class CompareRequest(BaseModel):
    paper_ids: List[int] = Field(..., min_items=2, max_items=5)


# ---------- Dashboard ----------
class DashboardStats(BaseModel):
    total_papers: int
    papers_summarized: int
    avg_reading_minutes_saved: float
    recent_uploads: List[PaperOut]
    top_keywords: List[Dict[str, Any]]
    recent_activity: List[Dict[str, Any]]
