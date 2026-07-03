"""
Database engine, session management, and ORM models for PaperPilot AI.

Uses SQLite for a zero-configuration, fully local, fully free persistence
layer. Schema is created automatically on startup (see main.py).
"""
from datetime import datetime

from sqlalchemy import (
    create_engine, Column, Integer, String, Text, DateTime, ForeignKey, Float, Boolean
)
from sqlalchemy.orm import declarative_base, sessionmaker, relationship

from app.config import settings

engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False} if settings.DATABASE_URL.startswith("sqlite") else {},
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(64), unique=True, index=True, nullable=False)
    email = Column(String(128), unique=True, index=True, nullable=False)
    hashed_password = Column(String(256), nullable=False)
    full_name = Column(String(128), nullable=True)
    dark_mode = Column(Boolean, default=False)
    summary_length_pref = Column(String(16), default="standard")  # short|standard|detailed
    created_at = Column(DateTime, default=datetime.utcnow)

    papers = relationship("Paper", back_populates="owner", cascade="all, delete-orphan")


class Paper(Base):
    __tablename__ = "papers"

    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    filename = Column(String(256), nullable=False)
    filepath = Column(String(512), nullable=False)

    title = Column(String(512), nullable=True)
    authors = Column(Text, nullable=True)  # JSON-encoded list
    abstract = Column(Text, nullable=True)

    raw_text = Column(Text, nullable=True)
    sections_json = Column(Text, nullable=True)  # JSON-encoded {section: text}

    executive_summary = Column(Text, nullable=True)
    standard_summary = Column(Text, nullable=True)
    detailed_summary = Column(Text, nullable=True)
    simplified_explanation = Column(Text, nullable=True)

    key_contributions = Column(Text, nullable=True)   # JSON list
    research_gaps = Column(Text, nullable=True)        # JSON list
    future_scope = Column(Text, nullable=True)         # JSON list
    methodology_json = Column(Text, nullable=True)     # JSON dict
    keywords_json = Column(Text, nullable=True)        # JSON list
    flashcards_json = Column(Text, nullable=True)      # JSON list of {q,a}
    viva_questions_json = Column(Text, nullable=True)  # JSON dict by difficulty
    ppt_outline_json = Column(Text, nullable=True)     # JSON list of slides
    citations_json = Column(Text, nullable=True)       # JSON dict {apa, ieee, mla, chicago}

    difficulty_score = Column(Float, nullable=True)
    difficulty_label = Column(String(32), nullable=True)
    estimated_reading_minutes = Column(Integer, nullable=True)

    is_analyzed = Column(Boolean, default=False)
    status = Column(String(32), default="uploaded")  # uploaded|processing|analyzed|failed
    error_message = Column(Text, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    owner = relationship("User", back_populates="papers")
    chat_messages = relationship("ChatMessage", back_populates="paper", cascade="all, delete-orphan")


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, index=True)
    paper_id = Column(Integer, ForeignKey("papers.id"), nullable=False)
    role = Column(String(16), nullable=False)  # user|assistant
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    paper = relationship("Paper", back_populates="chat_messages")


class Comparison(Base):
    __tablename__ = "comparisons"

    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    paper_ids_json = Column(Text, nullable=False)  # JSON list of paper ids
    result_json = Column(Text, nullable=False)     # JSON comparison result
    created_at = Column(DateTime, default=datetime.utcnow)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    Base.metadata.create_all(bind=engine)
