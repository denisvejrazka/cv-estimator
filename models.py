from pydantic import BaseModel
from typing import Literal

EducationLevel = Literal["none", "high_school", "bachelor", "master", "doctor"]

# English translation from platy.cz
Area = Literal[
    "Administration",
    "Automotive Industry",
    "Banking",
    "Security and Protection",
    "Tourism, Hospitality, Catering and Hotel Management",
    "Chemical Industry",
    "Transport, Freight Forwarding and Logistics",
    "Wood Processing Industry",
    "Economics, Finance and Accounting",
    "Electrical Engineering and Energy",
    "Pharmaceutical Industry",
    "Mining, Metallurgy and Extraction",
    "Information Technology",
    "Leasing",
    "Human Resources and Recruitment",
    "Management",
    "Quality Management",
    "Marketing, Advertising and Public Relations",
    "Sales and Commerce",
    "Insurance",
    "General Support Work",
    "Law and Legislation",
    "Translation and Interpretation",
    "Services",
    "Construction and Real Estate",
    "Mechanical Engineering",
    "Public Administration and Local Government",
    "Engineering and Development",
    "Telecommunications",
    "Textile, Leather and Apparel Industry",
    "Arts and Culture",
    "Water Management, Forestry and Environmental Protection",
    "Executive Management",
    "Manufacturing",
    "Healthcare and Social Care",
    "Agriculture and Food Industry",
    "Customer Support",
    "Education, Training, Science and Research",
    "Journalism, Printing and Media",
]

class Applicant(BaseModel):
    skills: list[str]
    education_level: EducationLevel
    roles: list[str]
    area: Area
    last_role: str
    yrs_exp: int
    leader: bool
    role: str
    any_certifications: bool
    raw_text: str
    languages: list[str]