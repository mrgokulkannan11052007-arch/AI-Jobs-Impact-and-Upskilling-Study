# AI Jobs Impact & Upskilling Study

A Streamlit dashboard project for exploring job-role AI-impact data, inspecting a CSV dataset, reviewing data quality, comparing roles, and exporting results.

## Important data note

`data/sample_jobs_ai_impact.csv` is an **illustrative demo dataset created for testing the application**. Its impact figures are not sourced labour-market statistics and must not be cited as factual research. Replace it with the approved/cited dataset for the final research submission.

## Quick start on Windows

1. Extract the ZIP into a folder such as `C:\Users\<you>\AI-Jobs-Upskilling-Complete`.
2. Install Python 3.10 or later if needed: https://www.python.org/downloads/windows/ (tick **Add python.exe to PATH** in the installer).
3. Double-click `run_windows.bat`. It installs dependencies and starts the app.
4. Open the `Local URL` printed in the terminal, usually `http://localhost:8501`.

### Run with terminal manually

Open PowerShell in this folder, then run:

```powershell
py -m pip install -r requirements.txt
py -m streamlit run app.py
```

If `py` is unavailable but `python` works, replace `py` with `python`.

## Features included

- Dashboard summary: role/category count, average AI impact, highest-impact role, skills field summary.
- Bar chart comparing impact scores across roles and a data-quality snapshot.
- CSV upload, automatic column-name detection, and manual column mapping.
- Dataset summary, data types, non-null count, missing count, unique values, and full table.
- CSV downloads for the data and column information.
- Quality checks for missing cells, duplicate rows, and non-numeric/out-of-range impact values.
- Impact distribution statistics and job-role aggregation.
- Downloadable text quality report and a final-submission checklist.
- Unit tests for key data-quality functions.

## Project structure

```text
AI-Jobs-Upskilling-Complete/
├── app.py
├── data_quality.py
├── requirements.txt
├── run_windows.bat
├── README.md
├── START_HERE.txt
├── VALIDATION_RESULTS.txt
├── data/
│   └── sample_jobs_ai_impact.csv
├── tests/
│   └── test_data_quality.py
└── docs/
    ├── WORKFLOW.md
    └── REPORT_TEMPLATE.md
```

## Workflow to finish your academic submission

1. Confirm the real dataset's source, publication date, license, geographic coverage, and variable definitions.
2. Keep the raw file unchanged and work on a copy for any cleaning.
3. Upload the approved data in the dashboard, map role/impact/skill columns, and inspect quality output.
4. Investigate missingness, duplicates, invalid values, inconsistent categories, and potential outliers. Do not silently delete rows; document each cleaning choice.
5. Export the quality report, data, and job-role analysis. Capture screenshots after loading the approved dataset.
6. Complete the report template with actual source references and observed results. State limitations.
7. Run tests with `py -m pytest -q` and verify the app starts cleanly. See `VALIDATION_RESULTS.txt` for checks completed during package review and limitations.

## Limitations and responsible interpretation

- An AI task-impact score is not the same as the probability that a job will disappear. Avoid job-loss claims from a single score.
- This app does not establish causal claims or forecast employment without a suitable validated model and supporting data.
- Uploaded CSV files are read in the current Streamlit session; this app does not intentionally persist them to disk.
- Validate all automatic column mappings before interpreting results.
