# Student Performance Analysis System

BCA Final Year Project built with Python, Streamlit, Pandas, NumPy and Plotly.

## Features
- Student records with name, ID, course, semester, gender, age and attendance
- Subject-wise marks and calculated average/result/grade
- KPI dashboard: total students, average marks, pass percentage, attendance
- Course, semester, gender and attendance filters
- Subject and semester charts, attendance-vs-marks scatter plot
- Top 10 students, student search and at-risk student list
- Upload your own CSV and download filtered records
- CSV template included in the app

## Important data note
`data/student_data.csv` contains 150 **synthetic illustrative records** with fictional names and generated academic details. They are not real student records and must not be represented as collected college data. For actual institutional analysis, upload a CSV containing authorized data and follow your college's privacy rules.

## Run locally
Python 3.10+ recommended.

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Deploy on Streamlit Community Cloud
1. Create a GitHub repository, e.g. `student-performance-analysis`.
2. Upload all files/folders from this project. Keep `app.py`, `requirements.txt`, and `data/` at the repository root.
3. Open https://share.streamlit.io/ and sign in with GitHub.
4. Choose **Create app**, select your repository and branch, and set Main file path to `app.py`.
5. Click **Deploy**.

Streamlit documentation: https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app

## CSV upload format
The uploaded CSV must contain these columns:
`Student_ID, Name, Gender, Age, Course, Semester, Attendance_Percent, Study_Hours_Per_Day, Programming_Marks, DBMS_Marks, Networks_Marks, Mathematics_Marks, Web_Technology_Marks, Internal_Marks, Practical_Marks`

Marks should be numeric and on a 0–100 scale for subject columns. Internal and practical marks are included for student records; dashboard average is calculated from the five subject columns.

## Project scope and limitations
The at-risk indicator is a transparent rule-based early warning (attendance < 65% or average subject marks < 45), not a trained machine-learning model and not a guarantee of future outcomes. This is appropriate to explain honestly in a student project viva.
