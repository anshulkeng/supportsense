# SupportSense

A real, runnable multimodal support-triage pipeline. Built to prove the core
architecture works end to end, with honest, measured numbers at every stage —
not a full production system (see "What to build next" below).

## Demo video
[Watch the walkthrough]([YOUR_VIDEO_LINK_HERE](https://drive.google.com/file/d/18MhBppdy86YrURzcve1U17xGzrj8WUdG/view?usp=drive_link))

## What's genuinely real here

- **The full pipeline runs.** Transcription → Vision → Triage → (conditional)
  Knowledge Retrieval → Response, wired together with LangGraph, actually
  executes, including a real conditional branch (critical-urgency cases skip
  KB retrieval and route straight to escalation).
- **Category classification is real zero-shot** (`facebook/bart-large-mnli`
  via Hugging Face `transformers`) — no fine-tuning, no labeled training data.
- **Urgency classification is rule-based with fuzzy matching** — deliberately
  *not* zero-shot. Real zero-shot scored only 33% on urgency (near-random for
  4 classes) vs. 76% for the rule-based approach on this dataset, so the
  rule-based method is used for the safety-critical escalation decision. See
  "Design decision" below.
- **Knowledge retrieval is real.** `knowledge/kb_retriever.py` uses scikit-learn
  TF-IDF + cosine similarity over a real (if small) knowledge base.
- **It's validated against known ground truth.** `ingestion/case_generator.py`
  produces synthetic cases with known true category/urgency/KB-topic labels.

  ## Design decision: why urgency isn't zero-shot

This is the most interesting engineering finding in the project, and worth
reading rather than skipping.

A rule-based keyword/frustration-score classifier, tuned against this exact
synthetic dataset, originally scored 98% category / 76% urgency. Swapping in
a real zero-shot model (BART-MNLI, no fine-tuning) gave a very different
picture:

| Approach | Category accuracy | Urgency accuracy |
|---|---|---|
| Rule-based (tuned to this dataset) | 98.0% | 76.0% |
| Real zero-shot (no tuning) | 66.0% | 33.3% |
| **Hybrid (shipped)** | **66.0%** (zero-shot) | **76.7%** (rule-based) |

Zero-shot handles *category* reasonably well — topic classification (billing
vs. bug vs. account) is close to what NLI-based zero-shot models are built
for. It handles *urgency* poorly, because urgency isn't a topic — it's a
contextual, often implicit judgment about severity, which a generic entailment
model isn't well-suited to without fine-tuning or much more careful prompt
design. Rather than force one model to do both, this pipeline uses zero-shot
where it's demonstrably reliable (category) and a fuzzy-matched rule-based
detector where it's demonstrably more reliable (urgency) — a deliberate,
measured tradeoff, not a limitation that was hidden.

## A real bug found and fixed

The eval also caught a genuine failure mode: simulated noisy-audio transcripts
sometimes truncate words (e.g. `"urgent"` → `"urge..."`), and the original
exact-substring urgency matcher missed truncated markers entirely, silently
misrouting a critical case to a lower urgency. Fixed via `_fuzzy_contains()`
in `perception/sentiment.py`, which recognizes a truncated word as matching a
marker if it's a genuine prefix (e.g. `"urge..."` correctly matches
`"urgent"`). Result: critical-escalation accuracy went from 33/34 to 34/34.

## What's simplified for this MVP (and how to upgrade it)

| Component | MVP version | Production upgrade |
|---|---|---|
| `perception/transcriber.py` | Simulates ASR noise based on an `audio_quality` flag | Swap for real HF Whisper (commented in file) |
| `perception/vision_reader.py` | Simulates OCR character-confusion noise | Swap for real HF image-to-text (commented in file) |
| `perception/sentiment.py` | Real rule-based scoring with fuzzy marker matching | Optionally upgrade to a real HF text-classification pipeline |
| `triage/classifier.py` | **Real zero-shot (category) + real rule-based (urgency)**, hybrid | Consider fine-tuning a small urgency classifier on real labeled tickets |
| `agents/response_agent.py` (TTS leg) | Stubbed | Swap for real HF text-to-speech (commented in file) |

`knowledge/kb_retriever.py`, the LangGraph orchestration, the escalation
branching logic, the FastAPI app, and the Streamlit dashboard are already real
and need no changes to work with real data.

## Running it

```bash
pip install -r requirements.txt

# Run the validation eval
python -m eval.run_eval

# Run the API
uvicorn api.main:app --reload --port 8001

# Run the dashboard
streamlit run frontend/app_streamlit.py
```

## Repository structure

## What to build next

1. Build real audio/screenshot intake and test the real Whisper/image-to-text
   swaps against self-recorded samples (see `PROGRESS.md`).
2. Upgrade retrieval from TF-IDF to dense embeddings + pgvector once the real
   knowledge base is larger than a handful of documents.
3. Explore fine-tuning a lightweight urgency classifier on real labeled
   support tickets, to see if it can beat both the rule-based approach and
   zero-shot.
4. Add CI gating (`.github/workflows/eval-gate.yml`) on routing-accuracy
   regressions.
5. Deploy the API and dashboard, record a demo video leading with the
   escalation-on-critical-urgency moment and the zero-shot-vs-rule-based
   design decision above.
