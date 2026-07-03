"""
Full analysis pipeline orchestrator.

Runs every AI module against one paper and returns a dict of results ready
to be persisted on the Paper ORM row. Kept as a single function so
routes/papers_routes.py stays thin, and so the same pipeline can be re-used
by a background task queue in a future iteration if desired.
"""
import json
import logging
from typing import Dict

from app.ai import (
    summarizer, simplifier, keywords as kw_module, contributions as contrib_module,
    gaps as gaps_module, methodology as method_module, flashcards as flash_module,
    viva as viva_module, difficulty as diff_module, citations as cite_module,
    ppt_outline as ppt_module,
)
from app.utils.pdf_processor import extract_raw_text, extract_title_and_authors, segment_sections

logger = logging.getLogger("paperpilot.pipeline")

def run_full_analysis(filepath: str) -> Dict:
    raw_text = extract_raw_text(filepath)
    if not raw_text.strip():
        raise ValueError("No extractable text found in this PDF (it may be a scanned image without OCR).")

    title, authors = extract_title_and_authors(filepath, raw_text)
    sections = segment_sections(raw_text)
    abstract = sections.get("abstract", "")[:3000] or raw_text[:1500]

    safe_raw_text = " ".join(raw_text.split()[:4000])

    logger.info("Generating summaries...")
    summaries = summarizer.generate_summaries(raw_text)

    logger.info("Generating simplified explanation...")
    simplified = simplifier.generate_simplified_explanation(sections, raw_text)

    logger.info("Extracting keywords...")
    keywords = kw_module.extract_keywords(raw_text, top_n=20)

    logger.info("Extracting key contributions...")
    contributions = contrib_module.extract_key_contributions(sections)

    logger.info("Extracting research gaps and future scope...")
    gaps = gaps_module.extract_research_gaps(sections)
    future_scope = gaps_module.extract_future_scope(sections)

    logger.info("Extracting methodology breakdown...")
    methodology = method_module.extract_methodology(sections)

    logger.info("Generating flashcards...")
    flashcards = flash_module.generate_flashcards(safe_raw_text, keywords)

    logger.info("Generating viva questions...")
    viva_questions = viva_module.generate_viva_questions(
        title=title,
        keywords=[k["keyword"] for k in keywords],
        methodology=methodology,
        contributions=contributions,
        gaps=gaps,
    )

    logger.info("Computing difficulty score...")
    difficulty = diff_module.compute_difficulty(safe_raw_text)

    logger.info("Generating citations...")
    citations = cite_module.generate_citations(title, authors, safe_raw_text)

    logger.info("Generating PPT outline...")
    ppt_outline = ppt_module.generate_ppt_outline(
        title=title, authors=authors, sections=sections, summaries=summaries,
        contributions=contributions, methodology=methodology, gaps=gaps,
        future_scope=future_scope, keywords=keywords,
    )

    return {
        "title": title,
        "authors": json.dumps(authors),
        "abstract": abstract,
        "raw_text": raw_text,
        "sections_json": json.dumps(sections),
        "executive_summary": summaries["executive"],
        "standard_summary": summaries["standard"],
        "detailed_summary": summaries["detailed"],
        "simplified_explanation": simplified,
        "key_contributions": json.dumps(contributions),
        "research_gaps": json.dumps(gaps),
        "future_scope": json.dumps(future_scope),
        "methodology_json": json.dumps(methodology),
        "keywords_json": json.dumps(keywords),
        "flashcards_json": json.dumps(flashcards),
        "viva_questions_json": json.dumps(viva_questions),
        "ppt_outline_json": json.dumps(ppt_outline),
        "citations_json": json.dumps(citations),
        "difficulty_score": difficulty["score"],
        "difficulty_label": difficulty["label"],
        "estimated_reading_minutes": difficulty["reading_minutes"],
    }