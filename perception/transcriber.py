"""
perception/transcriber.py

Real ASR (Whisper) requires downloading model weights from Hugging Face,
which this sandbox cannot reach. This module simulates what ASR output
actually looks like: on "clear" audio it returns the true transcript almost
verbatim; on "noisy" audio it drops/garbles some words, the way real Whisper
output looks on a bad phone connection. This lets the rest of the pipeline
(sentiment, triage, retrieval) be tested against realistically imperfect
input instead of assuming perfect transcripts.

To upgrade to real ASR once you have internet access:

    from transformers import pipeline
    asr = pipeline("automatic-speech-recognition", model="openai/whisper-base")
    def transcribe(audio_path: str) -> str:
        return asr(audio_path)["text"].strip()
"""
import random

DROP_WORDS = {"the", "a", "to", "this", "it", "my", "is"}


def transcribe(case: dict, rng: random.Random = None) -> str:
    """Simulates ASR output quality based on the case's audio_quality metadata."""
    rng = rng or random.Random()
    text = case["true_transcript"]
    if case["audio_quality"] == "clear":
        return text

    # "noisy" audio: drop some low-information words and occasionally garble one
    words = text.split()
    out = []
    for w in words:
        if w.lower() in DROP_WORDS and rng.random() < 0.4:
            continue
        if rng.random() < 0.08:
            out.append(w[: max(1, len(w) - 2)] + "...")
        else:
            out.append(w)
    return " ".join(out)
