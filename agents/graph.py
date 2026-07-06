"""
agents/graph.py

Wires the pipeline: Transcription -> Vision -> Triage -> (conditional) ->
Knowledge -> Response. Critical-urgency cases skip knowledge retrieval and
route straight to escalation -- a real conditional branch, not just a
linear pipeline.
"""
from langgraph.graph import StateGraph, END
from agents.nodes import transcription_node, vision_node, triage_node, knowledge_node, response_node


def _skip_knowledge(state: dict) -> dict:
    state["kb_match"] = {"topic": None, "text": "", "confidence": 0.0}
    return state


def _route_after_triage(state: dict) -> str:
    return "skip_to_response" if state["urgency"] == "critical" else "consult_kb"


def build_graph():
    graph = StateGraph(dict)
    graph.add_node("transcribe", transcription_node)
    graph.add_node("read_image", vision_node)
    graph.add_node("triage", triage_node)
    graph.add_node("skip_knowledge", _skip_knowledge)
    graph.add_node("consult_kb", knowledge_node)
    graph.add_node("respond", response_node)

    graph.set_entry_point("transcribe")
    graph.add_edge("transcribe", "read_image")
    graph.add_edge("read_image", "triage")

    graph.add_conditional_edges(
        "triage",
        _route_after_triage,
        {"skip_to_response": "skip_knowledge", "consult_kb": "consult_kb"},
    )
    graph.add_edge("skip_knowledge", "respond")
    graph.add_edge("consult_kb", "respond")
    graph.add_edge("respond", END)

    return graph.compile()


def run_case(case: dict) -> dict:
    app = build_graph()
    return app.invoke({"case": case})
