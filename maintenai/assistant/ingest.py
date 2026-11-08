"""Indexe les manuels PDF de data/manuals/ pour l'assistant.

Chaque page est découpée en morceaux ; on garde le nom du fichier et le numéro de page
pour que l'assistant puisse citer sa source.

Usage :
    python -m maintenai.assistant.ingest
"""
import json
import re
from pathlib import Path

import numpy as np
from pypdf import PdfReader

from maintenai.assistant.ollama_client import embed
from maintenai.config import INDEX_DIR, MANUALS_DIR


def chunk_text(text: str, max_chars: int = 1000, overlap: int = 150) -> list[str]:
    """Découpe un texte en morceaux qui se chevauchent légèrement."""
    text = re.sub(r"\s+", " ", text).strip()
    if not text:
        return []
    chunks, start = [], 0
    while start < len(text):
        end = min(start + max_chars, len(text))
        chunks.append(text[start:end])
        if end == len(text):
            break
        start = end - overlap
    return chunks


def read_pdf(path: Path) -> list[dict]:
    chunks = []
    for page_no, page in enumerate(PdfReader(str(path)).pages, start=1):
        for piece in chunk_text(page.extract_text() or ""):
            chunks.append({"source": path.name, "page": page_no, "text": piece})
    return chunks


def build_index(manuals_dir: Path = MANUALS_DIR, index_dir: Path = INDEX_DIR, batch: int = 32) -> int:
    pdfs = sorted(manuals_dir.glob("*.pdf"))
    if not pdfs:
        raise FileNotFoundError(f"Aucun PDF dans {manuals_dir}. Ajoutez des manuels techniques.")

    chunks = []
    for pdf in pdfs:
        found = read_pdf(pdf)
        print(f"{pdf.name} : {len(found)} morceaux")
        chunks.extend(found)
    if not chunks:
        raise ValueError("Aucun texte extrait (PDF scannés ? Il faut alors un OCR).")

    vectors = []
    for i in range(0, len(chunks), batch):
        vectors.extend(embed([c["text"] for c in chunks[i:i + batch]]))

    index_dir.mkdir(parents=True, exist_ok=True)
    np.save(index_dir / "vectors.npy", np.asarray(vectors, dtype=np.float32))
    (index_dir / "chunks.json").write_text(json.dumps(chunks, ensure_ascii=False), encoding="utf-8")
    return len(chunks)


if __name__ == "__main__":
    n = build_index()
    print(f"Index créé : {n} morceaux dans {INDEX_DIR}")
