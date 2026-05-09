import pandas as pd
import llm_service
import seniority_scorer

# credit to: https://www.kaggle.com/datasets/snehaanbhawal/resume-dataset
df = pd.read_csv("/Users/denisvejrazka/Downloads/archive/Resume/Resume.csv")

random_resume = df["Resume_str"].sample(1).values[0]
applicant = llm_service.extract_applicant(random_resume)

print(applicant.raw_text)
print(seniority_scorer.compute_seniority_score(
    applicant=applicant, 
    skills_dict=seniority_scorer.score_skills(applicant_skills=applicant.skills, role_skills=llm_service.get_key_skills(applicant.role))))