"""
Compare Multiple Research Papers (2-5 papers).

Builds comparison tables/lists from the already-computed per-paper analysis
fields (methodology, contributions, gaps, keywords) stored on each Paper
row — no re-analysis needed. Also computes a semantic "common objectives"
summary using embedding similarity between paper abstracts.
"""
import json
from typing import List, Dict

import numpy as np

from app.ai.model_manager import get_embedder


def _safe_json(value, default):
    if not value:
        return default
    try:
        return json.loads(value)
    except (json.JSONDecodeError, TypeError):
        return default


def _find_common_objective_terms(abstracts: List[str], top_n: int = 8) -> List[str]:
    """Find words/phrases that co-occur across most abstracts as a cheap proxy
    for shared objectives, without another paid API call."""
    from collections import Counter
    import re

    stop = set([
        "the", "a", "an", "of", "in", "to", "and", "for", "on", "with", "is",
        "are", "this", "that", "we", "our", "paper", "study", "using", "based",
    ])
    counters = []
    for text in abstracts:
        words = [w.lower() for w in re.findall(r"[A-Za-z]{4,}", text) if w.lower() not in stop]
        counters.append(set(words))

    if not counters:
        return []

    common = set.intersection(*counters) if len(counters) > 1 else counters[0]
    all_words = Counter()
    for text in abstracts:
        for w in re.findall(r"[A-Za-z]{4,}", text.lower()):
            if w in common:
                all_words[w] += 1
    return [w for w, _ in all_words.most_common(top_n)]


def compare_papers(papers: List) -> Dict:
    """`papers` is a list of ORM Paper objects, already analyzed."""
    table = []
    abstracts = []

    for p in papers:
        methodology = _safe_json(p.methodology_json, {})
        keywords = _safe_json(p.keywords_json, [])
        contributions = _safe_json(p.key_contributions, [])
        gaps = _safe_json(p.research_gaps, [])
        future_scope = _safe_json(p.future_scope, [])

        table.append({
            "paper_id": p.id,
            "title": p.title or p.filename,
            "algorithms": methodology.get("algorithms", []),
            "datasets": methodology.get("datasets", []),
            "evaluation_metrics": methodology.get("evaluation_metrics", []),
            "keywords": [k.get("keyword") for k in keywords[:8]],
            "contributions": contributions,
            "research_gaps": gaps,
            "future_directions": future_scope,
            "difficulty_score": p.difficulty_score,
            "difficulty_label": p.difficulty_label,
        })
        abstracts.append(p.abstract or "")

    common_terms = _find_common_objective_terms(abstracts)

    # Pairwise abstract similarity matrix (helps show how closely related the papers are)
    similarity_matrix = []
    if all(a.strip() for a in abstracts):
        embedder = get_embedder()
        vecs = embedder.encode(abstracts, normalize_embeddings=True)
        sim = vecs @ vecs.T
        similarity_matrix = sim.round(3).tolist()

    all_algorithms = sorted(set(a for row in table for a in row["algorithms"]))
    all_datasets = sorted(set(d for row in table for d in row["datasets"]))
    all_metrics = sorted(set(m for row in table for m in row["evaluation_metrics"]))

    return {
        "papers": table,
        "common_objective_terms": common_terms,
        "similarity_matrix": similarity_matrix,
        "algorithm_union": all_algorithms,
        "dataset_union": all_datasets,
        "metric_union": all_metrics,
    }
