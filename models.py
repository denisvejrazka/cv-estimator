from pydantic import BaseModel

class Applicant(BaseModel):
    role: str
    role_expected_skills: list[str]
    skills: list[str]
    languages: list[str]
    education_level: str
    leader: bool
    raw_text: str
    yrs_exp: int
    roles: list[str]
    last_role: str
    any_certifications: bool
