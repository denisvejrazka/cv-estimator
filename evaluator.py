import pandas as pd
import llm_service
import seniority_scorer
from salary_scorer import get_salary_by_area, estimate_salary
from concurrent.futures import ThreadPoolExecutor
import os
from dotenv import load_dotenv

SALARY_THRESHOLD = 20_000
SENIORITY_THRESHOLD = 15
load_dotenv()
RESUME_CSV_PATH = os.getenv("RESUME_CSV_PATH")


def sanity_check_salary(system_min: int, system_max: int, judge_min: int, judge_max: int, threshold=SALARY_THRESHOLD) -> dict:
    min_diff = abs(system_min - judge_min)
    max_diff = abs(system_max - judge_max)
    return {
        "passed": min_diff <= threshold and max_diff <= threshold,
        "system": f"{system_min}-{system_max}",
        "judge":  f"{judge_min}-{judge_max}",
        "diff":   f"{min_diff}-{max_diff}",
    }


def sanity_check_seniority(system_score: int, judge_score: int, threshold=SENIORITY_THRESHOLD) -> dict:
    diff = abs(system_score - judge_score)
    return {
        "passed": diff <= threshold,
        "system": system_score,
        "judge":  judge_score,
        "diff":   diff,
    }


def evaluate():
    df = pd.read_csv(RESUME_CSV_PATH)
    random_resume = df["Resume_str"].sample(1).values[0]
    applicant = llm_service.extract_applicant(random_resume)
    key_skills = llm_service.get_key_skills(applicant.role)
    skills_score = seniority_scorer.score_skills(applicant.skills, key_skills)
    score = seniority_scorer.compute_seniority_score(applicant, skills_score)
    sal_min, sal_max = estimate_salary(applicant.area, score["total"])
    platy_avg = get_salary_by_area(applicant.area)["avg"]

    print(f"Role:            {applicant.role}")
    print(f"Area:            {applicant.area}")
    print(f"Seniority score: {score['total']}/100")
    print(f"Salary estimate: {sal_min} - {sal_max} CZK")
    print(f"platy.cz avg:    {platy_avg} CZK")
    print(f"Score breakdown: {score}")

    with ThreadPoolExecutor() as ex:
        f_sal = ex.submit(llm_service.judge_cv_salary, applicant, sal_min, sal_max, platy_avg)
        f_sen = ex.submit(llm_service.judge_cv_seniority, applicant, score["total"])
        llm_min, llm_max = f_sal.result()
        llm_seniority = f_sen.result()

    print()
    print("Salary sanity:   ", sanity_check_salary(sal_min, sal_max, llm_min, llm_max))
    print("Seniority sanity:", sanity_check_seniority(score["total"], llm_seniority))
    print()
    print(llm_service.explain_cv(applicant, (sal_min, sal_max), skills_score, key_skills, score))
    print(applicant.raw_text)


if __name__ == "__main__":
    evaluate()