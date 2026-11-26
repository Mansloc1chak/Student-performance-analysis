import io
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(
    page_title="Student Performance Analysis",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

DATA_PATH = Path(__file__).parent / "data" / "student_data.csv"
MARK_COLUMNS = [
    "Programming_Marks", "DBMS_Marks", "Networks_Marks",
    "Mathematics_Marks", "Web_Technology_Marks",
]
REQUIRED_COLUMNS = [
    "Student_ID", "Name", "Gender", "Age", "Course", "Semester",
    "Attendance_Percent", "Study_Hours_Per_Day", *MARK_COLUMNS,
    "Internal_Marks", "Practical_Marks",
]

st.markdown("""
<style>
    .main {background-color: #f7f9fc;}
    [data-testid="stMetric"] {
        background: white; padding: 16px; border-radius: 12px;
        border: 1px solid #e7ebf2;
    }
    .block-container {padding-top: 1.5rem;}
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_sample():
    return pd.read_csv(DATA_PATH)

def prepare_data(data):
    data = data.copy()
    missing = [c for c in REQUIRED_COLUMNS if c not in data.columns]
    if missing:
        raise ValueError("CSV mein ye required columns missing hain: " + ", ".join(missing))
    numeric = ["Age", "Semester", "Attendance_Percent", "Study_Hours_Per_Day",
               *MARK_COLUMNS, "Internal_Marks", "Practical_Marks"]
    for col in numeric:
        data[col] = pd.to_numeric(data[col], errors="coerce")
    data = data.dropna(subset=["Student_ID", "Name", *numeric])
    data["Average_Marks"] = data[MARK_COLUMNS].mean(axis=1).round(1)
    data["Result"] = np.where(data["Average_Marks"] >= 40, "Pass", "Fail")
    data["Grade"] = pd.cut(
        data["Average_Marks"], bins=[-0.1, 39.9, 49.9, 59.9, 69.9, 79.9, 100],
        labels=["F", "D", "C", "B", "A", "A+"]
    ).astype(str)
    data["Performance_Risk"] = np.where(
        (data["Attendance_Percent"] < 65) | (data["Average_Marks"] < 45),
        "At Risk", "On Track"
    )
    return data

def csv_template():
    return pd.DataFrame(columns=REQUIRED_COLUMNS).to_csv(index=False).encode("utf-8")

st.title("🎓 Student Performance Analysis System")
st.caption("BCA Final Year Project | Academic analytics, student insights and performance monitoring")

with st.sidebar:
    st.header("📂 Data Source")
    uploaded = st.file_uploader("Upload your college student CSV", type=["csv"])
    st.caption("No file? The included sample dataset will be used.")
    st.download_button("⬇️ Download CSV Template", csv_template(),
                       "student_data_template.csv", "text/csv", use_container_width=True)
    st.divider()
    st.header("🔎 Filters")

try:
    if uploaded is not None:
        raw = pd.read_csv(uploaded)
        data = prepare_data(raw)
        st.sidebar.success("Uploaded dataset loaded")
        source_label = "Uploaded college dataset"
    else:
        data = prepare_data(load_sample())
        source_label = "Built-in illustrative sample data"
        st.sidebar.info("Using sample dataset")
except Exception as exc:
    st.error(f"Data load error: {exc}")
    st.stop()

with st.sidebar:
    courses = ["All"] + sorted(data["Course"].dropna().astype(str).unique().tolist())
    selected_course = st.selectbox("Course", courses)
    semesters = ["All"] + sorted(data["Semester"].dropna().unique().tolist())
    selected_semester = st.selectbox("Semester", semesters)
    genders = ["All"] + sorted(data["Gender"].dropna().astype(str).unique().tolist())
    selected_gender = st.selectbox("Gender", genders)
    min_attendance = st.slider("Minimum attendance (%)", 0, 100, 0)

filtered = data.copy()
if selected_course != "All":
    filtered = filtered[filtered["Course"] == selected_course]
if selected_semester != "All":
    filtered = filtered[filtered["Semester"] == selected_semester]
if selected_gender != "All":
    filtered = filtered[filtered["Gender"] == selected_gender]
filtered = filtered[filtered["Attendance_Percent"] >= min_attendance]

st.caption(f"Data source: **{source_label}** · Showing {len(filtered)} of {len(data)} records")
if uploaded is None:
    st.info("Sample names and academic records are synthetic and provided only for project demonstration. Replace them with authorized college data when required.")

if filtered.empty:
    st.warning("Selected filters ke liye koi student record nahi mila.")
    st.stop()

total = len(filtered)
avg = filtered["Average_Marks"].mean()
pass_rate = (filtered["Result"].eq("Pass").mean()) * 100
avg_att = filtered["Attendance_Percent"].mean()
topper = filtered.loc[filtered["Average_Marks"].idxmax()]

c1, c2, c3, c4 = st.columns(4)
c1.metric("Total Students", f"{total:,}")
c2.metric("Average Marks", f"{avg:.1f}/100")
c3.metric("Pass Percentage", f"{pass_rate:.1f}%")
c4.metric("Average Attendance", f"{avg_att:.1f}%")

st.subheader("📊 Academic Overview")
left, right = st.columns(2)
with left:
    result_counts = filtered["Result"].value_counts().rename_axis("Result").reset_index(name="Students")
    fig = px.pie(result_counts, names="Result", values="Students", hole=0.55,
                 title="Pass vs Fail Distribution", color="Result",
                 color_discrete_map={"Pass":"#16a34a", "Fail":"#ef4444"})
    st.plotly_chart(fig, use_container_width=True)
with right:
    subject_avg = filtered[MARK_COLUMNS].mean().rename_axis("Subject").reset_index(name="Average Marks")
    subject_avg["Subject"] = subject_avg["Subject"].str.replace("_Marks", "", regex=False).str.replace("_", " ")
    fig = px.bar(subject_avg, x="Subject", y="Average Marks", color="Average Marks",
                 title="Subject-wise Average Marks", text_auto=".1f",
                 color_continuous_scale="Blues", range_y=[0,100])
    st.plotly_chart(fig, use_container_width=True)

left, right = st.columns(2)
with left:
    sem_avg = filtered.groupby("Semester", as_index=False)["Average_Marks"].mean()
    fig = px.line(sem_avg, x="Semester", y="Average_Marks", markers=True,
                  title="Semester-wise Average Performance", range_y=[0,100])
    st.plotly_chart(fig, use_container_width=True)
with right:
    fig = px.scatter(filtered, x="Attendance_Percent", y="Average_Marks",
                     color="Performance_Risk", hover_name="Name",
                     hover_data=["Student_ID","Course","Semester"],
                     title="Attendance vs Academic Performance",
                     color_discrete_map={"At Risk":"#ef4444","On Track":"#2563eb"})
    st.plotly_chart(fig, use_container_width=True)

st.subheader("🏆 Top Performing Students")
top_students = filtered.sort_values("Average_Marks", ascending=False).head(10)
st.dataframe(top_students[["Student_ID","Name","Course","Semester","Average_Marks","Attendance_Percent","Result"]],
             use_container_width=True, hide_index=True)

st.subheader("🔍 Student Search")
search = st.text_input("Search by student name or ID", placeholder="e.g. BCA2026001 or Aarav")
if search.strip():
    matches = filtered[
        filtered["Name"].astype(str).str.contains(search, case=False, na=False) |
        filtered["Student_ID"].astype(str).str.contains(search, case=False, na=False)
    ]
    if matches.empty:
        st.warning("No matching student found.")
    else:
        st.dataframe(matches, use_container_width=True, hide_index=True)

st.subheader("⚠️ Students Requiring Attention")
risk = filtered[filtered["Performance_Risk"] == "At Risk"].sort_values("Average_Marks")
st.caption("Rule-based indicator: attendance below 65% OR average subject marks below 45%. It is an early-warning flag, not a guaranteed prediction.")
if risk.empty:
    st.success("Current filters mein koi at-risk student nahi mila.")
else:
    st.dataframe(risk[["Student_ID","Name","Course","Semester","Attendance_Percent","Average_Marks","Performance_Risk"]],
                 use_container_width=True, hide_index=True)

st.subheader("📁 Complete Student Records")
st.dataframe(filtered.sort_values("Student_ID"), use_container_width=True, hide_index=True)
csv_bytes = filtered.to_csv(index=False).encode("utf-8")
st.download_button("⬇️ Download filtered student data (CSV)", csv_bytes,
                   "student_performance_filtered.csv", "text/csv")

with st.expander("ℹ️ Project methodology"):
    st.write("""
    - Average marks are calculated as the mean of five subject marks.
    - Pass/Fail is determined using a 40% average-marks threshold.
    - Performance risk is flagged when attendance is below 65% or average marks are below 45.
    - Charts and KPIs are recalculated after sidebar filters are applied.
    - Uploaded CSV data is processed in the app session and is not saved into the repository.
    """)
st.caption("Student Performance Analysis System · BCA Final Year Project")
