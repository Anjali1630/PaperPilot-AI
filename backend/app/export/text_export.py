"""Export analysis as plain Markdown (.md) or plain text (.txt)."""
import json
from pathlib import Path


def _build_markdown(paper) -> str:
    authors = json.loads(paper.authors) if paper.authors else []
    methodology = json.loads(paper.methodology_json or "{}")
    keywords = json.loads(paper.keywords_json or "[]")
    viva = json.loads(paper.viva_questions_json or "{}")
    citations = json.loads(paper.citations_json or "{}")
    contributions = json.loads(paper.key_contributions or "[]")
    gaps = json.loads(paper.research_gaps or "[]")
    future_scope = json.loads(paper.future_scope or "[]")

    lines = [
        f"# {paper.title or paper.filename}",
        "",
        f"**Authors:** {', '.join(authors) if authors else 'N/A'}  ",
        f"**Difficulty:** {paper.difficulty_label or 'N/A'} ({paper.difficulty_score or 0}/100)  ",
        f"**Estimated Reading Time:** {paper.estimated_reading_minutes or 'N/A'} minutes",
        "",
        "## Abstract", paper.abstract or "N/A", "",
        "## Executive Summary", paper.executive_summary or "", "",
        "## Standard Summary", paper.standard_summary or "", "",
        "## Detailed Summary", paper.detailed_summary or "", "",
        "## Simplified Technical Explanation", paper.simplified_explanation or "", "",
        "## Key Contributions",
        *[f"- {c}" for c in contributions], "",
        "## Research Gaps",
        *[f"- {g}" for g in gaps], "",
        "## Future Scope",
        *[f"- {f}" for f in future_scope], "",
        "## Methodology",
        f"- **Algorithms:** {', '.join(methodology.get('algorithms', [])) or 'N/A'}",
        f"- **Datasets:** {', '.join(methodology.get('datasets', [])) or 'N/A'}",
        f"- **Metrics:** {', '.join(methodology.get('evaluation_metrics', [])) or 'N/A'}",
        "",
        "## Keywords",
        ", ".join(k["keyword"] for k in keywords), "",
        "## Viva Questions",
    ]
    for level_name, questions in viva.items():
        lines.append(f"### {level_name.replace('_', ' ').title()}")
        lines.extend([f"- {q}" for q in questions])
    lines += ["", "## Citations"]
    for style, citation in citations.items():
        lines.append(f"- **{style.upper()}:** {citation}")

    return "\n".join(lines)


def export_paper_to_markdown(paper, output_path: Path) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(_build_markdown(paper), encoding="utf-8")
    return output_path


def export_paper_to_txt(paper, output_path: Path) -> Path:
    import re
    md = _build_markdown(paper)
    plain = re.sub(r"[#*`]", "", md)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(plain, encoding="utf-8")
    return output_path
