"""
triage/classifier.py

Rule-based category and urgency tagging. This is real, working logic
(keyword scoring), not a simulation -- it's a legitimate simplification of
zero-shot classification for an MVP with no model access. Swap for a real
HF zero-shot-classification pipeline once you have internet access:

    from transformers import pipeline
    zero_shot = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")
    URGENCY_LABELS = ["low", "medium", "high", "critical"]
    CATEGORY_LABELS = ["billing", "bug", "how-to", "account"]
"""
CATEGORY_KEYWORDS = {
    "billing": ["charge", "charged", "refund", "payment", "credit card", "subscription", "invoice"],
    "bug": ["crash", "crashes", "error", "bug", "broken", "sync", "lost data", "disappeared"],
    "how-to": ["how do i", "how to", "where do i", "where can i"],
    "account": ["log in", "login", "logged in", "password", "account", "credentials"],
}

CRITICAL_MARKERS = ["compromised", "right now", "urgent", "fatal", "all my", "disappeared"]
HIGH_MARKERS = ["crash", "crashes", "every time", "broken"]


def _score_categories(text: str) -> dict:
    text_lower = text.lower()
    scores = {}
    for category, keywords in CATEGORY_KEYWORDS.items():
        scores[category] = sum(1 for kw in keywords if kw in text_lower)
    return scores


def triage(transcript: str, screenshot_text: str, frustration_score: float) -> dict:
    combined = f"{transcript} {screenshot_text}".strip()
    combined_lower = combined.lower()

    cat_scores = _score_categories(combined)
    best_category = max(cat_scores, key=cat_scores.get)
    if cat_scores[best_category] == 0:
        best_category = "other"
    total = sum(cat_scores.values()) or 1
    category_confidence = cat_scores.get(best_category, 0) / total if best_category != "other" else 0.3

    if any(m in combined_lower for m in CRITICAL_MARKERS) or frustration_score >= 0.7:
        urgency = "critical"
    elif any(m in combined_lower for m in HIGH_MARKERS) or frustration_score >= 0.4:
        urgency = "high"
    elif frustration_score >= 0.15:
        urgency = "medium"
    else:
        urgency = "low"

    return {
        "category": best_category,
        "category_confidence": round(category_confidence, 2),
        "urgency": urgency,
    }
