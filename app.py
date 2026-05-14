import streamlit as st
import tempfile, os
from parser import parse
from llm_service import get_key_skills, explain_cv
from seniority_scorer import score_skills, compute_seniority_score
from salary_scorer import estimate_salary, get_salary_by_area

st.set_page_config(page_title="CV Estimator", layout="centered")
st.title("CV Estimator")

uploaded = st.file_uploader("Import CV (PDF/DOCX)", type=["pdf", "docx"])

if uploaded:
    with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded.name)[1]) as tmp:
        tmp.write(uploaded.read())
        tmp_path = tmp.name

    with st.spinner("Analyzing CV..."):
        applicant = parse(tmp_path)
        key_skills = get_key_skills(applicant.role)
        skills_dict = score_skills(applicant.skills, key_skills)
        score = compute_seniority_score(applicant, skills_dict)
        sal_min, sal_max = estimate_salary(applicant.area, score["total"])
        area_avg = get_salary_by_area(applicant.area)["avg"]
        explanation = explain_cv(applicant, (sal_min, sal_max), skills_dict, key_skills, score)

    os.unlink(tmp_path)

    col1, col2 = st.columns(2)
    col1.metric("Seniority Score", f"{score['total']} / 100")
    col2.metric("Salary Estimate", f"{sal_min:,} – {sal_max:,} CZK")

    with st.expander("Breakdown score"):
        for k, v in score["breakdown"].items():
            st.progress(v / {"skills":20,"education":15,"seniority":25,"experience":30,"other":10}[k], text=f"{k}: {v}")

    st.markdown("---")
    st.markdown(explanation)