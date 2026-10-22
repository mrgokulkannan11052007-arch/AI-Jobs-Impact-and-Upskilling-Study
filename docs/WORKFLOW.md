# Project Workflow

## Completed in this package

1. **App launch** — Streamlit entry point and Windows launcher are included.
2. **Dashboard** — KPI cards, role impact chart, and a data-quality snapshot.
3. **CSV ingestion** — bundled sample data or user-selected CSV.
4. **Dataset inspection** — row/column summary, types, missing counts, unique counts, complete table, CSV downloads.
5. **Quality checks** — missing cells, duplicate rows, non-numeric impact values, and values outside 0–100.
6. **Analysis** — impact distribution, descriptive statistics, job-role comparison and skill-field summary.
7. **Exports** — dataset, column metadata, job-role summary and text data-quality report.
8. **Basic tests** — pytest coverage for column matching and quality counters.
9. **Documentation** — run instructions, workflow, report outline and limitations.

## Must be verified with the real project dataset before submission

- The source and usage permission/licence for the actual dataset.
- Column mapping and units (confirm whether impact values are 0–1 or 0–100 and adjust before analysis if needed).
- Whether missing values or duplicates should be corrected, retained, or excluded; document the rationale.
- Findings, figures, and conclusions against reliable sources.
- Screenshot evidence of the app using the approved dataset.

## Final validation steps

```powershell
py -m pip install -r requirements.txt
py -m pytest -q
py -m streamlit run app.py
```

Then use the app to upload the approved dataset and verify all tabs, charts and download buttons.
