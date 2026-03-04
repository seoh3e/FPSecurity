from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import random
from typing import Iterable

import pandas as pd

from src.features.window_features import featurize_window


@dataclass(frozen=True)
class SampleRecord:
    path: Path
    label: int


def iter_parquet_files(root: Path) -> Iterable[Path]:
    return root.rglob("*.parquet")


def collect_samples(
    data_dir: str | Path,
    cheater_dir_name: str = "cheater",
    not_cheater_dir_name: str = "not_cheater",
    max_per_class: int | None = None,
    seed: int = 42,
) -> list[SampleRecord]:
    data_root = Path(data_dir)
    cheater_root = data_root / cheater_dir_name
    not_cheater_root = data_root / not_cheater_dir_name

    if not cheater_root.exists() or not not_cheater_root.exists():
        raise FileNotFoundError(
            f"Expected class folders under {data_root}: {cheater_dir_name}, {not_cheater_dir_name}"
        )

    cheater_files = list(iter_parquet_files(cheater_root))
    normal_files = list(iter_parquet_files(not_cheater_root))

    rng = random.Random(seed)
    if max_per_class is not None:
        cheater_files = rng.sample(cheater_files, k=min(max_per_class, len(cheater_files)))
        normal_files = rng.sample(normal_files, k=min(max_per_class, len(normal_files)))

    records = [SampleRecord(path=p, label=1) for p in cheater_files] + [
        SampleRecord(path=p, label=0) for p in normal_files
    ]
    rng.shuffle(records)
    return records


def build_feature_table(records: list[SampleRecord]) -> tuple[pd.DataFrame, pd.Series, list[str]]:
    rows: list[dict[str, float]] = []
    labels: list[int] = []
    paths: list[str] = []

    for rec in records:
        df = pd.read_parquet(rec.path)
        feature_row = featurize_window(df)
        rows.append(feature_row)
        labels.append(rec.label)
        paths.append(str(rec.path))

    x = pd.DataFrame(rows)
    y = pd.Series(labels, name="label")
    return x, y, paths
