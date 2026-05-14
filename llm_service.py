from openai import OpenAI
from dotenv import load_dotenv
from models import Applicant
import json
import numpy as np
from datetime import datetime
import cache

now = datetime.now()
year = now.year
month = now.month
load_dotenv()
client = OpenAI()

# Extract the raw CV text to Pydantic Applicant model
def extract_applicant(raw_text: str) -> Applicant:
    try:
        response = client.responses.parse(
            model="gpt-5.4-nano-2026-03-17",
            input=[
            {
                "role": "system",
                "content": f"""You are a precise HR data extraction engine. Extract structured data from the provided CV text.
                
GLOBAL RULES:
- Always respond in English, regardless of the original CV language.
- Extract facts explicitly where possible, but apply inference and normalization STRICTLY as defined in the field instructions below.

FIELD INSTRUCTIONS:

- skills: Extract ALL professional skills, specialized tools, technologies, and methodologies as short items (1-3 words).
  Rule: INFER implicit professional competencies from mentioned activities or tools.
  EXAMPLES ACROSS DOMAINS:
  - IT: 'React' implies 'JavaScript', 'Blazor' implies '.NET'.
  - HR: 'Hiring' implies 'Recruitment' and 'Sourcing'. 'Succession planning' implies 'Talent Management'.
  - SALES: 'Cashier' implies 'POS Systems' and 'Cash Handling'. 'Merchandising' implies 'Inventory Management'.
  - MANUAL/CLEANING: 'Industrial cleaning' implies 'Chemical Safety' and 'Floor Care Equipment'. 'Room turnover' implies 'Sanitization'.
  GOOD Output: ['Recruitment', 'LinkedIn Recruiter', 'Labor Law', 'Customer Service', 'POS Systems', 'Chemical Safety']

- education_level: Choose EXACTLY ONE: 'none', 'high_school', 'bachelor', 'master', 'doctor'.
  CRITICAL RULE: Do NOT use 'master' for MBA (Master of Business Administration) or other purely professional degrees. If the highest degree is an MBA, fall back to the candidate's highest academic degree (e.g., evaluate as 'bachelor').

- roles: List ALL job titles the candidate has held in their career, ordered most recent first.

- last_role: The most recent job title, translated to English, keeping the seniority level.
  Example: 'Junior C# Developer', 'Senior Marketing Manager', 'VP of Product'.

- role: The canonical, normalized version of the MOST RECENT job title.
  Normalization Rules:
  1. REMOVE seniority/level (Junior, Senior, Lead, Principal, Chief, Head of).
  2. REMOVE personal names or internal company jargon.
  3. KEEP ecosystem-defining tech, but REMOVE specific tools/frameworks.
  Examples: 
  'Senior Python Developer' -> 'Python Developer'
  'Junior C# Software Engineer' -> 'C# Developer'
  'Lead React Frontend Engineer' -> 'Frontend Developer'
  'Junior AWS Cloud Architect' -> 'Cloud Architect'
  'SAP FI/CO Consultant' -> 'SAP Consultant'
  'Head of Performance Marketing' -> 'Marketing Manager'

- area: The primary industry or domain of the candidate. Choose EXACTLY ONE from the Allowed List.
  Allowed List: 'Administration', 'Automotive Industry', 'Banking', 'Security and Protection', 'Tourism, Hospitality, Catering and Hotel Management', 'Chemical Industry', 'Transport, Freight Forwarding and Logistics', 'Wood Processing Industry', 'Economics, Finance and Accounting', 'Electrical Engineering and Energy', 'Pharmaceutical Industry', 'Mining, Metallurgy and Extraction', 'Information Technology', 'Leasing', 'Human Resources and Recruitment', 'Management', 'Quality Management', 'Marketing, Advertising and Public Relations', 'Sales and Commerce', 'Insurance', 'General Support Work', 'Law and Legislation', 'Translation and Interpretation', 'Services', 'Construction and Real Estate', 'Mechanical Engineering', 'Public Administration and Local Government', 'Engineering and Development', 'Telecommunications', 'Textile, Leather and Apparel Industry', 'Arts and Culture', 'Water Management, Forestry and Environmental Protection', 'Executive Management', 'Manufacturing', 'Healthcare and Social Care', 'Agriculture and Food Industry', 'Customer Support', 'Education, Training, Science and Research', 'Journalism, Printing and Media'.
  
  EVALUATION ALGORITHM FOR 'area' (Apply in strict order):
  STEP 1: Is the most recent role C-level (CEO, CTO, CFO, COO, CPO, CRO) or VP? 
          If YES -> Output 'Executive Management'. Stop.
  STEP 2: Is the most recent role "Director", "Head of", or "Manager" WITH org-wide or P&L responsibility? 
          If YES -> Output 'Management'. Stop.
  STEP 3: Otherwise, determine the candidate's PRIMARY DOMAIN based on the aggregate of their education, core skills, and majority of daily tasks.
          CRITICAL RULE: Do NOT classify based on isolated tools or single projects (e.g., using accounting software or creating a simple database does NOT make someone 'Information Technology').
          Examples: 
          - 'Grants Manager' with a finance/banking background -> 'Economics, Finance and Accounting'
          - 'Account Executive' -> 'Sales and Commerce'
          - 'Aviation Technician' doing purely HR/Budgeting -> 'Management'
          - 'Java Backend Developer' -> 'Information Technology'

- yrs_exp: Total years of work experience (integer). Calculate up to {month}/{year} if currently employed.

- leader: Boolean (true/false). Set to true if the candidate facilitated meetings, managed projects, supervised people, coordinated teams, or mentored others (does not require explicit "lead" title).

- any_certifications: Boolean (true/false) based on whether certifications are mentioned.

- languages: List of languages spoken by the candidate.

- raw_text: Copy the exact raw text of the CV."""
            },
            {
                "role": "user",
                "content": raw_text
            },
        ],
            text_format=Applicant
        )

        return response.output_parsed
    
    except Exception as e:
        raise ValueError(f"Failed to extract application data: {e}")


