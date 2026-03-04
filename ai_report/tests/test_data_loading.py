from pathlib import Path

import pandas as pd

from src.data.load_parquet import build_feature_table, collect_samples


def test_collect_and_build_features(tmp_path: Path) -> None:
    cheater = tmp_path / "cheater"
    normal = tmp_path / "not_cheater"
    cheater.mkdir(parents=True)
    normal.mkdir(parents=True)

    cdf = pd.DataFrame({"attacker_X": [1.0, 2.0], "attacker_yaw_delta": [0.1, 0.2]})
    ndf = pd.DataFrame({"attacker_X": [0.1, 0.2], "attacker_yaw_delta": [0.01, 0.02]})

    cdf.to_parquet(cheater / "a.parquet")
    ndf.to_parquet(normal / "b.parquet")

    records = collect_samples(tmp_path, max_per_class=1, seed=1)
    x, y, _ = build_feature_table(records)

    assert len(records) == 2
    assert x.shape[0] == 2
    assert y.shape[0] == 2
    assert "attacker_X__mean" in x.columns
