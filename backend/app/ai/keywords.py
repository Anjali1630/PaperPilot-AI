"""Keyword / keyphrase extraction using KeyBERT (local embeddings, no API)."""
from typing import List, Dict
import logging
from app.ai.model_manager import get_keybert_model

logger = logging.getLogger("paperpilot.keywords")

def extract_keywords(text: str, top_n: int = 20) -> List[Dict[str, float]]:
    if not text or not text.strip():
        return []
        
    safe_text = " ".join(text.split()[:4000])
    kw_model = get_keybert_model()
    
    try:
        results = kw_model.extract_keywords(
            safe_text,
            keyphrase_ngram_range=(1, 3),
            stop_words="english",
            use_mmr=True,
            diversity=0.6,
            top_n=top_n,
        )
        return [{"keyword": kw, "score": round(float(score), 4)} for kw, score in results]
    except Exception as e:
        logger.error(f"KeyBERT failed on GPU: {e}. Executing graceful fallback.")
        words = [w.strip(",.()\"';:") for w in safe_text.split() if len(w) > 5]
        unique_words = list(set(words))[:top_n]
        return [{"keyword": w.lower(), "score": 0.5000} for w in unique_words]