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

if "queue" not in st.session_state:
    st.session_state.queue = []

tab1, tab2, tab3 = st.tabs(["Submit a Case", "Batch Eval (Golden Set)", "Queue"])

with tab1:
    st.subheader("Submit a case")
    transcript = st.text_area("What the customer said (true transcript)",
                               "The app crashes every time I try to export my report")
    uploaded_audio = st.file_uploader("Upload real audio (optional — overrides the text transcript below)", type=["mp3", "mp4", "wav", "m4a"])
    audio_quality = st.selectbox("Audio quality (only used if no real audio uploaded)", ["clear", "noisy"])
    channel = st.selectbox("Channel", ["chat", "phone"])
    has_screenshot = st.checkbox("Has screenshot")
    screenshot_text = st.text_input("Screenshot error text (if any)", "ERR_EXPORT_0x5A") if has_screenshot else ""
    screenshot_quality = st.selectbox("Screenshot quality", ["clear", "blurry"]) if has_screenshot else "clear"

    if st.button("Run Case"):
        final_transcript = transcript
        if uploaded_audio is not None:
            temp_path = f"temp_upload_{uploaded_audio.name}"
            with open(temp_path, "wb") as f:
                f.write(uploaded_audio.getbuffer())
            from perception.transcriber import transcribe_real
            final_transcript = transcribe_real(temp_path)
            os.remove(temp_path)
            st.write("**Real Whisper transcript (from your upload):**", final_transcript)

        case = {
            "case_id": f"manual-{len(st.session_state.queue) + 1}",
            "true_transcript": final_transcript,
            "audio_quality": audio_quality,
            "has_screenshot": has_screenshot,
            "true_screenshot_text": screenshot_text,
            "screenshot_quality": screenshot_quality,
            "channel": channel,
        }
        result = run_case(case)
        result["case_id"] = case["case_id"]
        st.session_state.queue.append(result)

        st.write("**Simulated ASR transcript:**", result["transcript"])
        if has_screenshot:
            st.write("**Simulated screenshot extraction:**", result["screenshot_text"])
        col1, col2, col3 = st.columns(3)
        col1.metric("Category", result["category"])
        col2.metric("Urgency", result["urgency"])
        col3.metric("Escalated", "Yes" if result["escalated"] else "No")
        st.write("**KB Match:**", result["kb_match"]["topic"], f"(confidence {result['kb_match']['confidence']})")
        st.write("**Reply:**", result["reply"])
        st.success("Added to the Queue tab.")

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

with tab3:
    st.subheader("Case Queue (sorted by urgency)")
    st.caption("Cases submitted in the 'Submit a Case' tab this session, sorted critical first.")

    if st.button("Clear Queue"):
        st.session_state.queue = []
        st.rerun()

    if not st.session_state.queue:
        st.info("No cases yet — submit one in the 'Submit a Case' tab first.")
    else:
        urgency_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
        sorted_queue = sorted(st.session_state.queue, key=lambda c: urgency_order.get(c.get("urgency", "low"), 99))
        icon = {"critical": "🔴", "high": "🟠", "medium": "🟡", "low": "🟢"}

        for c in sorted_queue:
            urgency = c.get("urgency", "unknown")
            st.write(f"{icon.get(urgency, '⚪')} **{urgency.upper()}** — {c.get('category', 'other')} — {c.get('transcript', '')[:80]}")
            st.caption(f"Escalated: {c.get('escalated')} | Reply: {c.get('reply', '')[:100]}")
            st.divider()