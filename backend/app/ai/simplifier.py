"""
Simplified Technical Explanation.

Strategy (fully local, no paid LLM):
1. Take the abstract + introduction + conclusion (the sections that state
   *what* the paper does and *why*, as opposed to deep mathematical detail).
2. Run it through the local summarizer to compress it.
3. Apply readability-oriented rewriting heuristics:
   - Split long, comma-heavy sentences into shorter ones.
   - Expand acronyms the first time they appear, using acronym detection
     (regex for "Full Term (ACRONYM)" patterns found anywhere in the paper).
   - Strip inline citation clutter like "[12]" or "(Smith et al., 2020)"
     which add noise without meaning for a beginner reader.
"""
import re
from typing import Dict
from app.ai.summarizer import _summarize_chunk

CITATION_RE = re.compile(r"\[\d+(?:,\s*\d+)*\]|\((?:[A-Z][a-zA-Z\-]+(?:\s+et al\.)?,?\s*\d{4}[a-z]?)\)")
ACRONYM_DEF_RE = re.compile(r"([A-Z][a-zA-Z\-]+(?:\s+[A-Z][a-zA-Z\-]+){1,5})\s*\(([A-Z]{2,8})\)")

def _find_acronyms(text: str) -> Dict[str, str]:
    return {m.group(2): m.group(1) for m in ACRONYM_DEF_RE.finditer(text)}

def _split_long_sentences(text: str, max_words: int = 28) -> str:
    sentences = re.split(r"(?<=[.!?])\s+", text)
    rebuilt = []
    for s in sentences:
        words = s.split()
        if len(words) <= max_words:
            rebuilt.append(s)
            continue
        parts = re.split(r",\s+(?:which|and|but|so|because)\s+|;\s+", s)
        if len(parts) > 1:
            rebuilt.extend([p.strip().rstrip(",") + "." for p in parts if p.strip()])
        else:
            mid = len(words) // 2
            if mid == 0:
                mid = 1
            comma_idx = s.find(",", len(" ".join(words[:mid])))
            if comma_idx != -1:
                rebuilt.append(s[:comma_idx].strip() + ".")
                rebuilt.append(s[comma_idx + 1:].strip())
            else:
                rebuilt.append(s)
    return " ".join(rebuilt)

def generate_simplified_explanation(sections: Dict[str, str], full_text: str) -> str:
    source = " ".join([
        sections.get("abstract", ""),
        sections.get("introduction", ""),
        sections.get("conclusion", ""),
    ]).strip()
    
    if not source:
        source = full_text[:4000]
    if not source.strip():
        return ""
        
    safe_source = " ".join(source.split()[:500])

    compressed = _summarize_chunk(safe_source, max_len=260, min_len=120)
    compressed = CITATION_RE.sub("", compressed)
    compressed = re.sub(r"\s{2,}", " ", compressed).strip()
    simplified = _split_long_sentences(compressed)

    acronyms = _find_acronyms(full_text[:30000])
    if acronyms:
        glossary_lines = [f"- **{abbr}** stands for {full}." for abbr, full in list(acronyms.items())[:10]]
        glossary = "\n".join(glossary_lines)
        simplified = f"{simplified}\n\n**Glossary of terms used in this paper:**\n{glossary}"

    return simplified