from openai import OpenAI
from dotenv import load_dotenv
from models import Applicant
import json
import numpy as np

load_dotenv()

client = OpenAI()

def extract_applicant(raw_text: str) -> Applicant:
    try:
        response = client.responses.parse(
            model="gpt-5.4-nano-2026-03-17",
            input=[
            {
                "role": "system",
                "content": """You are a professional HR analyst. Extract structured data from CV text.
                
                RULES:
                - Always respond in English regardless of CV language
                - Extract only what is explicitly stated; do not invent or assume

                FIELD INSTRUCTIONS:
                - skills: Extract ALL specific technologies, tools, and frameworks as individual short items (1-3 words).
                Infer implicit skills — e.g. 'Blazor' implies '.NET', 'React.js' implies 'JavaScript'.
                BAD: ['C#: Blazor, WinForms'] GOOD: ['C#', 'Blazor', 'WinForms', '.NET']

                - education_level: Use exactly one of: 'none', 'high_school', 'bachelor', 'master', 'doctor'

                - roles: List all job titles the candidate has held, most recent first.

                - yrs_exp: Total years of professional experience as an integer. 
                If still employed, calculate up to 2025.
                - leader: true if candidate facilitated meetings, managed projects, 
                supervised people, coordinated teams, or mentored others.
                Not only explicit "team lead" titles.
                - last_role: Most recent job title only."""
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


def get_key_skills(role: str) -> list[str]:
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

    return json.loads(response.output_text)


def get_embeddings(texts: list[str]) -> np.ndarray:
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=texts
    )
    return np.array([item.embedding for item in response.data])





