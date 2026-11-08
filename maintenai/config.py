"""Chemins et paramètres partagés du projet."""
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
SKAB_DIR = DATA_DIR / "skab"
MANUALS_DIR = DATA_DIR / "manuals"
INDEX_DIR = DATA_DIR / "index"
MODELS_DIR = ROOT / "models"
RESULTS_DIR = ROOT / "results"

# Capteurs SKAB (pompe à eau du banc d'essai Skoltech)
SENSORS = [
    "Accelerometer1RMS",
    "Accelerometer2RMS",
    "Current",
    "Pressure",
    "Temperature",
    "Thermocouple",
    "Voltage",
    "Volume Flow RateRMS",
]

# Libellés lisibles pour l'interface
SENSOR_LABELS = {
    "Accelerometer1RMS": "Vibration 1 (g)",
    "Accelerometer2RMS": "Vibration 2 (g)",
    "Current": "Courant moteur (A)",
    "Pressure": "Pression (bar)",
    "Temperature": "Température moteur (°C)",
    "Thermocouple": "Température fluide (°C)",
    "Voltage": "Tension (V)",
    "Volume Flow RateRMS": "Débit (L/min)",
}

# Assistant IA (Ollama en local)
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
CHAT_MODEL = os.getenv("MAINTENAI_CHAT_MODEL", "qwen3.5:9b")
EMBED_MODEL = os.getenv("MAINTENAI_EMBED_MODEL", "nomic-embed-text")
