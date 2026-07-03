import json
from collections import Counter

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.database import get_db, User, Paper
from app.schemas import DashboardStats, PaperOut

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("", response_model=DashboardStats)
def get_dashboard(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    papers = db.query(Paper).filter(Paper.owner_id == current_user.id).all()

    total_papers = len(papers)
    analyzed = [p for p in papers if p.is_analyzed]
    papers_summarized = len(analyzed)

    total_minutes_saved = 0
    for p in analyzed:
        if p.estimated_reading_minutes:
            # Reading the executive summary is assumed to take ~1/8th the
            # time of reading the full paper — a simple, explainable proxy
            # for "time saved" rather than an arbitrary made-up number.
            total_minutes_saved += max(p.estimated_reading_minutes - p.estimated_reading_minutes / 8, 0)

    avg_minutes_saved = round(total_minutes_saved / papers_summarized, 1) if papers_summarized else 0.0

    recent_uploads = sorted(papers, key=lambda p: p.created_at, reverse=True)[:5]

    keyword_counter = Counter()
    for p in analyzed:
        try:
            keywords = json.loads(p.keywords_json or "[]")
        except json.JSONDecodeError:
            keywords = []
        for k in keywords[:10]:
            keyword_counter[k["keyword"]] += 1
    top_keywords = [{"keyword": k, "count": c} for k, c in keyword_counter.most_common(15)]

    recent_activity = [
        {
            "paper_id": p.id,
            "title": p.title or p.filename,
            "status": p.status,
            "timestamp": p.updated_at.isoformat() if p.updated_at else p.created_at.isoformat(),
        }
        for p in sorted(papers, key=lambda p: p.updated_at or p.created_at, reverse=True)[:10]
    ]

    return DashboardStats(
        total_papers=total_papers,
        papers_summarized=papers_summarized,
        avg_reading_minutes_saved=avg_minutes_saved,
        recent_uploads=[PaperOut.model_validate(p) for p in recent_uploads],
        top_keywords=top_keywords,
        recent_activity=recent_activity,
    )
