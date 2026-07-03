"""
Lazy-loaded, process-wide singletons for all local AI models.

Loading transformer models is expensive (seconds-to-minutes and hundreds of
MB of RAM), so every model is instantiated exactly once and reused across
requests. Nothing here calls any paid/external API — every model is pulled
from the public Hugging Face Hub once and then cached locally by the
`transformers`/`sentence-transformers` libraries (~/.cache/huggingface).
"""
import logging
from functools import lru_cache
from app.config import settings

logger = logging.getLogger("paperpilot.models")

# Sync directly with the core application config settings
DEVICE_STR = "cpu" if settings.DEVICE.lower() == "cpu" else "cuda"
DEVICE = -1 if DEVICE_STR == "cpu" else 0

logger.info(f"Model manager synchronized execution platform: {DEVICE_STR.upper()}")


@lru_cache(maxsize=1)
def get_summarizer():
    from transformers import pipeline
    logger.info("Loading summarization model: %s", settings.SUMMARIZATION_MODEL)
    return pipeline("summarization", model=settings.SUMMARIZATION_MODEL, device=DEVICE)


@lru_cache(maxsize=1)
def get_embedder():
    from sentence_transformers import SentenceTransformer
    logger.info("Loading embedding model: %s", settings.EMBEDDING_MODEL)
    model = SentenceTransformer(settings.EMBEDDING_MODEL, device=DEVICE_STR)
    # Target safety restriction for technical subwords
    model.max_seq_length = 256
    return model


@lru_cache(maxsize=1)
def get_qa_pipeline():
    from transformers import pipeline
    logger.info("Loading extractive QA model: %s", settings.QA_MODEL)
    return pipeline("question-answering", model=settings.QA_MODEL, device=DEVICE)


@lru_cache(maxsize=1)
def get_keybert_model():
    from keybert import KeyBERT
    logger.info("Loading KeyBERT (uses embedding model above)")
    return KeyBERT(model=get_embedder())


@lru_cache(maxsize=1)
def get_spacy_model():
    import spacy
    try:
        return spacy.load(settings.SPACY_MODEL)
    except OSError:
        logger.warning(
            "spaCy model '%s' not found. Run: python -m spacy download %s",
            settings.SPACY_MODEL, settings.SPACY_MODEL,
        )
        nlp = spacy.blank("en")
        nlp.add_pipe("sentencizer")
        return nlp