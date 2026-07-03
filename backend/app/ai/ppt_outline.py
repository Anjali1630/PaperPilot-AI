"""Builds a 10-15 slide presentation outline from already-extracted analysis."""
from typing import Dict, List


def generate_ppt_outline(
    title: str,
    authors: List[str],
    sections: Dict[str, str],
    summaries: Dict[str, str],
    contributions: List[str],
    methodology: Dict,
    gaps: List[str],
    future_scope: List[str],
    keywords: List[Dict],
) -> List[Dict]:

    def bullets_from_text(text: str, max_bullets: int = 4, max_len: int = 140) -> List[str]:
        if not text:
            return []
        sentences = [s.strip() for s in text.replace("\n", " ").split(". ") if s.strip()]
        return [s[:max_len] + ("..." if len(s) > max_len else "") for s in sentences[:max_bullets]]

    slides = [
        {"slide_no": 1, "title": title or "Research Paper Title", "bullets": [
            ", ".join(authors[:5]) if authors else "Author(s) not detected",
        ], "type": "title_slide"},

        {"slide_no": 2, "title": "Background", "bullets": bullets_from_text(sections.get("introduction", ""), 4)},

        {"slide_no": 3, "title": "Problem Statement", "bullets": bullets_from_text(
            sections.get("abstract", "") or summaries.get("executive", ""), 3)},

        {"slide_no": 4, "title": "Literature Review", "bullets": bullets_from_text(sections.get("related_work", ""), 4)
            or ["Related work section not detected in the source PDF."]},

        {"slide_no": 5, "title": "Proposed Methodology", "bullets": methodology.get("pipeline_steps", [])[:4]
            or bullets_from_text(sections.get("methodology", ""), 4)},

        {"slide_no": 6, "title": "Algorithms & Models Used", "bullets": methodology.get("algorithms", ["Not explicitly detected"])},

        {"slide_no": 7, "title": "Dataset(s)", "bullets": methodology.get("datasets", ["Not explicitly detected"])},

        {"slide_no": 8, "title": "Evaluation Metrics", "bullets": methodology.get("evaluation_metrics", ["Not explicitly detected"])},

        {"slide_no": 9, "title": "Results", "bullets": bullets_from_text(sections.get("results", ""), 4)},

        {"slide_no": 10, "title": "Key Contributions", "bullets": contributions[:4] or ["See paper for contribution details."]},

        {"slide_no": 11, "title": "Research Gaps", "bullets": gaps[:4] or ["No explicit gaps detected."]},

        {"slide_no": 12, "title": "Conclusion", "bullets": bullets_from_text(sections.get("conclusion", ""), 4)},

        {"slide_no": 13, "title": "Future Scope", "bullets": future_scope[:4] or ["No explicit future work detected."]},

        {"slide_no": 14, "title": "Keywords", "bullets": [k["keyword"] for k in keywords[:10]]},

        {"slide_no": 15, "title": "Thank You / Q&A", "bullets": ["Questions & Discussion"]},
    ]
    return slides
