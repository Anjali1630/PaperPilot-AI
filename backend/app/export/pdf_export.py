"""Export a full analysis report as a .pdf file using ReportLab."""
import json
from pathlib import Path

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, ListFlowable, ListItem, Table, TableStyle
)


def _styles():
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="PPTitle", fontSize=20, leading=24, spaceAfter=10,
                               alignment=1, textColor=colors.HexColor("#4338CA")))
    styles.add(ParagraphStyle(name="PPHeading", fontSize=14, leading=18, spaceBefore=14,
                               spaceAfter=6, textColor=colors.HexColor("#312E81")))
    styles.add(ParagraphStyle(name="PPBody", fontSize=10.5, leading=15))
    return styles


def export_paper_to_pdf(paper, output_path: Path) -> Path:
    styles = _styles()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    doc = SimpleDocTemplate(str(output_path), pagesize=A4,
                             leftMargin=2 * cm, rightMargin=2 * cm,
                             topMargin=1.5 * cm, bottomMargin=1.5 * cm)
    story = []

    story.append(Paragraph(paper.title or paper.filename, styles["PPTitle"]))
    authors = json.loads(paper.authors) if paper.authors else []
    if authors:
        story.append(Paragraph(", ".join(authors), styles["PPBody"]))
    story.append(Spacer(1, 8))

    meta_table = Table([[
        f"Difficulty: {paper.difficulty_label or 'N/A'} ({paper.difficulty_score or 0}/100)",
        f"Est. reading time: {paper.estimated_reading_minutes or 'N/A'} min",
    ]], colWidths=[9 * cm, 9 * cm])
    meta_table.setStyle(TableStyle([
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("TEXTCOLOR", (0, 0), (-1, -1), colors.HexColor("#6B7280")),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 10))

    def add_section(title, text):
        if not text:
            return
        story.append(Paragraph(title, styles["PPHeading"]))
        story.append(Paragraph(text.replace("\n", "<br/>"), styles["PPBody"]))

    def add_list_section(title, items):
        if not items:
            return
        story.append(Paragraph(title, styles["PPHeading"]))
        story.append(ListFlowable(
            [ListItem(Paragraph(str(i), styles["PPBody"])) for i in items],
            bulletType="bullet",
        ))

    add_section("Abstract", paper.abstract)
    add_section("Executive Summary", paper.executive_summary)
    add_section("Standard Summary", paper.standard_summary)
    add_section("Detailed Summary", paper.detailed_summary)
    add_section("Simplified Technical Explanation", paper.simplified_explanation)

    add_list_section("Key Contributions", json.loads(paper.key_contributions or "[]"))
    add_list_section("Research Gaps", json.loads(paper.research_gaps or "[]"))
    add_list_section("Future Scope", json.loads(paper.future_scope or "[]"))

    methodology = json.loads(paper.methodology_json or "{}")
    story.append(Paragraph("Methodology Breakdown", styles["PPHeading"]))
    story.append(Paragraph(f"<b>Algorithms:</b> {', '.join(methodology.get('algorithms', [])) or 'N/A'}", styles["PPBody"]))
    story.append(Paragraph(f"<b>Datasets:</b> {', '.join(methodology.get('datasets', [])) or 'N/A'}", styles["PPBody"]))
    story.append(Paragraph(f"<b>Metrics:</b> {', '.join(methodology.get('evaluation_metrics', [])) or 'N/A'}", styles["PPBody"]))

    keywords = json.loads(paper.keywords_json or "[]")
    add_section("Keywords", ", ".join(k["keyword"] for k in keywords))

    viva = json.loads(paper.viva_questions_json or "{}")
    for level_name, questions in viva.items():
        add_list_section(f"Viva Questions — {level_name.replace('_', ' ').title()}", questions)

    citations = json.loads(paper.citations_json or "{}")
    story.append(Paragraph("Citations", styles["PPHeading"]))
    for style, citation in citations.items():
        story.append(Paragraph(f"<b>{style.upper()}:</b> {citation}", styles["PPBody"]))

    doc.build(story)
    return output_path
