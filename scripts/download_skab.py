"""Télécharge le jeu de données SKAB dans data/skab/.

Source : https://github.com/waico/SKAB (Skoltech Anomaly Benchmark, licence GPL-3.0).

Usage :
    python scripts/download_skab.py
"""
import io
import shutil
import sys
import zipfile
from pathlib import Path

import requests

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from maintenai.config import SKAB_DIR  # noqa: E402

URL = "https://github.com/waico/SKAB/archive/refs/heads/master.zip"


def main() -> None:
    if (SKAB_DIR / "data" / "valve1").exists():
        print(f"SKAB est déjà présent dans {SKAB_DIR}")
        return
    print(f"Téléchargement de {URL} …")
    resp = requests.get(URL, timeout=120)
    resp.raise_for_status()
    with zipfile.ZipFile(io.BytesIO(resp.content)) as zf:
        members = [m for m in zf.namelist() if "/data/" in m]
        tmp = SKAB_DIR.parent / "_skab_tmp"
        zf.extractall(tmp, members)
    extracted = next(tmp.iterdir())
    SKAB_DIR.mkdir(parents=True, exist_ok=True)
    shutil.move(str(extracted / "data"), str(SKAB_DIR / "data"))
    shutil.rmtree(tmp)
    n = len(list((SKAB_DIR / "data").rglob("*.csv")))
    print(f"OK : {n} fichiers CSV dans {SKAB_DIR / 'data'}")


if __name__ == "__main__":
    main()
