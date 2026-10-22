import pandas as pd
from data_quality import build_quality_report, detect_column, normalise_column_name, parse_impact_values


def test_normalise_column_name():
    assert normalise_column_name(" AI_Task-Impact ") == "ai task impact"


def test_detect_column_exact_and_partial():
    assert detect_column(["Job Role", "AI_Task_Impact"], ["job role"]) == "Job Role"
    assert detect_column(["AI_Task_Impact"], ["ai impact"]) == "AI_Task_Impact"


def test_build_quality_report_counts_missing_duplicates_and_invalid_impact():
    df = pd.DataFrame({"Job Role": ["A", "A", None], "Impact": [50, 50, 150]})
    impact = pd.to_numeric(df["Impact"], errors="coerce")
    report = build_quality_report(df, "Impact", impact)
    assert report["rows"] == 3
    assert report["columns"] == 2
    assert report["missing_cells"] == 1
    assert report["duplicate_rows"] == 1
    assert report["invalid_impact_rows"] == 1


def test_parse_impact_values_accepts_percent_and_thousands_separator():
    parsed = parse_impact_values(pd.Series(["82%", "1,200", "not a number", None]))
    assert parsed.iloc[0] == 82
    assert parsed.iloc[1] == 1200
    assert pd.isna(parsed.iloc[2])
    assert pd.isna(parsed.iloc[3])


def test_invalid_impact_report_counts_missing_and_out_of_range_values():
    df = pd.DataFrame({"Impact": ["82%", "bad", -1, 101, None]})
    report = build_quality_report(df, "Impact")
    assert report["invalid_impact_rows"] == 4
