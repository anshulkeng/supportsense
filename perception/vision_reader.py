"""
perception/vision_reader.py

Real screenshot understanding (BLIP/Florence-2 image-to-text) requires
Hugging Face model downloads, unavailable in this sandbox. This module
simulates OCR-style extraction: "clear" screenshots return the true
error text intact, "blurry" ones corrupt a few characters, mimicking
real OCR failure modes.

To upgrade to real vision understanding once you have internet access:

    from transformers import pipeline
    image_to_text = pipeline("image-to-text", model="Salesforce/blip-image-captioning-base")
    def read_screenshot(image_path: str) -> str:
        return image_to_text(image_path)[0]["generated_text"]
"""
import random

CONFUSABLE = {"0": "O", "O": "0", "5": "S", "S": "5", "1": "I", "I": "1"}


def read_screenshot(case: dict, rng: random.Random = None) -> str:
    if not case.get("has_screenshot"):
        return ""
    rng = rng or random.Random()
    text = case["true_screenshot_text"]
    if case["screenshot_quality"] == "clear":
        return text

    out = []
    for ch in text:
        if ch in CONFUSABLE and rng.random() < 0.25:
            out.append(CONFUSABLE[ch])
        else:
            out.append(ch)
    return "".join(out)
