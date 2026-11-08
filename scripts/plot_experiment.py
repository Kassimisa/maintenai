"""Trace les capteurs d'une expérience SKAB avec les anomalies en couleur.

Usage :
    python scripts/plot_experiment.py valve1 0
"""
import sys
from pathlib import Path

import matplotlib.pyplot as plt

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from maintenai.anomaly.data import load_file  # noqa: E402
from maintenai.config import RESULTS_DIR, SENSOR_LABELS, SENSORS, SKAB_DIR  # noqa: E402


def main(group: str = "valve1", number: str = "0") -> None:
    df = load_file(SKAB_DIR / "data" / group / f"{number}.csv")
    fig, axes = plt.subplots(len(SENSORS), 1, figsize=(14, 16), sharex=True)
    for ax, col in zip(axes, SENSORS):
        ax.plot(df.index, df[col], lw=0.8, color="#1f4e78")
        ax.fill_between(df.index, df[col].min(), df[col].max(), where=df["anomaly"] == 1,
                        color="#e07a2e", alpha=0.3)
        ax.set_ylabel(SENSOR_LABELS[col], fontsize=8)
    fig.suptitle(f"SKAB {group}/{number} : zones orange = anomalies")
    fig.tight_layout()
    RESULTS_DIR.mkdir(exist_ok=True)
    out = RESULTS_DIR / f"skab_{group}_{number}.png"
    fig.savefig(out, dpi=110)
    print(f"Graphique enregistré : {out}")


if __name__ == "__main__":
    main(*sys.argv[1:3])
