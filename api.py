from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
import tempfile, os
from parser import parse
from llm_service import get_key_skills, explain_cv
from seniority_scorer import score_skills, compute_seniority_score
from salary_scorer import estimate_salary

app = FastAPI(title="CV Estimator API")

@app.post("/analyze")
async def analyze_cv(file: UploadFile = File(...)):
    if not file.filename.endswith((".pdf", ".docx")):
        raise HTTPException(400, "Only PDF/DOCX")
    
    suffix = os.path.splitext(file.filename)[1]
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(await file.read())
        tmp_path = tmp.name

    try:
        applicant = parse(tmp_path)
        key_skills = get_key_skills(applicant.role)
        skills_dict = score_skills(applicant.skills, key_skills)
        score = compute_seniority_score(applicant, skills_dict)
        sal_min, sal_max = estimate_salary(applicant.area, score["total"])
        explanation = explain_cv(
            applicant, (sal_min, sal_max), skills_dict, key_skills, score
        )
    finally:
        os.unlink(tmp_path)

    return JSONResponse({
        "seniority_score": score,
        "salary_estimate": {"min": sal_min, "max": sal_max, "currency": "CZK"},
        "explanation": explanation,
        "applicant": applicant.model_dump(exclude={"raw_text"})
    })

@app.get("/health")
def health():
    return {"status": "ok"}