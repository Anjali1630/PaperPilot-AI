from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.config import settings
from app.database import get_db, User, Paper
from app.export.pdf_export import export_paper_to_pdf
from app.export.docx_export import export_paper_to_docx
from app.export.pptx_export import export_paper_to_pptx
from app.export.text_export import export_paper_to_markdown, export_paper_to_txt

router = APIRouter(prefix="/api/papers/{paper_id}/export", tags=["export"])

MIME_TYPES = {
    "pdf": "application/pdf",
    "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "pptx": "application/vnd.openxmlformats-officedocument.presentationml.presentation",
    "md": "text/markdown",
    "txt": "text/plain",
}

EXPORTERS = {
    "pdf": export_paper_to_pdf,
    "docx": export_paper_to_docx,
    "pptx": export_paper_to_pptx,
    "md": export_paper_to_markdown,
    "txt": export_paper_to_txt,
}


def _get_owned_analyzed_paper(paper_id: int, current_user: User, db: Session) -> Paper:
    paper = db.query(Paper).filter(Paper.id == paper_id, Paper.owner_id == current_user.id).first()
    if not paper:
        raise HTTPException(status_code=404, detail="Paper not found")
    if not paper.is_analyzed:
        raise HTTPException(status_code=400, detail="Paper analysis is not complete yet")
    return paper


@router.get("/{fmt}")
def export_paper(paper_id: int, fmt: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if fmt not in EXPORTERS:
        raise HTTPException(status_code=400, detail=f"Unsupported format '{fmt}'. Choose from: {list(EXPORTERS)}")

    paper = _get_owned_analyzed_paper(paper_id, current_user, db)
    safe_title = "".join(c for c in (paper.title or paper.filename) if c.isalnum() or c in " _-")[:60].strip() or "paper"
    output_path = settings.EXPORT_DIR / f"{paper.id}_{safe_title}.{fmt}"

    EXPORTERS[fmt](paper, output_path)

    return FileResponse(
        path=str(output_path),
        media_type=MIME_TYPES[fmt],
        filename=f"{safe_title}.{fmt}",
    )
