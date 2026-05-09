import llm_service
import parser
from sklearn.metrics.pairwise import cosine_similarity


applicant = parser.parse("jn_cv.pdf")

def score_education(applicant_education: str) -> int:
    mapping = {
        "none":        0,
        "high_school": 5,
        "bachelor":    10,
        "master":      12,
        "doctor":      15
    }
    return mapping.get(applicant_education, 0)


def score_seniority(applicant_roles: list[str]) -> int:
    if not applicant_roles:
        return 0
    
    best = 0
    
    for role in applicant_roles:
        role_lower = role.lower()
        
        if any(k in role_lower for k in ["ceo", "cto", "coo", "cfo", "cpo", "director"]):
            best = max(best, 25)
        elif any(k in role_lower for k in ["senior", "lead", "principal"]):
            best = max(best, 20)
        elif any(k in role_lower for k in ["junior"]):
            best = max(best, 10)
        elif any(k in role_lower for k in ["intern", "trainee"]):
            best = max(best, 5)
        else:
            best = max(best, 15)
    
    return best


def score_years_of_exp(applicant_yrs_exp: int) -> int:
    if applicant_yrs_exp <= 0:
        return 0
    if applicant_yrs_exp <= 2:
        return 10
    if applicant_yrs_exp <= 5:
        return 15
    if applicant_yrs_exp <= 10:
        return 20
    if applicant_yrs_exp <= 15:
        return 25
    return 30


def score_other(applicant_langs: list[str], applicant_leader: bool, applicant_certified: bool) -> int:
    score = 0
    
    if len(applicant_langs) > 1:
        score += 3
    if applicant_leader:
        score += 5
    if applicant_certified:
        score += 2
    
    return score


def score_skills(applicant_skills: list[str], role_skills: list[str], threshold: float = 0.55) -> dict:
    if not applicant_skills or not role_skills:
        return {"score": 0, "matched": [], "missing": []}

    applicant_vecs = llm_service.get_embeddings(applicant_skills)
    role_vecs = llm_service.get_embeddings(role_skills)

    sim_matrix = cosine_similarity(applicant_vecs, role_vecs)

    matched = []
    missing = []

    for i, role_skill in enumerate(role_skills):
        best_score = sim_matrix[:, i].max()
        best_match = applicant_skills[sim_matrix[:, i].argmax()]

        if best_score >= threshold:
            matched.append({
                "role_skill": role_skill,
                "matched_with": best_match,
                "similarity": round(float(best_score), 2)
            })
        else:
            missing.append(role_skill)

    raw_score = round(len(matched) / len(role_skills) * 100)
    scaled_score = round(raw_score * 20 / 100)  # 0-100 → 0-20

    return {
        "score": scaled_score,
        "matched": matched,
        "missing": missing
    }


def compute_seniority_score(applicant, skills_dict) -> dict:
    education   = score_education(applicant.education_level)
    seniority   = score_seniority(applicant.roles)
    experience  = score_years_of_exp(applicant.yrs_exp)
    other       = score_other(applicant.languages, applicant.leader, applicant.any_certifications)
    skills      = skills_dict["score"]

    total = education + seniority + experience + other + skills

    return {
        "total": total,          # 0-100
        "breakdown": {
            "skills":     skills,      # max 20
            "education":  education,   # max 15
            "seniority":  seniority,   # max 25
            "experience": experience,  # max 30
            "other":      other        # max 10
        }
    }
# print(applicant.education_level)
# print(compute_seniority_score(applicant=applicant, skills_dict=score_skills(applicant_skills=applicant.skills, role_skills=llm_service.get_key_skills(applicant.role))))