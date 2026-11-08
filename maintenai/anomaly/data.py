"""Chargement du jeu de données SKAB."""
from pathlib import Path

import pandas as pd

from maintenai.config import SKAB_DIR

GROUPS = ("valve1", "valve2", "other")


def load_file(path: Path) -> pd.DataFrame:
    """Lit un CSV SKAB (séparateur ';', index = datetime)."""
    df = pd.read_csv(path, sep=";", index_col="datetime", parse_dates=True)
    return df.sort_index()


def list_experiments(skab_dir: Path = SKAB_DIR) -> dict[str, list[Path]]:
    """Fichiers d'expériences (avec anomalies étiquetées), par groupe."""
    data_dir = skab_dir / "data"
    if not data_dir.exists():
        raise FileNotFoundError(
            f"SKAB introuvable dans {data_dir}. Lancez : python scripts/download_skab.py"
        )
    return {
        group: sorted((data_dir / group).glob("*.csv"), key=lambda p: int(p.stem))
        for group in GROUPS
    }


def load_anomaly_free(skab_dir: Path = SKAB_DIR) -> pd.DataFrame:
    """Enregistrement de fonctionnement normal (sans anomalie)."""
    return load_file(skab_dir / "data" / "anomaly-free" / "anomaly-free.csv")
