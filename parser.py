from extractor import extract_text
from llm_service import extract_applicant
from models import Applicant
import os

MAX_FILE_SIZE_MB = 5
MAX_CHARS = 15_000

def parse(file_path: str) -> Applicant:
    file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
    if file_size_mb > MAX_FILE_SIZE_MB:
        raise ValueError(f"File is too large ({file_size_mb:.1f} MB), max is {MAX_FILE_SIZE_MB} MB")

    raw_text = extract_text(file_path)

    if len(raw_text) > MAX_CHARS:
        raise ValueError(f"File contains too much text ({len(raw_text):,} chars), max is {MAX_CHARS:,}")

    return extract_applicant(raw_text)