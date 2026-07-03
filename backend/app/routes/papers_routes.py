import shutil
import uuid
import logging
from pathlib import Path
from typing import List

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, BackgroundTasks
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.config import settings
from app.database import get_db, User, Paper
from app.schemas import PaperOut, PaperDetail
from app.ai.pipeline import run_full_analysis

router = APIRouter(prefix="/api/papers", tags=["papers"])
logger = logging.getLogger("paperpilot.papers")

ALLOWED_EXTENSIONS = {".pdf"}


def _validate_pdf(file: UploadFile):
    ext = Path(file.filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")


def _run_analysis_task(paper_id: int):
    """Runs in a FastAPI background task so the upload request returns immediately
    and the frontend can poll /api/papers/{id} for status."""
    from app.database import SessionLocal
    db = SessionLocal()
    try:
        paper = db.query(Paper).filter(Paper.id == paper_id).first()
        if not paper:
            return
        paper.status = "processing"
        db.commit()

        try:
            results = run_full_analysis(paper.filepath)
            for key, value in results.items():
                setattr(paper, key, value)
            paper.is_analyzed = True
            paper.status = "analyzed"
            paper.error_message = None
        except Exception as exc:  # noqa: BLE001
            logger.exception("Analysis failed for paper %s", paper_id)
            paper.status = "failed"
            paper.error_message = str(exc)

        db.commit()
    finally:
        db.close()


@router.post("/upload", response_model=List[PaperOut])
async def upload_papers(
    background_tasks: BackgroundTasks,
    files: List[UploadFile] = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    created = []
    for file in files:
        _validate_pdf(file)

        contents = await file.read()
        size_mb = len(contents) / (1024 * 1024)
        if size_mb > settings.MAX_UPLOAD_SIZE_MB:
            raise HTTPException(
                status_code=400,
                detail=f"'{file.filename}' exceeds max upload size of {settings.MAX_UPLOAD_SIZE_MB}MB",
            )

        unique_name = f"{uuid.uuid4().hex}_{Path(file.filename).name}"
        dest_path = settings.UPLOAD_DIR / unique_name
        with open(dest_path, "wb") as f:
            f.write(contents)

        paper = Paper(
            owner_id=current_user.id,
            filename=file.filename,
            filepath=str(dest_path),
            status="uploaded",
        )
        db.add(paper)
        db.commit()
        db.refresh(paper)

        background_tasks.add_task(_run_analysis_task, paper.id)
        created.append(paper)

    return created


@router.get("", response_model=List[PaperOut])
def list_papers(
    search: str = "",
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    query = db.query(Paper).filter(Paper.owner_id == current_user.id)
    if search:
        query = query.filter(Paper.title.ilike(f"%{search}%") | Paper.filename.ilike(f"%{search}%"))
    return query.order_by(Paper.created_at.desc()).all()


@router.get("/{paper_id}", response_model=PaperDetail)
def get_paper(paper_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    paper = db.query(Paper).filter(Paper.id == paper_id, Paper.owner_id == current_user.id).first()
    if not paper:
        raise HTTPException(status_code=404, detail="Paper not found")
    return paper


@router.delete("/{paper_id}", status_code=204)
def delete_paper(paper_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    paper = db.query(Paper).filter(Paper.id == paper_id, Paper.owner_id == current_user.id).first()
    if not paper:
        raise HTTPException(status_code=404, detail="Paper not found")

    try:
        Path(paper.filepath).unlink(missing_ok=True)
    except OSError:
        pass

    for pattern in [f"paper_{paper.id}.faiss", f"paper_{paper.id}.chunks.pkl"]:
        p = settings.VECTOR_STORE_DIR / pattern
        if p.exists():
            p.unlink()

    db.delete(paper)
    db.commit()
    return None


@router.post("/{paper_id}/reanalyze", response_model=PaperOut)
def reanalyze_paper(
    paper_id: int,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    paper = db.query(Paper).filter(Paper.id == paper_id, Paper.owner_id == current_user.id).first()
    if not paper:
        raise HTTPException(status_code=404, detail="Paper not found")

    paper.status = "processing"
    paper.is_analyzed = False
    db.commit()

    background_tasks.add_task(_run_analysis_task, paper.id)
    return paper
