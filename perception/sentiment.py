"""
perception/sentiment.py

Rule-based frustration detection. This is a real, working implementation
(not a simulation) -- it just uses keyword/punctuation heuristics instead
of a trained classifier. Swap for a real HF text-classification pipeline
once you have internet access and want higher recall on subtler phrasing:

    from transformers import pipeline
    sentiment = pipeline("text-classification", model="distilbert-base-uncased-finetuned-sst-2-english")
"""
FRUSTRATION_MARKERS = [
    "urgent", "immediately", "asap", "right now", "unacceptable", "worst",
    "furious", "angry", "ridiculous", "disappointed", "again", "still not",
    "really bad", "this is bad",
]


def detect_frustration(text: str) -> dict:
    text_lower = text.lower()
    hits = [m for m in FRUSTRATION_MARKERS if m in text_lower]
    exclamation_count = text.count("!")
    score = min(1.0, 0.2 * len(hits) + 0.15 * exclamation_count)
    return {"frustration_score": round(score, 2), "markers_found": hits}
