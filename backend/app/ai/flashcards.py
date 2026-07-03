"""
Flashcard generation.

Two complementary strategies, both fully local/rule-based:
1. Definition-style: for each top keyword, find the sentence in the paper
   that best "defines" or explains it (highest embedding similarity to a
   templated question about that keyword) and turn it into a Q/A pair.
2. Cloze-style: take high-information sentences (containing a keyword) and
   blank out the keyword, so the "answer" is the missing term.
"""
import re
from typing import Dict, List

from app.ai.model_manager import get_embedder, get_spacy_model


def _sentences(text: str) -> List[str]:
    nlp = get_spacy_model()
    doc = nlp(text)
    return [s.text.strip() for s in doc.sents if 20 < len(s.text.strip()) < 350]


def generate_flashcards(full_text: str, keywords: List[Dict], max_cards: int = 15) -> List[Dict[str, str]]:
    sentences = _sentences(full_text)
    if not sentences or not keywords:
        return []

    embedder = get_embedder()
    sent_vecs = embedder.encode(sentences, normalize_embeddings=True)

    cards = []
    used_sentences = set()

    for kw_entry in keywords[:max_cards]:
        term = kw_entry["keyword"]
        question_probe = f"What is {term}?"
        q_vec = embedder.encode([question_probe], normalize_embeddings=True)[0]
        sims = sent_vecs @ q_vec

        # Prefer sentences that literally contain the term for grounding
        best_idx, best_score = -1, -1.0
        for i, s in enumerate(sentences):
            if term.lower() in s.lower() and i not in used_sentences:
                score = float(sims[i])
                if score > best_score:
                    best_score, best_idx = score, i

        if best_idx == -1:
            continue

        answer_sentence = sentences[best_idx]
        used_sentences.add(best_idx)

        cards.append({
            "question": f"What is meant by '{term}' in this paper?",
            "answer": answer_sentence,
            "type": "definition",
        })

        if len(cards) >= max_cards:
            break

    # Top up with cloze cards if we didn't reach max_cards
    if len(cards) < max_cards:
        for i, s in enumerate(sentences):
            if i in used_sentences or len(cards) >= max_cards:
                continue
            for kw_entry in keywords:
                term = kw_entry["keyword"]
                pattern = re.compile(re.escape(term), re.IGNORECASE)
                if pattern.search(s):
                    cloze = pattern.sub("_____", s, count=1)
                    cards.append({
                        "question": cloze,
                        "answer": term,
                        "type": "cloze",
                    })
                    used_sentences.add(i)
                    break

    return cards[:max_cards]
