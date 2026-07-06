# SupportSense — Working MVP

A real, runnable multimodal support-triage pipeline. Scoped-down MVP built to
prove the core architecture actually works end to end — not a full production
system (see "What to build next" below).

## What's genuinely real here

- **The full pipeline runs.** Transcription → Vision → Triage → (conditional)
  Knowledge Retrieval → Response, wired together with LangGraph, actually
  executes, including a real conditional branch (critical-urgency cases skip
  KB retrieval and route straight to escalation).
- **Knowledge retrieval is real.** `knowledge/kb_retriever.py` uses scikit-learn
  TF-IDF + cosine similarity over a real (if small) knowledge base — no model
  download needed, genuinely functional, not simulated.
- **Sentiment and triage are real rule-based logic**, not a simulation — just
  a simplified stand-in for zero-shot classification (see upgrade table below).
- **It's validated against known ground truth.** `ingestion/case_generator.py`
  produces synthetic cases with known true category/urgency/KB-topic labels.
  Run `python -m eval.run_eval` and you'll see real, honestly-measured numbers:

  ```
  Category routing accuracy: 147/150 = 98.0%
  Urgency routing accuracy:  114/150 = 76.0%
  KB retrieval accuracy (non-escalated cases): 114/115 = 99.1%
  Critical-urgency cases correctly escalated: 33/34
  ```

  That 33/34 is not a bug I hid — it's a genuine, interesting failure the eval
  caught: one case had noisy simulated audio that corrupted "urgent" into
  "urge..." and "right now" into "right n...", so the keyword-based urgency
  detector missed both markers and the case was misrouted to "low" urgency
  instead of escalating. This is exactly the kind of case-level failure a
  real triage system needs visibility into, and exactly why perception
  quality matters for downstream routing decisions — a good thing to mention
  in an interview as a failure mode you found and could fix (e.g. fuzzy
  keyword matching, or a frustration-score fallback that doesn't depend on
  exact phrase matches).

- **The FastAPI app and Streamlit dashboard both actually run** against this
  same pipeline.

## What's simplified for this MVP (and how to upgrade it)

This sandbox has no internet access to Hugging Face or LLM APIs, so the
perception legs that would normally call a real model are simulated instead:

| Component | MVP version | Production upgrade |
|---|---|---|
| `perception/transcriber.py` | Simulates ASR noise based on an `audio_quality` flag (clear vs. noisy) | Swap for a real HF Whisper pipeline (commented in the file) |
| `perception/vision_reader.py` | Simulates OCR character-confusion noise on a `screenshot_quality` flag | Swap for a real HF image-to-text pipeline (commented in the file) |
| `perception/sentiment.py` | Real, working keyword/punctuation rule-based scoring | Optionally upgrade to a real HF text-classification pipeline for subtler phrasing |
| `triage/classifier.py` | Real, working keyword-based category/urgency scoring | Swap for a real HF zero-shot-classification pipeline (commented in the file) |
| `agents/response_agent.py` (TTS leg) | Stubbed — returns a placeholder path | Swap for a real HF text-to-speech pipeline (commented in the file) |

`knowledge/kb_retriever.py`, the LangGraph orchestration, the escalation
branching logic, the FastAPI app, and the Streamlit dashboard need **no
changes** to work with real data — they're already real.

## Running it

```bash
pip install -r requirements.txt

# Run the validation eval (proves routing + retrieval accuracy against known ground truth)
python -m eval.run_eval

# Run the API
uvicorn api.main:app --reload --port 8001
# then: curl -X POST http://localhost:8001/case -H "Content-Type: application/json" \
#   -d '{"true_transcript": "The app crashes every time I export", "channel": "chat"}'

# Run the dashboard
streamlit run frontend/app_streamlit.py
```

## Repository structure

```
supportsense_mvp/
├── ingestion/case_generator.py     # Synthetic cases with known ground truth
├── perception/
│   ├── transcriber.py              # Simulated ASR (documented swap point)
│   ├── vision_reader.py            # Simulated vision/OCR (documented swap point)
│   └── sentiment.py                # REAL rule-based frustration detection
├── triage/classifier.py            # REAL rule-based category/urgency tagging
├── knowledge/
│   ├── kb_docs.py                  # Help-center knowledge base content
│   └── kb_retriever.py             # REAL TF-IDF retrieval
├── agents/
│   ├── nodes.py                    # LangGraph node functions
│   ├── graph.py                    # LangGraph supervisor + conditional escalation routing
│   └── response_agent.py           # Reply/escalation decision + TTS stub
├── api/main.py                     # FastAPI app
├── frontend/app_streamlit.py       # Dashboard (single case + batch eval tabs)
├── eval/run_eval.py                # Ground-truth validation script
└── requirements.txt
```

## What to build next (see the full 12-week guide for detail)

1. Swap the four components in the upgrade table above for real HF model calls.
2. Upgrade retrieval from TF-IDF to dense embeddings + pgvector once your real
   knowledge base is larger than a handful of documents.
3. Fix the urgency-detection failure mode found above (fuzzy matching or a
   frustration-score path that's robust to partial word corruption).
4. Build a larger, hand-labeled golden set from real (not synthetic) support
   tickets, and add CI gating on routing accuracy regressions.
5. Deploy the API and dashboard, record a demo video leading with the
   escalation-on-critical-urgency moment and the honest ASR-noise finding.
