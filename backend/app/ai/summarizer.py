"""
Multi-length abstractive summarization using a local BART model
(facebook/bart-large-cnn by default — fully open-source, no API key).

BART has a ~1024 token input limit, so long papers are chunked, each chunk
is summarized independently, and the partial summaries are combined and
(for longer targets) re-summarized in a second pass ("map-reduce"
summarization), which is a standard technique for summarizing long
documents with encoder-decoder models.
"""
import logging
from typing import List

from app.ai.model_manager import get_summarizer
from app.utils.pdf_processor import chunk_text

logger = logging.getLogger("paperpilot.summarizer")


def _summarize_chunk(text: str, max_len: int, min_len: int) -> str:
    summarizer = get_summarizer()
    text = text.strip()
    if not text:
        return ""

    # IMPORTANT: BART's position embeddings only support up to 1024 tokens.
    # A word-count heuristic is not a reliable proxy for token count
    # (technical text tokenizes to more subwords than plain English), and
    # feeding an over-length sequence causes an out-of-range embedding
    # lookup — which raises a clear IndexError on CPU, but on GPU it
    # surfaces later and asynchronously as a confusing
    # "CUDA error: device-side assert triggered" crash.
    #
    # `truncation=True` makes the pipeline's tokenizer actually truncate to
    # the model's real max input length before encoding, which is the
    # correct fix (rather than guessing a word count).
    try:
        out = summarizer(
            text,
            max_length=max_len,
            min_length=min_len,
            do_sample=False,
            truncation=True,
        )
        return out[0]["summary_text"].strip()
    except Exception as exc:
        logger.warning("Summarization failed for a chunk (%s); returning truncated raw text instead.", exc)
        # Model may reject very short/malformed inputs; fall back to
        # returning the text as-is rather than crashing the whole pipeline.
        return text[:max_len * 6]


def _map_reduce_summary(full_text: str, target_words: int) -> str:
    chunks = chunk_text(full_text, chunk_size=700, overlap=50)
    if not chunks:
        return ""

    per_chunk_max = max(60, min(180, int(target_words / max(len(chunks), 1)) + 40))
    partial_summaries: List[str] = [
        _summarize_chunk(c, max_len=per_chunk_max, min_len=max(20, per_chunk_max // 3))
        for c in chunks
    ]
    combined = " ".join(partial_summaries)

    # Second pass: compress the combined partial summaries down to target length
    if len(combined.split()) > target_words * 1.3:
        combined = _summarize_chunk(
            combined,
            max_len=int(target_words * 1.4),
            min_len=int(target_words * 0.6),
        )
    return combined


def generate_summaries(full_text: str) -> dict:
    """Generate executive (100w), standard (300w), and detailed (700w) summaries."""
    if not full_text or not full_text.strip():
        return {"executive": "", "standard": "", "detailed": ""}

    detailed = _map_reduce_summary(full_text, target_words=700)
    # Executive and standard are further compressions of the detailed
    # summary, which is cheaper and more consistent than re-running
    # map-reduce from scratch each time.
    base_for_short = detailed if detailed else full_text
    standard = _summarize_chunk(base_for_short, max_len=340, min_len=180) if base_for_short else ""
    executive = _summarize_chunk(standard or base_for_short, max_len=130, min_len=60) if (standard or base_for_short) else ""

    return {
        "executive": executive,
        "standard": standard,
        "detailed": detailed,
    }