# Get key skills for the recognized Role
def get_key_skills(role: str) -> list[str]:
    skills_cache = cache.load_cache()

    if role in skills_cache:
        return skills_cache[role]
    
    response = client.responses.create(
        model="gpt-5-nano-2025-08-07",
        input=[
            {
                "role": "system",
                "content": "Always respond in English."
            },
            {
                "role": "user", 
                "content": (
                    f"List exactly 10 essential skills for: {role}. "
                    f"Rules: short (1-3 words), specific and practical, no duplicates. "
                    f"Examples of good format: 'Python', 'Team Leadership', 'Budget Planning', 'Soil Analysis'. "
                    f"JSON array only, nothing else."
                )
            }
        ]
    )

    skills = json.loads(response.output_text)
    skills_cache[role] = skills
    cache.save_cache(skills_cache)
    return skills


def get_embeddings(texts: list[str]) -> np.ndarray:
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=texts
    )
    return np.array([item.embedding for item in response.data])


# LLM as judge for seniority
def judge_cv_seniority(applicant: Applicant, seniority_score: int) -> int:
    response = client.responses.create(
        model="gpt-5-mini-2025-08-07",
        input=[
            {
                "role": "system",
                "content": "You are an expert HR evaluator. Rate candidate seniority 0-100. Return only a single integer."
            },
            {
                "role": "user",
                "content": f"""
                    Role: {applicant.role}
                    Area: {applicant.area}
                    Last role: {applicant.last_role}
                    All roles: {', '.join(applicant.roles)}
                    Years of experience: {applicant.yrs_exp}
                    Education: {applicant.education_level}
                    Skills: {', '.join(applicant.skills)}
                    Languages: {', '.join(applicant.languages)}
                    Leader: {applicant.leader}
                    Certifications: {applicant.any_certifications}

                    System score: {seniority_score}/100
                    The system score is composed of:
                    - Skills match (0-20)
                    - Education level (0-15): none=0, high_school=5, bachelor=10, master=12, doctor=15
                    - Seniority of roles (0-25): intern=5, junior=10, medior=15, senior=20, director/C-level=25
                    - Years of experience (0-30): 0=0, 1-2=10, 3-5=15, 6-10=20, 11-15=25, 15+=30
                    - Other (0-10): multiple languages=3, leadership=5, certifications=2

                    Full CV:
                    {applicant.raw_text}
                    """
            }
        ]
    )
    return int(response.output_text.strip())


