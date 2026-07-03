"""
PDF parsing utilities.

Extracts raw text using PyMuPDF (fitz) and then segments a research paper
into its logical sections (Abstract, Introduction, Methodology, Results,
Conclusion, References, ...) using heading-detection heuristics based on
font size / boldness plus common section-title regex matching. This is a
standard, dependency-light approach that works well across the variety of
templates found in IEEE / ACM / arXiv-style papers, without needing any
paid layout-analysis API.
"""
import re
from typing import Dict, List, Optional

import fitz  # PyMuPDF


SECTION_ALIASES = {
    "abstract": ["abstract"],
    "introduction": ["introduction", "background"],
    "related_work": ["related work", "literature review", "prior work"],
    "methodology": ["methodology", "method", "proposed method", "proposed system",
                     "materials and methods", "system design", "approach"],
    "experiments": ["experiments", "experimental setup", "experimental results", "implementation"],
    "results": ["results", "results and discussion", "evaluation", "performance analysis"],
    "discussion": ["discussion"],
    "conclusion": ["conclusion", "conclusions", "conclusion and future work", "summary"],
    "future_work": ["future work", "future scope"],
    "references": ["references", "bibliography"],
    "acknowledgment": ["acknowledgment", "acknowledgement", "acknowledgments"],
}

_HEADING_RE = re.compile(
    r"^\s*((?:\d{1,2}\.?\d*\.?)|(?:[IVXLC]{1,5}\.))?\s*([A-Za-z][A-Za-z\s\-:]{2,60})\s*$"
)


def extract_raw_text(filepath: str) -> str:
    """Extract full plain text from a PDF file."""
    doc = fitz.open(filepath)
    text_parts = []
    for page in doc:
        text_parts.append(page.get_text("text"))
    doc.close()
    return "\n".join(text_parts)


def extract_title_and_authors(filepath: str, raw_text: str) -> (Optional[str], List[str]):
    """
    Heuristically extract the paper title (largest font on first page) and
    author names (the text block immediately following the title, filtered
    with a light heuristic since author-list formats vary widely).
    """
    doc = fitz.open(filepath)
    title = None
    authors: List[str] = []

    if len(doc) > 0:
        page = doc[0]
        blocks = page.get_text("dict")["blocks"]
        spans = []
        for b in blocks:
            for line in b.get("lines", []):
                for span in line.get("spans", []):
                    txt = span.get("text", "").strip()
                    if txt:
                        spans.append((span["size"], txt))
        if spans:
            max_size = max(s[0] for s in spans)
            title_spans = [s[1] for s in spans if s[0] >= max_size - 0.5]
            title = " ".join(title_spans).strip()
            title = re.sub(r"\s+", " ", title)[:300]

            # Author heuristic: next largest cluster of short lines below the title
            candidate_size = sorted({s[0] for s in spans if s[0] < max_size}, reverse=True)
            if candidate_size:
                author_size = candidate_size[0]
                author_line = " ".join(s[1] for s in spans if abs(s[0] - author_size) < 0.5)
                # Split on common separators
                parts = re.split(r",|\band\b|;", author_line)
                authors = [p.strip() for p in parts if 2 < len(p.strip()) < 60]
    doc.close()

    if not title:
        # Fallback: first non-empty line of raw text
        for line in raw_text.splitlines():
            if line.strip():
                title = line.strip()[:300]
                break

    return title, authors[:10]


def segment_sections(raw_text: str) -> Dict[str, str]:
    """
    Split raw paper text into canonical sections using regex heading
    detection. Falls back gracefully: any text that can't be matched to a
    known heading is placed under 'body'.
    """
    lines = raw_text.splitlines()
    sections: Dict[str, List[str]] = {}
    current_key = "body"
    sections[current_key] = []

    for line in lines:
        stripped = line.strip()
        matched_key = _match_heading(stripped)
        if matched_key:
            current_key = matched_key
            sections.setdefault(current_key, [])
            continue
        sections.setdefault(current_key, []).append(line)

    return {k: "\n".join(v).strip() for k, v in sections.items() if "\n".join(v).strip()}


def _match_heading(line: str) -> Optional[str]:
    if not line or len(line) > 80:
        return None
    m = _HEADING_RE.match(line)
    if not m:
        return None
    candidate = m.group(2).strip().lower()
    for canonical, aliases in SECTION_ALIASES.items():
        for alias in aliases:
            if candidate == alias or candidate.startswith(alias):
                return canonical
    return None


def chunk_text(text: str, chunk_size: int = 800, overlap: int = 100) -> List[str]:
    """Split text into overlapping word-based chunks for embedding/RAG."""
    words = text.split()
    if not words:
        return []
    chunks = []
    step = max(chunk_size - overlap, 1)
    for i in range(0, len(words), step):
        chunk = " ".join(words[i:i + chunk_size])
        if chunk.strip():
            chunks.append(chunk)
        if i + chunk_size >= len(words):
            break
    return chunks
