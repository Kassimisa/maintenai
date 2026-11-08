"""Client minimal pour l'API locale d'Ollama (https://ollama.com)."""
import requests

from maintenai.config import CHAT_MODEL, EMBED_MODEL, OLLAMA_URL


class OllamaError(RuntimeError):
    pass


def _post(endpoint: str, payload: dict, timeout: int = 120) -> dict:
    try:
        resp = requests.post(f"{OLLAMA_URL}{endpoint}", json=payload, timeout=timeout)
    except requests.ConnectionError as exc:
        raise OllamaError(
            f"Ollama ne répond pas sur {OLLAMA_URL}. Lancez Ollama puis réessayez."
        ) from exc
    if resp.status_code == 404:
        raise OllamaError(
            f"Modèle introuvable. Installez-le avec : ollama pull {payload.get('model')}"
        )
    resp.raise_for_status()
    return resp.json()


def embed(texts: list[str], model: str = EMBED_MODEL) -> list[list[float]]:
    """Vecteurs d'embedding pour une liste de textes."""
    return _post("/api/embed", {"model": model, "input": texts})["embeddings"]


def chat(messages: list[dict], model: str = CHAT_MODEL) -> str:
    """Réponse du modèle de chat (non streamée)."""
    data = _post("/api/chat", {"model": model, "messages": messages, "stream": False}, timeout=300)
    return data["message"]["content"]
