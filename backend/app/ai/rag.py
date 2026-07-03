"""
Retrieval-Augmented Generation for "Chat with PDF".

Pipeline (100% local):
1. The paper is chunked (see utils.pdf_processor.chunk_text) and each chunk
   is embedded with a sentence-transformer model.
2. Embeddings are indexed per-paper with FAISS (flat L2 index — fine at this
   scale, no need for IVF/quantization).
3. On each question, the top-k most relevant chunks are retrieved.
4. An extractive QA model (RoBERTa fine-tuned on SQuAD2) finds the best
   answer span inside the retrieved context. If confidence is very low
   (likely unanswerable / not in the paper), we fall back to returning the
   most relevant retrieved passage instead of a low-confidence extracted
   span, and say so explicitly rather than hallucinate.
Per-paper FAISS indexes are cached to disk under VECTOR_STORE_DIR so a
paper's index only needs to be built once.
"""
import json
import pickle
from pathlib import Path
from typing import List, Tuple
import faiss
import numpy as np
from app.ai.model_manager import get_embedder, get_qa_pipeline
from app.config import settings
from app.utils.pdf_processor import chunk_text

def _index_paths(paper_id: int) -> Tuple[Path, Path]:
    idx_path = settings.VECTOR_STORE_DIR / f"paper_{paper_id}.faiss"
    meta_path = settings.VECTOR_STORE_DIR / f"paper_{paper_id}.chunks.pkl"
    return idx_path, meta_path

def build_or_load_index(paper_id: int, full_text: str):
    idx_path, meta_path = _index_paths(paper_id)
    embedder = get_embedder()
    
    if idx_path.exists() and meta_path.exists():
        try:
            index = faiss.read_index(str(idx_path))
            with open(meta_path, "rb") as f:
                chunks = pickle.load(f)
            return index, chunks
        except Exception:
            idx_path.unlink(missing_ok=True)
            meta_path.unlink(missing_ok=True)

    chunks = chunk_text(full_text, chunk_size=250, overlap=40)
    if not chunks:
        chunks = [full_text[:2000]] if full_text else [""]
        
    embeddings = embedder.encode(chunks, normalize_embeddings=True)
    embeddings = np.array(embeddings, dtype="float32")
    
    dim = embeddings.shape[1]
    index = faiss.IndexFlatIP(dim)
    index.add(embeddings)
    
    faiss.write_index(index, str(idx_path))
    with open(meta_path, "wb") as f:
        pickle.dump(chunks, f)
        
    return index, chunks

def retrieve_relevant_chunks(paper_id: int, full_text: str, question: str, top_k: int = 4) -> List[str]:
    index, chunks = build_or_load_index(paper_id, full_text)
    embedder = get_embedder()
    q_vec = embedder.encode([question], normalize_embeddings=True).astype("float32")
    
    k = min(top_k, len(chunks))
    if k == 0:
        return []
    scores, indices = index.search(q_vec, k)
    return [chunks[i] for i in indices[0] if 0 <= i < len(chunks)]

def answer_question(paper_id: int, full_text: str, question: str) -> str:
    clean_q = question.strip().lower()
    
    if any(clean_q.startswith(greet) for greet in ["hi", "hello", "hey", "thanks", "thank you"]):
        return "You're welcome! Let me know if you need help extracting details or metrics from this paper."
        
    relevant_chunks = retrieve_relevant_chunks(paper_id, full_text, question, top_k=4)
    if not relevant_chunks:
        return "I couldn't find relevant content in this paper to answer that question."
        
    context = "\n\n".join(relevant_chunks)[:3800]
    qa_pipeline = get_qa_pipeline()
    
    try:
        result = qa_pipeline(question=question, context=context)
    except Exception:
        return f"Based on the most relevant passage I found:\n\n{relevant_chunks[0][:600]}"
        
    answer = (result.get("answer") or "").strip()
    confidence = result.get("score", 0.0)
    
    if not answer or confidence < 0.25:
        if any(k in clean_q for k in ["problem", "objective", "statement", "goal"]):
            for chunk in relevant_chunks:
                if any(k in chunk.lower() for k in ["problem", "objective", "introduce", "aim"]):
                    return f"I couldn't isolate a clean, short answer span, but this section highlights the objective:\n\n...{chunk[:600]}..."
                    
        return (
            "I couldn't extract a highly confident, direct answer for that question. "
            f"Here is the most relevant passage found:\n\n...{relevant_chunks[0][:500]}..."
        )
        
    return f"{answer}\n\n— (based on: \"{relevant_chunks[0][:220].strip()}...\")"
