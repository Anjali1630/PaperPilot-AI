"""
Research Gap Analysis + Future Scope extraction.

Same extractive-embedding-similarity technique as contributions.py, but
anchored on sentences describing limitations/open problems and, separately,
future-work statements. Pulling both from the same technique keeps the
whole "insight extraction" layer consistent, fast, and free of any paid API.
"""
from typing import Dict, List

import numpy as np

from app.ai.model_manager import get_embedder, get_spacy_model

GAP_ANCHORS = [
    "This method has limitations and does not work well in some cases.",
    "There remains an open problem or unresolved challenge in this area.",
    "Existing approaches fail to address this issue adequately.",
    "The dataset or evaluation used has certain constraints.",
]

GAP_CUES = ["limitation", "however", "does not", "fails to", "remains unclear",
            "challenge", "difficult", "still", "open problem", "future work",
            "not addressed", "insufficient", "lack of"]

FUTURE_ANCHORS = [
    "In future work, we plan to extend this method.",
    "Future research could explore additional improvements.",
    "We aim to investigate this further in upcoming work.",
]

FUTURE_CUES = ["future work", "future research", "we plan to", "we aim to",
               "could be extended", "further investigation", "in the future",
               "next step", "remains to be explored"]


def _sentences(text: str) -> List[str]:
    nlp = get_spacy_model()
    doc = nlp(text)
    return [s.text.strip() for s in doc.sents if 25 < len(s.text.strip()) < 400]


def _rank_by_anchors(sentences: List[str], anchors: List[str], cues: List[str], top_k: int) -> List[str]:
    if not sentences:
        return []
    embedder = get_embedder()
    anchor_vecs = embedder.encode(anchors, normalize_embeddings=True)
    sent_vecs = embedder.encode(sentences, normalize_embeddings=True)
    sim_scores = np.max(sent_vecs @ anchor_vecs.T, axis=1)
    cue_scores = np.array(
        [sum(1 for c in cues if c in s.lower()) for s in sentences], dtype=float
    )
    combined = sim_scores + 0.2 * cue_scores
    idx = np.argsort(-combined)[:top_k]
    idx = sorted(idx)
    seen, out = set(), []
    for i in idx:
        s = sentences[i].strip()
        if s not in seen:
            seen.add(s)
            out.append(s)
    return out


def extract_research_gaps(sections: Dict[str, str], top_k: int = 5) -> List[str]:
    text = " ".join([
        sections.get("discussion", ""),
        sections.get("conclusion", ""),
        sections.get("results", ""),
        sections.get("related_work", ""),
    ])
    return _rank_by_anchors(_sentences(text), GAP_ANCHORS, GAP_CUES, top_k)


def extract_future_scope(sections: Dict[str, str], top_k: int = 5) -> List[str]:
    text = " ".join([
        sections.get("future_work", ""),
        sections.get("conclusion", ""),
        sections.get("discussion", ""),
    ])
    return _rank_by_anchors(_sentences(text), FUTURE_ANCHORS, FUTURE_CUES, top_k)
