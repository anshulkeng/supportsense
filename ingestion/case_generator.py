"""
ingestion/case_generator.py

Generates synthetic support cases with KNOWN ground truth (true category,
true urgency, true relevant KB topic). This lets us validate the whole
pipeline's routing accuracy and retrieval accuracy against a known answer,
the same way execution/target_agent.py let AgentAudit validate its causal
engine. In production this generator is replaced by real incoming tickets.
"""
import random
import uuid

CASE_TEMPLATES = [
    # (true_category, true_urgency, true_kb_topic, base_transcript, has_screenshot, screenshot_hint)
    ("billing", "medium", "double_charge_refund",
     "I think I was charged twice for my subscription this month", False, ""),
    ("billing", "low", "update_payment_method",
     "How do I update my credit card on file", False, ""),
    ("bug", "high", "export_crash",
     "The app crashes every time I try to export my report", True, "ERR_EXPORT_0x5A"),
    ("bug", "critical", "data_loss",
     "All my saved data disappeared after the last update this is really bad", True, "ERR_SYNC_FATAL"),
    ("how-to", "low", "reset_password",
     "How do I reset my password I forgot it", False, ""),
    ("how-to", "low", "change_email",
     "Where do I go to change my account email address", False, ""),
    ("account", "medium", "cannot_login",
     "I can't log into my account it keeps saying invalid credentials", True, "ERR_AUTH_401"),
    ("account", "critical", "account_compromised",
     "Someone else is logged into my account right now this is urgent", False, ""),
]


def generate_cases(n: int = 120, seed: int = 42) -> list[dict]:
    rng = random.Random(seed)
    cases = []
    for i in range(n):
        template = rng.choice(CASE_TEMPLATES)
        true_category, true_urgency, true_kb_topic, transcript, has_screenshot, hint = template
        cases.append({
            "case_id": str(uuid.uuid4())[:8],
            "true_category": true_category,
            "true_urgency": true_urgency,
            "true_kb_topic": true_kb_topic,
            "true_transcript": transcript,
            "audio_quality": rng.choice(["clear", "clear", "noisy"]),  # skew toward clear
            "has_screenshot": has_screenshot,
            "true_screenshot_text": hint,
            "screenshot_quality": rng.choice(["clear", "blurry"]) if has_screenshot else None,
            "channel": rng.choice(["phone", "chat"]),
        })
    return cases
