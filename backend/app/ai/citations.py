"""
Citation Generator — produces APA, IEEE, MLA, and Chicago formatted
citations from metadata extracted directly from the PDF (title, authors,
year). Purely string formatting; no external citation API is used.
"""
import re
from typing import Dict, List, Optional


def _extract_year(raw_text: str) -> Optional[str]:
    # Look for a plausible 4-digit publication year (1990-2029) near the
    # start of the document, which is where copyright/venue lines usually sit.
    window = raw_text[:3000]
    matches = re.findall(r"\b(19[9]\d|20[0-2]\d)\b", window)
    if matches:
        return matches[0]
    matches_full = re.findall(r"\b(19[9]\d|20[0-2]\d)\b", raw_text)
    return matches_full[0] if matches_full else None


def _last_name(author: str) -> str:
    parts = author.strip().split()
    return parts[-1] if parts else author


def _initials(author: str) -> str:
    parts = author.strip().split()
    return " ".join(f"{p[0]}." for p in parts[:-1]) if len(parts) > 1 else ""


def generate_citations(title: str, authors: List[str], raw_text: str) -> Dict[str, str]:
    title = (title or "Untitled Paper").strip().rstrip(".")
    authors = [a for a in (authors or []) if a][:8]
    year = _extract_year(raw_text) or "n.d."

    if not authors:
        apa = f'{title}. ({year}).'
        ieee = f'"{title}," {year}.'
        mla = f'"{title}." {year}.'
        chicago = f'"{title}." {year}.'
        return {"apa": apa, "ieee": ieee, "mla": mla, "chicago": chicago}

    # --- APA: Last, F. M., & Last2, F. M. (Year). Title. ---
    apa_authors = []
    for a in authors:
        init = _initials(a)
        apa_authors.append(f"{_last_name(a)}, {init}".strip().rstrip(","))
    if len(apa_authors) == 1:
        apa_author_str = apa_authors[0]
    elif len(apa_authors) == 2:
        apa_author_str = f"{apa_authors[0]} & {apa_authors[1]}"
    else:
        apa_author_str = ", ".join(apa_authors[:-1]) + f", & {apa_authors[-1]}"
    apa = f"{apa_author_str} ({year}). {title}."

    # --- IEEE: A. Author, B. Author, "Title," Year. ---
    ieee_authors = []
    for a in authors:
        parts = a.strip().split()
        if len(parts) > 1:
            ieee_authors.append(f"{parts[0][0]}. {parts[-1]}")
        else:
            ieee_authors.append(a)
    ieee = f'{", ".join(ieee_authors)}, "{title}," {year}.'

    # --- MLA: Last, First, et al. "Title." Year. ---
    if len(authors) == 1:
        mla_author_str = f"{_last_name(authors[0])}, {' '.join(authors[0].split()[:-1])}".strip().rstrip(",")
    else:
        first = authors[0]
        mla_author_str = f"{_last_name(first)}, {' '.join(first.split()[:-1])}, et al.".strip()
    mla = f'{mla_author_str}. "{title}." {year}.'

    # --- Chicago: Last, First, and First Last. "Title." Year. ---
    chicago_authors = []
    for i, a in enumerate(authors):
        parts = a.strip().split()
        if i == 0:
            chicago_authors.append(f"{_last_name(a)}, {' '.join(parts[:-1])}".strip().rstrip(","))
        else:
            chicago_authors.append(a)
    chicago_author_str = " and ".join(chicago_authors) if len(chicago_authors) <= 2 else ", ".join(chicago_authors[:-1]) + f", and {chicago_authors[-1]}"
    chicago = f'{chicago_author_str}. "{title}." {year}.'

    return {"apa": apa, "ieee": ieee, "mla": mla, "chicago": chicago}
