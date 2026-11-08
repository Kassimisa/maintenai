"""Construction des variables (features) à partir des capteurs bruts."""
import pandas as pd

from maintenai.config import SENSORS


def add_rolling_features(df: pd.DataFrame, window: int = 10) -> pd.DataFrame:
    """Ajoute moyenne et écart-type glissants (fenêtre en secondes, mesures à 1 Hz).

    Une anomalie se voit souvent dans l'évolution du signal plutôt que sur un point isolé.
    Les premières lignes sont complétées avec la fenêtre partielle disponible.
    """
    out = df[SENSORS].copy()
    rolling = df[SENSORS].rolling(window, min_periods=1)
    means = rolling.mean().add_suffix("_mean")
    stds = rolling.std().fillna(0).add_suffix("_std")
    return pd.concat([out, means, stds], axis=1)
