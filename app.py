from __future__ import annotations

from pathlib import Path
import io
import pandas as pd
import streamlit as st
import plotly.express as px

from data_quality import build_quality_report, detect_column, parse_impact_values

BASE_DIR = Path(__file__).resolve().parent
SAMPLE_DATA = BASE_DIR / "data" / "sample_jobs_ai_impact.csv"

st.set_page_config(
    page_title="AI Jobs Impact & Upskilling Study",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
    .block-container {padding-top: 1.8rem; padding-bottom: 2.5rem;}
    [data-testid="stMetric"] {background: #f5f7fb; border: 1px solid #e6eaf2; padding: 14px 16px; border-radius: 12px;}
    .small-note {color: #64748b; font-size: 0.88rem;}
</style>
""", unsafe_allow_html=True)

st.title("📊 AI Jobs Impact & Upskilling Study")
st.caption("Explore job-role exposure, data quality, and potential upskilling priorities.")
st.warning(
    "Demo dataset notice: the bundled six-row dataset is illustrative sample data, not verified labour-market research. "
    "Replace it with a cited, project-approved dataset before reporting real-world conclusions.",
    icon="⚠️",
)

@st.cache_data(show_spinner=False)
def load_sample() -> pd.DataFrame:
    return pd.read_csv(SAMPLE_DATA)

with st.sidebar:
    st.header("Dataset")
    source = st.radio("Choose data source", ["Bundled sample dataset", "Upload a CSV"], index=0)
    uploaded = None
    if source == "Upload a CSV":
        uploaded = st.file_uploader("Upload project CSV", type=["csv"])
        st.caption("The uploaded file is processed in this session and is not saved by this app.")
    st.divider()
    st.header("About this project")
    st.write("Workflow: inspect → validate → analyse → document → submit.")
    st.caption("For academic use. Verify dataset provenance and methodology before drawing conclusions.")

if source == "Upload a CSV":
    if uploaded is None:
        st.info("Upload a CSV from the sidebar to begin. You can explore the included demo by selecting 'Bundled sample dataset'.")
        st.stop()
    try:
        raw_df = pd.read_csv(uploaded)
        dataset_name = uploaded.name
    except Exception as exc:
        st.error(f"Could not read this CSV. Check that it is a valid comma-separated file. Details: {exc}")
        st.stop()
else:
    try:
        raw_df = load_sample()
        dataset_name = SAMPLE_DATA.name
    except Exception as exc:
        st.error(f"Bundled sample data could not be loaded: {exc}")
        st.stop()

if raw_df.empty:
    st.error("This CSV contains no data rows. Upload a CSV with at least one row.")
    st.stop()
if len(raw_df.columns) == 0:
    st.error("No columns were found in this CSV. Please check the file and upload it again.")
    st.stop()

# Use a copy so display and analysis never mutate the source frame.
df = raw_df.copy()
all_columns = list(df.columns)
role_guess = detect_column(all_columns, ["job role", "job title", "occupation", "role", "job"])
impact_guess = detect_column(all_columns, ["ai task impact", "ai impact", "impact percent", "impact", "automation risk", "exposure"])
skill_guess = detect_column(all_columns, ["recommended skill", "skills", "skill", "upskilling", "training"])

with st.expander("Analysis column mapping", expanded=(source == "Upload a CSV")):
    st.write("The app auto-detects common column names. Check or adjust the mapping below for uploaded datasets.")
    c1, c2, c3 = st.columns(3)
    role_options = ["(None)"] + all_columns
    impact_options = ["(None)"] + all_columns
    skill_options = ["(None)"] + all_columns
    def selected_index(options, guess):
        return options.index(guess) if guess in options else 0
    role_col = c1.selectbox("Job-role column", role_options, index=selected_index(role_options, role_guess))
    impact_col = c2.selectbox("AI-impact column", impact_options, index=selected_index(impact_options, impact_guess))
    skill_col = c3.selectbox("Skills column", skill_options, index=selected_index(skill_options, skill_guess))

role_col = None if role_col == "(None)" else role_col
impact_col = None if impact_col == "(None)" else impact_col
skill_col = None if skill_col == "(None)" else skill_col
impact_values = parse_impact_values(df[impact_col]) if impact_col else None
valid_impact_mask = impact_values.notna() & impact_values.between(0, 100) if impact_values is not None else None
role_labels = None
if role_col:
    role_labels = df[role_col].astype("string").str.strip().replace("", pd.NA)

quality = build_quality_report(df, impact_col=impact_col, impact_values=impact_values)

# Overview metrics. Values outside 0–100 are shown in quality checks, but excluded
# from impact statistics so they cannot distort the averages or rankings.
st.subheader("Dashboard Overview")
k1, k2, k3, k4 = st.columns(4)
if role_labels is not None:
    role_count = int(role_labels.dropna().nunique())
else:
    role_count = int(len(df))
k1.metric("Job Roles / Categories", f"{role_count:,}")
if impact_values is not None and valid_impact_mask.any():
    avg_impact = float(impact_values[valid_impact_mask].mean())
    k2.metric("Average AI Impact", f"{avg_impact:.1f}%")
    if role_labels is not None:
        valid_roles = pd.DataFrame({"role": role_labels, "impact": impact_values}).loc[valid_impact_mask].dropna(subset=["role"])
        if not valid_roles.empty:
            role_means = valid_roles.groupby("role", as_index=False).agg(mean_impact=("impact", "mean"))
            high_row = role_means.loc[role_means["mean_impact"].idxmax()]
            k3.metric("Highest Impact Role", str(high_row["role"])[:28], f"{high_row['mean_impact']:.1f}% mean")
        else:
            k3.metric("Highest Impact Role", "No valid role labels")
    else:
        k3.metric("Highest Impact Role", "Map role column")
else:
    k2.metric("Average AI Impact", "N/A")
    k3.metric("Highest Impact Role", "No valid impact values")
if skill_col:
    skill_values = df[skill_col].dropna().astype(str).str.strip()
    most_common_skill = skill_values[skill_values.ne("")].mode()
    k4.metric("Skill Entries", f"{skill_values[skill_values.ne('')].nunique():,}", "unique values")
else:
    k4.metric("Skill Column", "Not mapped", "Set mapping above")

# Dashboard charts
chart_col1, chart_col2 = st.columns([1.45, 1])
with chart_col1:
    st.markdown("#### AI Impact Across Job Roles")
    if role_col and impact_values is not None:
        chart_df = pd.DataFrame({"Job Role": role_labels, "AI Impact (%)": impact_values}).loc[valid_impact_mask].dropna(subset=["Job Role"])
        if not chart_df.empty:
            chart_df = chart_df.groupby("Job Role", as_index=False).agg(**{"AI Impact (%)": ("AI Impact (%)", "mean")})
            chart_df = chart_df.sort_values("AI Impact (%)", ascending=False)
            fig = px.bar(chart_df, x="Job Role", y="AI Impact (%)", color="AI Impact (%)", color_continuous_scale="Blues", text_auto=".1f")
            fig.update_layout(xaxis_title="Job role", yaxis_title="Mean AI impact (%)", coloraxis_showscale=False, margin=dict(l=10, r=10, t=10, b=10))
            fig.update_xaxes(tickangle=-25)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No rows with both a valid 0–100 impact value and a job-role label are available. Check the column mapping and Data Quality tab.")
    else:
        st.info("Map a job-role column and a numeric AI-impact column to display this chart.")
with chart_col2:
    st.markdown("#### Data Quality Snapshot")
    quality_counts = pd.DataFrame({"Check": ["Missing cells", "Duplicate rows", "Invalid impact values"], "Count": [quality["missing_cells"], quality["duplicate_rows"], quality["invalid_impact_rows"]]})
    qfig = px.bar(quality_counts, x="Check", y="Count", color="Check", color_discrete_sequence=px.colors.qualitative.Safe)
    qfig.update_layout(showlegend=False, margin=dict(l=10, r=10, t=10, b=10), xaxis_title="", yaxis_title="Count")
    st.plotly_chart(qfig, use_container_width=True)

# Detail tabs
tab1, tab2, tab3, tab4 = st.tabs(["Dataset Explorer", "Data Quality", "Analysis", "Submission Guide"])
with tab1:
    st.subheader("Dataset Summary")
    a, b, c, d = st.columns(4)
    a.metric("Rows", f"{df.shape[0]:,}")
    b.metric("Columns", f"{df.shape[1]:,}")
    c.metric("Missing cells", f"{quality['missing_cells']:,}")
    d.metric("Duplicate rows", f"{quality['duplicate_rows']:,}")
    st.markdown("#### Column Information")
    col_info = pd.DataFrame({
        "Column": df.columns,
        "Data Type": [str(df[col].dtype) for col in df.columns],
        "Non-null Count": [int(df[col].notna().sum()) for col in df.columns],
        "Missing Count": [int(df[col].isna().sum()) for col in df.columns],
        "Unique Values": [int(df[col].nunique(dropna=True)) for col in df.columns],
    })
    st.dataframe(col_info, use_container_width=True, hide_index=True)
    st.markdown("#### Complete Dataset")
    st.dataframe(df, use_container_width=True, height=420)
    out = io.BytesIO()
    df.to_csv(out, index=False)
    st.download_button("⬇️ Download Data as CSV", data=out.getvalue(), file_name=f"{Path(dataset_name).stem}_export.csv", mime="text/csv")
    colout = col_info.to_csv(index=False).encode("utf-8")
    st.download_button("⬇️ Download Column Information", data=colout, file_name="column_information.csv", mime="text/csv")

with tab2:
    st.subheader("Data Quality Report")
    st.write("These checks describe the currently selected dataset; they do not automatically prove the dataset is accurate or representative.")
    qc1, qc2, qc3 = st.columns(3)
    qc1.metric("Missing cells", quality["missing_cells"])
    qc2.metric("Duplicate rows", quality["duplicate_rows"])
    qc3.metric("Invalid impact rows", quality["invalid_impact_rows"] if impact_col else "N/A")
    missing_table = pd.DataFrame({"Column": df.columns, "Missing Count": [int(df[c].isna().sum()) for c in df.columns]})
    missing_table["Missing %"] = (missing_table["Missing Count"] / max(len(df), 1) * 100).round(2)
    st.markdown("#### Missing values by column")
    st.dataframe(missing_table.sort_values("Missing Count", ascending=False), use_container_width=True, hide_index=True)
    if quality["duplicate_rows"]:
        st.markdown("#### Duplicate rows preview")
        st.dataframe(df[df.duplicated(keep=False)].head(100), use_container_width=True)
    if impact_col:
        st.markdown("#### Impact values outside the expected 0–100 range or not numeric")
        invalid_mask = impact_values.isna() | ~impact_values.between(0, 100)
        if invalid_mask.any():
            invalid = df.loc[invalid_mask].copy()
            invalid["Parsed impact value"] = impact_values.loc[invalid_mask]
            st.dataframe(invalid.head(100), use_container_width=True)
        else:
            st.success("All non-missing impact values are numeric and within 0–100.")
    st.markdown("#### Data type overview")
    dtype_table = df.dtypes.astype(str).value_counts().rename_axis("Data type").reset_index(name="Column count")
    st.dataframe(dtype_table, use_container_width=True, hide_index=True)
    report_lines = [
        "AI Jobs Impact & Upskilling Study — Data Quality Report",
        f"Dataset file: {dataset_name}",
        f"Rows: {len(df)}", f"Columns: {len(df.columns)}",
        f"Missing cells: {quality['missing_cells']}",
        f"Duplicate rows: {quality['duplicate_rows']}",
        f"Invalid impact rows: {quality['invalid_impact_rows'] if impact_col else 'N/A (no impact column mapped)'}",
        "Note: verify source, date, coverage and definitions before making real-world claims.",
    ]
    st.download_button("⬇️ Download Quality Report (TXT)", "\n".join(report_lines), file_name="data_quality_report.txt", mime="text/plain")

with tab3:
    st.subheader("Analysis")
    if impact_col and impact_values is not None and valid_impact_mask.any():
        valid_impacts = impact_values[impact_values.notna() & impact_values.between(0, 100)]
        s1, s2, s3, s4 = st.columns(4)
        s1.metric("Minimum", f"{valid_impacts.min():.2f}")
        s2.metric("Median", f"{valid_impacts.median():.2f}")
        s3.metric("Maximum", f"{valid_impacts.max():.2f}")
        s4.metric("Std. deviation", f"{valid_impacts.std():.2f}" if len(valid_impacts) > 1 else "N/A")
        excluded_impact_rows = int((impact_values.isna() | ~impact_values.between(0, 100)).sum())
        if excluded_impact_rows:
            st.info(f"{excluded_impact_rows} row(s) with missing, non-numeric, or out-of-range impact values are excluded from impact statistics. Review them in the Data Quality tab.")
        st.markdown("#### Impact distribution")
        hist = px.histogram(pd.DataFrame({"AI impact": valid_impacts}), x="AI impact", nbins=10, title="Distribution of AI impact values")
        st.plotly_chart(hist, use_container_width=True)
        if role_col:
            role_analysis = pd.DataFrame({"Job Role": role_labels, "AI Impact": impact_values})
            role_analysis = role_analysis.loc[role_analysis["AI Impact"].between(0, 100)].dropna(subset=["Job Role"])
            role_analysis = role_analysis.groupby("Job Role", as_index=False).agg(
                Mean_Impact=("AI Impact", "mean"), Records=("AI Impact", "size"),
            ).sort_values("Mean_Impact", ascending=False)
            st.markdown("#### Job-role comparison")
            st.dataframe(role_analysis, use_container_width=True, hide_index=True)
            st.download_button("⬇️ Download Job-role Analysis", role_analysis.to_csv(index=False).encode("utf-8"), file_name="job_role_analysis.csv", mime="text/csv")
    else:
        if impact_col:
            st.warning("No valid AI-impact values between 0 and 100 were found. Check the Data Quality tab and confirm the impact column's units.")
        else:
            st.info("To enable impact analysis, map a numeric AI impact/exposure column in 'Analysis column mapping'.")
    if skill_col:
        st.markdown("#### Skills / upskilling field overview")
        skills = df[skill_col].dropna().astype(str).str.strip()
        skills = skills[skills.ne("")]
        st.write(f"Non-empty skill entries: **{len(skills):,}**; unique values: **{skills.nunique():,}**")
        if not skills.empty:
            st.dataframe(skills.value_counts().head(20).rename_axis("Skill value").reset_index(name="Count"), use_container_width=True, hide_index=True)
    else:
        st.caption("Map a skill column to inspect skills/upskilling recommendations.")

with tab4:
    st.subheader("Final Workflow & Submission Checklist")
    checklist = [
        "Confirm data source, licence/permission, collection date, and documentation.",
        "Keep the raw dataset unchanged; clean a separate working copy if required.",
        "Review missing values, duplicates, types, range violations, and unusual categories.",
        "Check column mapping and validate the findings against the dataset's codebook.",
        "Export data-quality and analysis reports; capture dashboard screenshots.",
        "Write methods, limitations, results, and references in the project report.",
        "Run tests and verify the app starts from a fresh environment.",
    ]
    for item in checklist:
        st.checkbox(item, key="check_" + str(checklist.index(item)))
    st.markdown("#### Report outline")
    st.markdown("1. Abstract and problem statement\n2. Objectives\n3. Dataset source and variables\n4. Methodology and data cleaning\n5. Dashboard and analysis results\n6. Limitations and ethical considerations\n7. Conclusion and future improvements\n8. References")
    st.info("Do not state that AI will replace a role based on an illustrative impact score. Distinguish task exposure from actual job loss, and cite the source of each real-world dataset and claim.")

st.divider()
st.caption(f"Loaded: {dataset_name} · {df.shape[0]:,} rows × {df.shape[1]:,} columns · Interactive analysis is based on the currently selected dataset.")
