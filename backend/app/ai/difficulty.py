"""
Paper Difficulty Score.

Combines four measurable signals into a single 0-100 difficulty score:
  1. Readability (Flesch Reading Ease via `textstat`, inverted so higher = harder)
  2. Vocabulary complexity (fraction of long/rare words, avg word length)
  3. Mathematical complexity (density of equations/symbols/numeric notation)
  4. Technical term density (count of domain acronyms and jargon-like tokens)

This is a transparent, explainable scoring function (not a black-box call),
so it's easy to justify in a viva/interview.
"""
import re
from typing import Dict

import textstat

MATH_SYMBOL_RE = re.compile(r"[=∑∫√≤≥≠±∞∂∇×÷^_{}\\]|\b\d+\.\d+\b")
ACRONYM_RE = re.compile(r"\b[A-Z]{2,6}\b")


def _readability_component(text: str) -> float:
    try:
        flesch = textstat.flesch_reading_ease(text)
    except Exception:
        flesch = 50.0
    flesch = max(0.0, min(100.0, flesch))
    return 100.0 - flesch  # invert: lower Flesch score == harder to read


def _vocabulary_component(text: str) -> float:
    words = re.findall(r"[A-Za-z]{2,}", text)
    if not words:
        return 0.0
    long_words = [w for w in words if len(w) >= 9]
    avg_len = sum(len(w) for w in words) / len(words)
    long_ratio = len(long_words) / len(words)
    # Normalize: avg word length ~4-9, long word ratio ~0-0.25 typical range
    score = (min(avg_len, 9) / 9) * 50 + (min(long_ratio, 0.25) / 0.25) * 50
    return min(score, 100.0)


def _math_component(text: str) -> float:
    matches = MATH_SYMBOL_RE.findall(text)
    density = len(matches) / max(len(text.split()), 1)
    # density of ~0.02 (1 symbol per 50 words) treated as high-math paper
    return min(density / 0.02, 1.0) * 100


def _technical_density_component(text: str) -> float:
    words = text.split()
    if not words:
        return 0.0
    acronyms = ACRONYM_RE.findall(text)
    density = len(acronyms) / len(words)
    return min(density / 0.03, 1.0) * 100


def compute_difficulty(full_text: str) -> Dict:
    sample = full_text[:15000] if full_text else ""
    if not sample.strip():
        return {"score": 0.0, "label": "Unknown", "reading_minutes": 0}

    readability = _readability_component(sample)
    vocabulary = _vocabulary_component(sample)
    math_complexity = _math_component(sample)
    technical_density = _technical_density_component(sample)

    score = (
        0.35 * readability +
        0.25 * vocabulary +
        0.25 * math_complexity +
        0.15 * technical_density
    )
    score = round(min(max(score, 0.0), 100.0), 1)

    if score < 30:
        label = "Beginner Friendly"
    elif score < 55:
        label = "Intermediate"
    elif score < 75:
        label = "Advanced"
    else:
        label = "Expert / Research-Level"

    word_count = len(full_text.split())
    reading_minutes = max(1, round(word_count / 200))  # ~200 wpm average technical reading speed

    return {
        "score": score,
        "label": label,
        "reading_minutes": reading_minutes,
        "components": {
            "readability": round(readability, 1),
            "vocabulary_complexity": round(vocabulary, 1),
            "mathematical_complexity": round(math_complexity, 1),
            "technical_term_density": round(technical_density, 1),
        },
    }
