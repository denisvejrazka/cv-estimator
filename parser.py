from extractor import extract_text
from llm_service import extract_applicant
from models import Applicant

def parse(file_path: str) -> Applicant:
    raw_text = extract_text(file_path)
    return extract_applicant(raw_text)
