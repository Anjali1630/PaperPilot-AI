"""
Key Contributions extraction.

Approach: extractive NLP over the Abstract + Introduction + Conclusion.
Sentences are scored by:
  1. Presence of "contribution cue phrases" (novel, propose, introduce, ...)
  2. Semantic similarity to a fixed set of contribution-describing anchor
     sentences, computed with the local sentence-transformer embedding model.
This mirrors how a human skim-reader spots "what's new here" sentences,
without requiring any generative/paid LLM call.
"""
from typing import Dict, List

import numpy as np

from app.ai.model_manager import get_embedder, get_spacy_model

CUE_PHRASES = [
    "we propose", "we present", "we introduce", "we develop", "this paper proposes",
    "our contribution", "novel", "for the first time", "we design", "we achieve",
    "outperforms", "state-of-the-art", "we demonstrate", "our approach", "our method",
]

ANCHOR_SENTENCES = [
    "This paper introduces a new method that improves on previous work.",
    "The main contribution of this research is a novel algorithm or system.",
    "We achieve better performance than existing approaches on a benchmark.",
]


def _sentences(text: str) -> List[str]:
    nlp = get_spacy_model()
    doc = nlp(text)
    return [s.text.strip() for s in doc.sents if 25 < len(s.text.strip()) < 400]


def _cue_score(sentence: str) -> int:
    lowered = sentence.lower()
    return sum(1 for cue in CUE_PHRASES if cue in lowered)


def extract_key_contributions(sections: Dict[str, str], top_k: int = 6) -> List[str]:
    source_text = " ".join([
        sections.get("abstract", ""),
        sections.get("introduction", ""),
        sections.get("conclusion", ""),
    ])
    sentences = _sentences(source_text)
    if not sentences:
        return []

    embedder = get_embedder()
    anchor_vecs = embedder.encode(ANCHOR_SENTENCES, normalize_embeddings=True)
    sent_vecs = embedder.encode(sentences, normalize_embeddings=True)

    sim_scores = np.max(sent_vecs @ anchor_vecs.T, axis=1)
    cue_scores = np.array([_cue_score(s) for s in sentences], dtype=float)

    combined = sim_scores + 0.15 * cue_scores
    ranked_idx = np.argsort(-combined)[:top_k]
    ranked_idx = sorted(ranked_idx)  # keep original reading order

    seen = set()
    contributions = []
    for i in ranked_idx:
        s = sentences[i].strip()
        if s not in seen:
            seen.add(s)
            contributions.append(s)
    return contributions
