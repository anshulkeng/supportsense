"""
agents/nodes.py

LangGraph node functions. Each takes and returns the shared per-case state dict.
"""
import random
from perception.transcriber import transcribe
from perception.vision_reader import read_screenshot
from perception.sentiment import detect_frustration
from triage.classifier import triage_hybrid as triage
from knowledge.kb_retriever import retrieve
from agents.response_agent import respond

_rng = random.Random(7)


def transcription_node(state: dict) -> dict:
    state["transcript"] = transcribe(state["case"], _rng)
    return state


def vision_node(state: dict) -> dict:
    state["screenshot_text"] = read_screenshot(state["case"], _rng)
    return state


def triage_node(state: dict) -> dict:
    frustration = detect_frustration(state["transcript"])
    state["frustration_score"] = frustration["frustration_score"]
    result = triage(state["transcript"], state["screenshot_text"], frustration["frustration_score"])
    state["category"] = result["category"]
    state["category_confidence"] = result["category_confidence"]
    state["urgency"] = result["urgency"]
    return state


def knowledge_node(state: dict) -> dict:
    query = f"{state['transcript']} {state['screenshot_text']}".strip()
    matches = retrieve(query, top_k=1)
    state["kb_match"] = matches[0]
    return state


def response_node(state: dict) -> dict:
    state["channel"] = state["case"]["channel"]
    return respond(state)
