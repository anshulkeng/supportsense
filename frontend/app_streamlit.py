"""
frontend/app_streamlit.py

Run with: streamlit run frontend/app_streamlit.py
(run from the project root so imports resolve)
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import streamlit as st
import pandas as pd
from ingestion.case_generator import generate_cases
from agents.graph import run_case

st.set_page_config(page_title="SupportSense", layout="wide")
st.title("SupportSense — Multimodal Support Triage Dashboard")
st.caption("Fuses simulated ASR + vision + rule-based triage + TF-IDF knowledge retrieval into one routing decision.")

tab1, tab2 = st.tabs(["Submit a Case", "Batch Eval (Golden Set)"])

with tab1:
    st.subheader("Submit a case")
    transcript = st.text_area("What the customer said (true transcript)",
                               "The app crashes every time I try to export my report")
    audio_quality = st.selectbox("Audio quality", ["clear", "noisy"])
    channel = st.selectbox("Channel", ["chat", "phone"])
    has_screenshot = st.checkbox("Has screenshot")
    screenshot_text = st.text_input("Screenshot error text (if any)", "ERR_EXPORT_0x5A") if has_screenshot else ""
    screenshot_quality = st.selectbox("Screenshot quality", ["clear", "blurry"]) if has_screenshot else "clear"

    if st.button("Run Case"):
        case = {
            "case_id": "manual",
            "true_transcript": transcript,
            "audio_quality": audio_quality,
            "has_screenshot": has_screenshot,
            "true_screenshot_text": screenshot_text,
            "screenshot_quality": screenshot_quality,
            "channel": channel,
        }
        result = run_case(case)
        st.write("**Simulated ASR transcript:**", result["transcript"])
        if has_screenshot:
            st.write("**Simulated screenshot extraction:**", result["screenshot_text"])
        col1, col2, col3 = st.columns(3)
        col1.metric("Category", result["category"])
        col2.metric("Urgency", result["urgency"])
        col3.metric("Escalated", "Yes" if result["escalated"] else "No")
        st.write("**KB Match:**", result["kb_match"]["topic"], f"(confidence {result['kb_match']['confidence']})")
        st.write("**Reply:**", result["reply"])

with tab2:
    st.subheader("Run the golden evaluation set")
    n = st.slider("Number of synthetic golden cases", 20, 300, 150, step=10)
    if st.button("Run Batch Eval"):
        cases = generate_cases(n=n, seed=99)
        rows = []
        for c in cases:
            r = run_case(c)
            rows.append({
                "true_category": c["true_category"], "pred_category": r["category"],
                "true_urgency": c["true_urgency"], "pred_urgency": r["urgency"],
                "true_kb_topic": c["true_kb_topic"], "pred_kb_topic": r["kb_match"]["topic"],
                "escalated": r["escalated"],
            })
        df = pd.DataFrame(rows)
        cat_acc = (df["true_category"] == df["pred_category"]).mean()
        urg_acc = (df["true_urgency"] == df["pred_urgency"]).mean()
        non_escalated = df[~df["escalated"]]
        kb_acc = (non_escalated["true_kb_topic"] == non_escalated["pred_kb_topic"]).mean() if len(non_escalated) else 0

        c1, c2, c3 = st.columns(3)
        c1.metric("Category Accuracy", f"{cat_acc:.1%}")
        c2.metric("Urgency Accuracy", f"{urg_acc:.1%}")
        c3.metric("KB Retrieval Accuracy", f"{kb_acc:.1%}")
        st.dataframe(df, use_container_width=True)
