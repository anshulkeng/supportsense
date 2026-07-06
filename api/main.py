"""
api/main.py

Run with: uvicorn api.main:app --reload --port 8001
"""
import uuid
from fastapi import FastAPI
from pydantic import BaseModel
from agents.graph import run_case
from ingestion.case_generator import generate_cases

app = FastAPI(title="SupportSense")
CASES: dict = {}


class CaseRequest(BaseModel):
    true_transcript: str
    audio_quality: str = "clear"
    has_screenshot: bool = False
    true_screenshot_text: str = ""
    screenshot_quality: str = "clear"
    channel: str = "chat"


@app.get("/health")
def health():
    return {"ready": True}


@app.post("/case")
def create_case(req: CaseRequest):
    case_id = str(uuid.uuid4())
    case = {
        "case_id": case_id,
        "true_transcript": req.true_transcript,
        "audio_quality": req.audio_quality,
        "has_screenshot": req.has_screenshot,
        "true_screenshot_text": req.true_screenshot_text,
        "screenshot_quality": req.screenshot_quality,
        "channel": req.channel,
    }
    result = run_case(case)
    CASES[case_id] = result
    return {"case_id": case_id, "status": "processed"}


@app.get("/case/{case_id}")
def get_case(case_id: str):
    return CASES.get(case_id, {"error": "not found"})


@app.get("/demo_cases")
def demo_cases(n: int = 5):
    """Convenience endpoint: runs n synthetic golden cases through the pipeline."""
    cases = generate_cases(n=n, seed=123)
    return [{"input": c, "result": run_case(c)} for c in cases]
