"""
perception/sentiment.py

Rule-based frustration detection. This is a real, working implementation
(not a simulation) -- it just uses keyword/punctuation heuristics instead
of a trained classifier. Swap for a real HF text-classification pipeline
once you have internet access and want higher recall on subtler phrasing:

    from transformers import pipeline
    sentiment = pipeline("text-classification", model="distilbert-base-uncased-finetuned-sst-2-english")

Known fix (see GitHub issue #4): noisy simulated ASR can truncate words to
their first few characters plus "..." (e.g. "urgent" -> "urge..."), which
made exact substring matching miss real urgency markers. _fuzzy_contains
below matches a marker word against a truncated word if the truncated word
is a genuine prefix of it, so "urge..." still matches "urgent".
"""
import re

FRUSTRATION_MARKERS = [
    "urgent", "immediately", "asap", "right now", "unacceptable", "worst",
    "furious", "angry", "ridiculous", "disappointed", "again", "still not",
    "really bad", "this is bad",
]


def _fuzzy_contains(text_lower: str, marker: str) -> bool:
    if marker in text_lower:
        return True
    text_words = re.findall(r"[a-z']+(?:\.\.\.)?", text_lower)
    for marker_word in marker.split():
        matched = False
        for word in text_words:
            if word.endswith("..."):
                core = word[:-3]
                if core and marker_word.startswith(core) and len(core) >= max(3, len(marker_word) - 3):
                    matched = True
                    break
            elif word == marker_word:
                matched = True
                break
        if not matched:
            return False
    return True


def detect_frustration(text: str) -> dict:
    text_lower = text.lower()
    hits = [m for m in FRUSTRATION_MARKERS if _fuzzy_contains(text_lower, m)]
    exclamation_count = text.count("!")
    score = min(1.0, 0.2 * len(hits) + 0.15 * exclamation_count)
    return {"frustration_score": round(score, 2), "markers_found": hits}