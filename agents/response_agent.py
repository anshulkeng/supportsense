"""
agents/response_agent.py

Decides whether to auto-reply (grounded in the retrieved KB doc) or escalate
to a human. Also handles the voice-reply leg for phone-channel cases.

TTS requires a downloaded model (unavailable in this sandbox), so
`generate_voice_reply()` is stubbed to return a placeholder path. Swap for
real TTS once you have internet access:

    from transformers import pipeline
    tts = pipeline("text-to-speech", model="microsoft/speecht5_tts")
    def generate_voice_reply(text: str) -> str:
        speech = tts(text)
        return save_audio_to_disk(speech)  # your own audio-writing helper
"""

ESCALATION_CONFIDENCE_THRESHOLD = 0.15


def generate_voice_reply(text: str) -> str:
    """STUBBED: no TTS model available in this sandbox. See module docstring for the real swap."""
    return "[voice_reply_not_generated_in_mvp]"


def respond(state: dict) -> dict:
    urgency = state["urgency"]
    kb_match = state["kb_match"]

    if urgency == "critical":
        state["reply"] = "This case has been escalated to a human agent due to its urgency."
        state["escalated"] = True
    elif kb_match["confidence"] < ESCALATION_CONFIDENCE_THRESHOLD:
        state["reply"] = "This case has been escalated to a human agent (no confident match found)."
        state["escalated"] = True
    else:
        state["reply"] = kb_match["text"]
        state["escalated"] = False

    if state.get("channel") == "phone" and not state["escalated"]:
        state["voice_reply_path"] = generate_voice_reply(state["reply"])
    else:
        state["voice_reply_path"] = None

    return state
