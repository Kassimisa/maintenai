"""Entraîne et évalue le détecteur sur SKAB.

Deux protocoles :
- per-file (protocole officiel SKAB) : pour chaque expérience, le modèle apprend sur les
  premières lignes (fonctionnement normal) puis surveille la suite. C'est le cas réel d'une
  machine qu'on installe : on apprend son comportement normal, puis on la surveille.
- global : un seul modèle appris sur l'enregistrement « anomaly-free », testé partout.

Usage :
    python -m maintenai.anomaly.train
    python -m maintenai.anomaly.train --protocol global --window 30
"""
import argparse
import json

import pandas as pd
from sklearn.metrics import f1_score, precision_score, recall_score

from maintenai.anomaly.data import list_experiments, load_anomaly_free, load_file
from maintenai.anomaly.model import AnomalyDetector
from maintenai.config import MODELS_DIR, RESULTS_DIR


def metrics(y_true, y_pred) -> dict:
    y_true = pd.Series(y_true).astype(int)
    y_pred = pd.Series(y_pred).astype(int)
    normal = y_true == 0
    return {
        "precision": round(precision_score(y_true, y_pred, zero_division=0), 3),
        "recall": round(recall_score(y_true, y_pred, zero_division=0), 3),
        "f1": round(f1_score(y_true, y_pred, zero_division=0), 3),
        "false_alarm_rate": round(float(y_pred[normal].mean()) if normal.any() else 0.0, 3),
        "n_points": int(len(y_true)),
    }


def run(protocol: str, window: int, quantile: float, train_rows: int) -> dict:
    experiments = list_experiments()
    global_model = None
    if protocol == "global":
        global_model = AnomalyDetector(window=window, threshold_quantile=quantile)
        global_model.fit(load_anomaly_free())
        global_model.save(MODELS_DIR / "detector_global.joblib")

    rows = []
    for group, files in experiments.items():
        for path in files:
            df = load_file(path)
            if protocol == "per-file":
                model = AnomalyDetector(window=window, threshold_quantile=quantile)
                model.fit(df.iloc[:train_rows])
                test = df.iloc[train_rows:]
                pred = model.predict(df)[train_rows:]  # fenêtres calculées sur tout le flux
            else:
                test = df
                pred = global_model.predict(df)
            rows.append(pd.DataFrame({
                "group": group, "file": path.name,
                "y_true": test["anomaly"].to_numpy(), "y_pred": pred,
            }))

    allp = pd.concat(rows, ignore_index=True)
    report = {
        "protocol": protocol,
        "params": {"window": window, "threshold_quantile": quantile, "train_rows": train_rows},
        "overall": metrics(allp.y_true, allp.y_pred),
        "by_group": {g: metrics(d.y_true, d.y_pred) for g, d in allp.groupby("group")},
    }
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--protocol", choices=["per-file", "global"], default="per-file")
    parser.add_argument("--window", type=int, default=10, help="fenêtre glissante (secondes)")
    parser.add_argument("--quantile", type=float, default=0.99, help="quantile du seuil d'alerte")
    parser.add_argument("--train-rows", type=int, default=400, help="lignes d'apprentissage (per-file)")
    args = parser.parse_args()

    report = run(args.protocol, args.window, args.quantile, args.train_rows)

    RESULTS_DIR.mkdir(exist_ok=True)
    out = RESULTS_DIR / f"metrics_{args.protocol}.json"
    out.write_text(json.dumps(report, indent=2), encoding="utf-8")

    print(f"\nProtocole : {report['protocol']}  |  paramètres : {report['params']}")
    table = pd.DataFrame({"global": report["overall"], **report["by_group"]}).T
    print(table.to_string())
    print(f"\nRésultats enregistrés dans {out}")


if __name__ == "__main__":
    main()