# LLM as judge for salary
def judge_cv_salary(applicant: Applicant, salary_min: int, salary_max: int, area_avg: int) -> tuple[int, int]:
    response = client.responses.create(
        model="gpt-5-mini-2025-08-07",
        input=[
            {
                "role": "system",
                "content": "You are an expert HR evaluator. Estimate the salary range for this candidate in Czech Republic in CZK. Return only two integers separated by a dash, e.g. 60000-80000."
            },
            {
                "role": "user",
                "content": f"""
                    Role: {applicant.role}
                    Area: {applicant.area}
                    Last role: {applicant.last_role}
                    All roles: {', '.join(applicant.roles)}
                    Years of experience: {applicant.yrs_exp}
                    Education: {applicant.education_level}
                    Skills: {', '.join(applicant.skills)}
                    Languages: {', '.join(applicant.languages)}
                    Leader: {applicant.leader}
                    Certifications: {applicant.any_certifications}

                    Area average salary (platy.cz): {area_avg} CZK
                    System estimate: {salary_min}-{salary_max} CZK

                    Full CV:
                    {applicant.raw_text}
                    """
            }
        ]
    )
    min_s, max_s = response.output_text.strip().split("-")
    return int(min_s), int(max_s)


# Explanation and +30% salary increase recommendation
def explain_cv(applicant: Applicant, salary_range: tuple[int, int], skills: dict, role_skills: list[str], seniority_score: dict) -> str:
    breakdown = seniority_score["breakdown"]
    total = seniority_score["total"]
    salary_low, salary_high = salary_range
    matched_skills = [m["role_skill"] for m in skills.get("matched", [])]
    missing_skills = skills.get("missing", [])

    response = client.responses.create(
        model="gpt-5-mini-2025-08-07",
        input=[
            {
                "role": "system",
                "content": "You are an expert HR analyst and career coach. Based on the structured candidate data below, provide a professional evaluation in Czech language."
            },
            {
                "role": "user",
                "content": f"""
                    ## Candidate Profile
                    - Field / Area: {applicant.area}
                    - Education: {applicant.education_level}
                    - Years of experience: {applicant.yrs_exp}
                    - Roles held: {', '.join(applicant.roles)}
                    - Languages: {', '.join(applicant.languages)}
                    - Leadership experience: {applicant.leader}
                    - Certifications: {applicant.any_certifications}
                    - Skills: {', '.join(applicant.skills)}

                    ## Scoring Results
                    | Category   | Score | Max |
                    |------------|-------|-----|
                    | Skills     | {breakdown['skills']}     | 20  |
                    | Education  | {breakdown['education']}  | 15  |
                    | Seniority  | {breakdown['seniority']}  | 25  |
                    | Experience | {breakdown['experience']} | 30  |
                    | Other      | {breakdown['other']}      | 10  |
                    | **TOTAL**  | **{total}**               | 100 |

                    ## Skill Match
                    - Required: {', '.join(role_skills)}
                    - Matched:  {', '.join(matched_skills) if matched_skills else 'none'}
                    - Missing:  {', '.join(missing_skills) if missing_skills else 'none'}

                    ## Salary Estimate
                    - Range: {salary_low:,} – {salary_high:,} CZK / month

                    ---

                    Odpověz v tomto formátu:

                    ### Hodnocení skóre
                    Vysvětli, proč kandidát dostal {total}/100. Popiš jednotlivé složky.

                    ### Silné stránky
                    3 konkrétních silných stránek kandidáta.

                    ### Slabiny a mezery
                    3 oblasti, kde kandidát zaostává nebo mu chybí zkušenosti.

                    ### Zdůvodnění mzdy
                    Proč je odhadovaný plat {salary_low:,} – {salary_high:,} CZK / měsíc.

                    ### Doporučení pro růst (+30 % mzdy)
                    1 - 2 věty jak zvýšit mzdu.
                    """
            }
        ]
    )

    return response.output_text