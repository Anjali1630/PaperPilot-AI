from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.database import get_db, User, Paper, ChatMessage
from app.schemas import ChatRequest, ChatMessageOut
from app.ai.rag import answer_question

router = APIRouter(prefix="/api/papers/{paper_id}/chat", tags=["chat"])


def _get_owned_paper(paper_id: int, current_user: User, db: Session) -> Paper:
    paper = db.query(Paper).filter(Paper.id == paper_id, Paper.owner_id == current_user.id).first()
    if not paper:
        raise HTTPException(status_code=404, detail="Paper not found")
    if not paper.is_analyzed:
        raise HTTPException(status_code=400, detail="Paper is still being analyzed. Please wait.")
    return paper


@router.get("", response_model=List[ChatMessageOut])
def get_chat_history(paper_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    _get_owned_paper(paper_id, current_user, db)
    return (
        db.query(ChatMessage)
        .filter(ChatMessage.paper_id == paper_id)
        .order_by(ChatMessage.created_at.asc())
        .all()
    )


@router.post("", response_model=ChatMessageOut)
def ask_question(
    paper_id: int,
    payload: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    paper = _get_owned_paper(paper_id, current_user, db)

    user_msg = ChatMessage(paper_id=paper.id, role="user", content=payload.question)
    db.add(user_msg)
    db.commit()

    answer_text = answer_question(paper.id, paper.raw_text or "", payload.question)

    assistant_msg = ChatMessage(paper_id=paper.id, role="assistant", content=answer_text)
    db.add(assistant_msg)
    db.commit()
    db.refresh(assistant_msg)

    return assistant_msg
