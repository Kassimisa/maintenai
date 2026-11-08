"""Recherche dans les manuels + réponse du modèle, avec citation des sources.

Usage :
    python -m maintenai.assistant.rag "La pompe vibre anormalement, que vérifier ?"
"""
import json
import sys
from dataclasses import dataclass
from pathlib import Path

import numpy as np

from maintenai.assistant.ollama_client import chat, embed
from maintenai.config import INDEX_DIR

SYSTEM_PROMPT = """Tu es MaintenAI, un assistant pour techniciens de maintenance industrielle.
Réponds en français, de façon claire et pas à pas.
Appuie-toi UNIQUEMENT sur les extraits de manuels fournis. Cite tes sources sous la forme
[fichier, p. N]. Si les extraits ne permettent pas de répondre, dis-le clairement
et propose quoi vérifier ou qui contacter. Rappelle les consignes de sécurité
(consignation, arrêt machine) quand une intervention est nécessaire."""


@dataclass
class Index:
    vectors: np.ndarray
    chunks: list[dict]

    @classmethod
    def load(cls, index_dir: Path = INDEX_DIR) -> "Index":
        if not (index_dir / "vectors.npy").exists():
            raise FileNotFoundError("Index absent. Lancez : python -m maintenai.assistant.ingest")
        vectors = np.load(index_dir / "vectors.npy")
        chunks = json.loads((index_dir / "chunks.json").read_text(encoding="utf-8"))
        return cls(vectors / np.linalg.norm(vectors, axis=1, keepdims=True), chunks)

    def search(self, question: str, k: int = 4) -> list[dict]:
        q = np.asarray(embed([question])[0], dtype=np.float32)
        sims = self.vectors @ (q / np.linalg.norm(q))
        best = np.argsort(sims)[::-1][:k]
        return [{**self.chunks[i], "score": float(sims[i])} for i in best]


def answer(question: str, index: Index, context: str | None = None, k: int = 4) -> tuple[str, list[dict]]:
    """Retourne la réponse et les extraits utilisés.

    `context` permet de transmettre une alerte du module de détection
    (ex. « Pression anormale sur la pompe P-03 »).
    """
    hits = index.search(f"{context}\n{question}" if context else question, k=k)
    excerpts = "\n\n".join(f"[{h['source']}, p. {h['page']}]\n{h['text']}" for h in hits)
    user = f"Extraits de manuels :\n{excerpts}\n\n"
    if context:
        user += f"Alerte machine : {context}\n"
    user += f"Question du technicien : {question}"
    reply = chat([{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": user}])
    return reply, hits


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit('Usage : python -m maintenai.assistant.rag "votre question"')
    text, sources = answer(" ".join(sys.argv[1:]), Index.load())
    print(text)
    print("\nSources :", ", ".join(f"{s['source']} p.{s['page']}" for s in sources))
