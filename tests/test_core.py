import numpy as np
import pandas as pd

from maintenai.anomaly.features import add_rolling_features
from maintenai.anomaly.model import AnomalyDetector
from maintenai.assistant.ingest import chunk_text
from maintenai.config import SENSORS


def make_signal(n: int, shift: float = 0.0, seed: int = 0) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    idx = pd.date_range("2020-01-01", periods=n, freq="s")
    return pd.DataFrame(rng.normal(shift, 1.0, (n, len(SENSORS))), index=idx, columns=SENSORS)


def test_rolling_features_shape():
    feats = add_rolling_features(make_signal(50), window=5)
    assert feats.shape == (50, 3 * len(SENSORS))
    assert not feats.isna().any().any()


def test_detector_flags_shifted_data():
    model = AnomalyDetector(window=5).fit(make_signal(500))
    normal_rate = model.predict(make_signal(300, seed=1)).mean()
    shifted_rate = model.predict(make_signal(300, shift=6.0, seed=2)).mean()
    assert normal_rate < 0.1
    assert shifted_rate > 0.9


def test_chunk_text_overlap_and_coverage():
    text = "mot " * 1000
    chunks = chunk_text(text, max_chars=300, overlap=50)
    assert all(len(c) <= 300 for c in chunks)
    assert chunks[-1].endswith("mot")
    assert chunk_text("   ") == []
