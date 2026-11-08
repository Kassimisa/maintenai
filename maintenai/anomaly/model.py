"""Détecteur d'anomalies : apprend le fonctionnement normal, signale ce qui s'en écarte."""
from dataclasses import dataclass, field
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

from maintenai.anomaly.features import add_rolling_features


@dataclass
class AnomalyDetector:
    """Isolation Forest entraîné uniquement sur des données normales.

    Le seuil d'alerte est fixé sur les scores des données normales (quantile),
    ce qui revient à accepter environ (1 - threshold_quantile) de fausses alertes.
    """

    window: int = 10
    threshold_quantile: float = 0.99
    n_estimators: int = 200
    random_state: int = 42
    scaler: StandardScaler = field(default_factory=StandardScaler, init=False)
    forest: IsolationForest | None = field(default=None, init=False)
    threshold: float | None = field(default=None, init=False)

    def _features(self, df: pd.DataFrame) -> np.ndarray:
        return add_rolling_features(df, self.window).to_numpy()

    def fit(self, normal_df: pd.DataFrame) -> "AnomalyDetector":
        X = self.scaler.fit_transform(self._features(normal_df))
        self.forest = IsolationForest(
            n_estimators=self.n_estimators, random_state=self.random_state
        ).fit(X)
        # score_samples : plus le score est bas, plus le point est anormal
        scores = -self.forest.score_samples(X)
        self.threshold = float(np.quantile(scores, self.threshold_quantile))
        return self

    def score(self, df: pd.DataFrame) -> np.ndarray:
        """Score d'anomalie par ligne (plus haut = plus anormal)."""
        if self.forest is None:
            raise RuntimeError("Le modèle n'est pas entraîné : appelez fit() d'abord.")
        X = self.scaler.transform(self._features(df))
        return -self.forest.score_samples(X)

    def predict(self, df: pd.DataFrame) -> np.ndarray:
        """1 = anomalie, 0 = normal."""
        return (self.score(df) > self.threshold).astype(int)

    def save(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(self, path)

    @staticmethod
    def load(path: Path) -> "AnomalyDetector":
        return joblib.load(path)
