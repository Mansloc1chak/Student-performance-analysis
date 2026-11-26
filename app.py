from pathlib import Path
import numpy as np
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Student Performance Analysis", page_icon="🎓", layout="wide")
DATA_PATH = Path(__file__).parent / "data" / "student_data.csv"
MARK_COLUMNS = ["Programming_Marks", "DBMS_Marks", "Networks_Marks", "Mathematics_Marks", "Web_Technology_Marks"]
REQUIRED_COLUMNS = ["Student_ID", "Name", "Gender", "Age", "Course", "Semester", "Attendance_Percent", "Study_Hours_Per_Day", *MARK_COLUMNS, "Internal_Marks", "Practical_Marks"]

st.title("🎓 Student Performance Analysis System")
st.caption("BCA Final Year Project | Academic analytics and student performance monitoring")

@st.cache_data
def load_sample():
    return pd.read_csv(DATA_PATH)

def prepare_data(data):
    data = data.copy()
    missing = [c for c in REQUIRED_COLUMNS if c not in data.columns]
    if missing:
        raise ValueError("CSV mein required columns missing hain: " + ", ".join(missing))
    numeric = ["Age", "Semester", "Attendance_Percent", "Study_Hours_Per_Day", *MARK_COLUMNS, "Internal_Marks", "Practical_Marks"]
    for col in numeric:
        data[col] = pd.to_numeric(data[col], errors="coerce")
    data = data.dropna(subset=["Student_ID", "Name", *numeric])
    data["Average_Marks"] = data[MARK_COLUMNS].mean(axis=1).round(1)
    data["Result"] = np.where(data["Average_Marks"] >= 40, "Pass", "Fail")
    data["Grade"] = pd.cut(data["Average_Marks"], bins=[-0.1, 39.9, 49.9, 59.9, 69.9, 79.9, 100], labels=["F", "D", "C", "B", "A", "A+"]).astype(str)
    data["Performance_Risk"] = np.where((data["Attendance_Percent"] < 65) | (data["Average_Marks"] < 45), "At Risk", "On Track")
    return data

def csv_template():
    return pd.DataFrame(columns=REQUIRED_COLUMNS).to_csv(index=False).encode("utf-8")

with st.sidebar:
    st.header("📂 Data Source")
    uploaded = st.file_uploader("Upload college student CSV", type=["csv"])
    st.download_button("⬇️ Download CSV Template", csv_template(), "student_data_template.csv", "text/csv", use_container_width=True)
    st.divider()
    st.header("🔎 Filters")

try:
    if uploaded is not None:
        data = prepare_data(pd.read_csv(uploaded))
        source_label = "Uploaded college dataset"
    else:
        data = prepare_data(load_sample())
        source_label = "Built-in illustrative sample data"
except Exception as exc:
    st.error(f"Data load error: {exc}")
    st.stop()

with st.sidebar:
    course = st.selectbox("Course", ["All"] + sorted(data["Course"].dropna().astype(str).unique().tolist()))
    semester = st.selectbox("Semester", ["All"] + sorted(data["Semester"].dropna().unique().tolist()))
    gender = st.selectbox("Gender", ["All"] + sorted(data["Gender"].dropna().astype(str).unique().tolist()))
    min_attendance = st.slider("Minimum attendance (%)", 0, 100, 0)

filtered = data.copy()
if course != "All": filtered = filtered[filtered["Course"] == course]
if semester != "All": filtered = filtered[filtered["Semester"] == semester]
if gender != "All": filtered = filtered[filtered["Gender"] == gender]
filtered = filtered[filtered["Attendance_Percent"] >= min_attendance]

st.caption(f"Data source: **{source_label}** · Showing {len(filtered)} of {len(data)} records")
if uploaded is None:
    st.info("Sample names and academic records are synthetic demonstration data, not real student records.")
if filtered.empty:
    st.warning("Selected filters ke liye koi student record nahi mila.")
    st.stop()

c1, c2, c3, c4 = st.columns(4)
c1.metric("Total Students", f"{len(filtered):,}")
c2.metric("Average Marks", f"{filtered['Average_Marks'].mean():.1f}/100")
c3.metric("Pass Percentage", f"{filtered['Result'].eq('Pass').mean()*100:.1f}%")
c4.metric("Average Attendance", f"{filtered['Attendance_Percent'].mean():.1f}%")

st.subheader("📊 Academic Overview")
left, right = st.columns(2)
with left:
    st.markdown("**Pass vs Fail Distribution**")
    result_counts = filtered["Result"].value_counts().reindex(["Pass", "Fail"], fill_value=0)
    st.bar_chart(result_counts)
with right:
    st.markdown("**Subject-wise Average Marks**")
    subject_avg = filtered[MARK_COLUMNS].mean().rename(lambda x: x.replace("_Marks", "").replace("_", " ")).to_frame("Average Marks")
    st.bar_chart(subject_avg)

left, right = st.columns(2)
with left:
    st.markdown("**Semester-wise Average Performance**")
    st.line_chart(filtered.groupby("Semester")["Average_Marks"].mean().sort_index())
with right:
    st.markdown("**Attendance vs Academic Performance**")
    scatter = filtered[["Attendance_Percent", "Average_Marks"]].rename(columns={"Attendance_Percent": "Attendance (%)", "Average_Marks": "Average Marks"})
    st.scatter_chart(scatter, x="Attendance (%)", y="Average Marks")

st.subheader("🏆 Top Performing Students")
st.dataframe(filtered.sort_values("Average_Marks", ascending=False).head(10)[["Student_ID","Name","Course","Semester","Average_Marks","Attendance_Percent","Result"]], use_container_width=True, hide_index=True)

st.subheader("🔍 Student Search")
search = st.text_input("Search by student name or ID", placeholder="e.g. BCA2026001 or Aarav")
if search.strip():
    found = filtered[filtered["Name"].astype(str).str.contains(search, case=False, na=False) | filtered["Student_ID"].astype(str).str.contains(search, case=False, na=False)]
    if found.empty: st.warning("No matching student found.")
    else: st.dataframe(found, use_container_width=True, hide_index=True)

st.subheader("⚠️ Students Requiring Attention")
risk = filtered[filtered["Performance_Risk"] == "At Risk"].sort_values("Average_Marks")
st.caption("Rule-based early-warning flag: attendance below 65% OR average subject marks below 45%. Not a guaranteed prediction.")
if risk.empty: st.success("Current filters mein koi at-risk student nahi mila.")
else: st.dataframe(risk[["Student_ID","Name","Course","Semester","Attendance_Percent","Average_Marks","Performance_Risk"]], use_container_width=True, hide_index=True)

st.subheader("📁 Complete Student Records")
st.dataframe(filtered.sort_values("Student_ID"), use_container_width=True, hide_index=True)
st.download_button("⬇️ Download filtered student data (CSV)", filtered.to_csv(index=False).encode("utf-8"), "student_performance_filtered.csv", "text/csv")
with st.expander("ℹ️ Project methodology"):
    st.write("Average marks = mean of five subjects. Pass threshold = 40%. At-risk rule = attendance below 65% OR average marks below 45%. Filters update all dashboard results. Uploaded CSV is processed in the app session and is not saved to the repository.")
st.caption("Student Performance Analysis System · BCA Final Year Project")
