from __future__ import annotations
from typing import Iterable
import pandas as pd


def normalise_column_name(value: object) -> str:
    """Normalise a column label for robust matching."""
    return " ".join(str(value).strip().lower().replace("_", " ").replace("-", " ").split())


def detect_column(columns: Iterable[object], candidates: list[str]) -> str | None:
    """Return the first matching column, preferring exact normalised matches."""
    pairs = [(str(c), normalise_column_name(c)) for c in columns]
    wanted = [normalise_column_name(c) for c in candidates]
    for w in wanted:
        for original, norm in pairs:
            if norm == w:
                return original
    for w in wanted:
        wanted_words = set(w.split())
        for original, norm in pairs:
            norm_words = set(norm.split())
            if (len(wanted_words) > 1 and wanted_words.issubset(norm_words)) or w in norm or norm in w:
                return original
    return None


def parse_impact_values(values: pd.Series) -> pd.Series:
    """Parse numeric impact values, accepting strings such as '82%' and '1,200'.

    This helper does not infer or convert 0–1 fractions to percentages; confirm units
    in the dataset documentation before interpreting the results.
    """
    cleaned = (
        values.astype("string")
        .str.strip()
        .str.replace("%", "", regex=False)
        .str.replace(",", "", regex=False)
    )
    return pd.to_numeric(cleaned, errors="coerce")


def build_quality_report(df: pd.DataFrame, impact_col: str | None = None, impact_values: pd.Series | None = None) -> dict[str, int]:
    """Return basic, non-destructive quality counters for a dataframe."""
    missing = int(df.isna().sum().sum())
    duplicates = int(df.duplicated().sum())
    invalid_impact = 0
    if impact_col is not None:
        values = impact_values if impact_values is not None else parse_impact_values(df[impact_col])
        values = pd.to_numeric(values, errors="coerce")
        invalid_impact = int((values.isna() | ~values.between(0, 100)).sum())
    return {
        "rows": int(df.shape[0]),
        "columns": int(df.shape[1]),
        "missing_cells": missing,
        "duplicate_rows": duplicates,
        "invalid_impact_rows": invalid_impact,
    }
