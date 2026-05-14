# cv-estimator

AI-powered CV analyzer that extracts structured data from a PDF/DOCX resume, scores the candidate's seniority (0-100), and estimates a monthly salary range in CZK based on the Czech market (https://www.platy.cz/platy reference data).

## Features

- Parses PDF and DOCX resumes (max 5 MB, 15 000 chars).
- Extracts structured applicant data (skills, education, roles, area, experience, languages, certifications) via OpenAI.
- Computes a transparent seniority score with a breakdown across skills, education, seniority, experience and other signals (leadership, languages, certifications).
- Estimates a salary range by combining the score with industry averages.
- Generates a Czech-language evaluation (strengths, gaps, salary rationale, growth advice).
- Available both as a **Streamlit web UI** and a **FastAPI HTTP service**.

## Project structure

| File | Purpose |
|------|---------|
| `app.py` | Streamlit UI |
| `api.py` | FastAPI HTTP endpoint |
| `parser.py` | File-size guard + text extraction + LLM extraction |
| `extractor.py` | Raw text extraction from PDF/DOCX |
| `llm_service.py` | OpenAI calls (extraction, key skills, judge, explanation) |
| `seniority_scorer.py` | Seniority scoring logic |
| `salary_scorer.py` | Salary estimation logic |
| `evaluator.py` | CLI sanity-check script: samples a resume from a CSV dataset and compares the system's score/salary against an LLM-as-judge baseline |
| `models.py` | Pydantic `Applicant` model |
| `cache.py` | Simple cache for role → key skills |

## Requirements

- Python 3.11+
- An OpenAI API key

## Setup

```bash
git clone https://github.com/denisvejrazka/cv-estimator
cd ai_estimator

python -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt
```

Create a `.env` file in the project root:

```
OPENAI_API_KEY=sk-...
RESUME_CSV_PATH=/absolute/path/to/Resume.csv
```

- `OPENAI_API_KEY` — required for all extraction and evaluation calls.
- `RESUME_CSV_PATH` — only needed for `evaluator.py`. Path to a CSV with a `Resume_str` column (e.g. the [Kaggle resume dataset](https://www.kaggle.com/datasets/snehaanbhawal/resume-dataset)).

## How to run

### Streamlit web app

```bash
streamlit run app.py
```

Open the URL shown in the terminal (default `http://localhost:8501`) and upload a CV.

### FastAPI service

```bash
uvicorn api:app --reload
```

Then call the endpoint:

```bash
curl -X POST -F "file=@cv.pdf" http://localhost:8000/analyze
```

Health check:

```bash
curl http://localhost:8000/health
```

The `/analyze` response contains the seniority score breakdown, salary range, a Czech-language explanation, and the parsed applicant data.

### CLI evaluation

Run the LLM-as-judge sanity checks on a random resume from `RESUME_CSV_PATH`:

```bash
python evaluator.py
```

It prints the system's seniority score and salary range, compares them against an LLM judge, and outputs the full Czech evaluation.
