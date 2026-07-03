import json

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.database import get_db, User, Paper, Comparison
from app.schemas import CompareRequest
from app.ai.compare import compare_papers

router = APIRouter(prefix="/api/compare", tags=["compare"])


@router.post("")
def compare(payload: CompareRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    papers = (
        db.query(Paper)
        .filter(Paper.id.in_(payload.paper_ids), Paper.owner_id == current_user.id)
        .all()
    )
    if len(papers) != len(payload.paper_ids):
        raise HTTPException(status_code=404, detail="One or more papers not found")

    not_ready = [p.filename for p in papers if not p.is_analyzed]
    if not_ready:
        raise HTTPException(status_code=400, detail=f"Still analyzing: {', '.join(not_ready)}")

    result = compare_papers(papers)

    comparison = Comparison(
        owner_id=current_user.id,
        paper_ids_json=json.dumps(payload.paper_ids),
        result_json=json.dumps(result),
    )
    db.add(comparison)
    db.commit()

    return result
