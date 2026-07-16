# SupportSense

A real, runnable multimodal support-triage pipeline. Built to prove the core
architecture works end to end, with honest, measured numbers at every stage —
not a full production system (see "What to build next" below).

## Demo video

[Watch the full walkthrough](https://drive.google.com/file/d/18MhBppdy86YrURzcve1U17xGzrj8WUdG/view?usp=sharing)

## What's genuinely real here

- **The full pipeline runs.** Transcription → Vision → Triage → (conditional)
  Knowledge Retrieval → Response, wired together with LangGraph, actually
  executes, including a real conditional branch (critical-urgency cases skip
  KB retrieval and route straight to escalation).
- **Transcription is real Whisper** (`openai/whisper-base`), tested against
  3 self-recorded audio clips of varying quality. Results and error analysis
  in [`sample_data/real_transcription_results.md`](sample_data/real_transcription_results.md).
- **Screenshot text extraction uses real OCR** (Tesseract), not image
  captioning. Both were tested head to head on 3 self made error screenshots:
  OCR correctly read the exact error text in all 3 cases; BLIP image
  captioning failed to extract accurate text in all 3. Full comparison in
  [`sample_data/real_vision_results.md`](sample_data/real_vision_results.md).
- **Category classification is real zero shot** (`facebook/bart-large-mnli`
  via Hugging Face `transformers`)  no fine tuning, no labeled training data.
- **Urgency classification is rule-based with fuzzy matching**  deliberately
  *not* zero shot. Real zero shot scored only 33% on urgency (near random for
  4 classes) vs. 76% for the rule based approach on this dataset, so the
  rule-based method is used for the safety critical escalation decision. See
  "Design decision" below.
- **Knowledge retrieval is real.** `knowledge/kb_retriever.py` uses scikit-learn
  TF-IDF + cosine similarity over a real (if small) knowledge base.
- **The Streamlit dashboard accepts real audio uploads**, running them through
  actual Whisper transcription live, and includes a Queue view that sorts
  submitted cases by urgency (critical first) so an agent could scan and
  prioritize at a glance.
- **It's validated against known ground truth.** `ingestion/case_generator.py`
  produces synthetic cases with known true category/urgency/KB-topic labels.

Category routing accuracy: 99/150 = 66.0%
Urgency routing accuracy:  115/150 = 76.7%
KB retrieval accuracy (non-escalated cases): 114/114 = 100.0%
Critical-urgency cases correctly escalated: 34/34
PASS: escalation path is reachable and fires on critical cases

## Design decision: why urgency isn't zero-shot

This is the most interesting engineering finding in the project, and worth
reading rather than skipping.

A rule based keyword/frustration score classifier, tuned against this exact
synthetic dataset, originally scored 98% category / 76% urgency. Swapping in
a real zero-shot model (BART-MNLI, no fine-tuning) gave a very different
picture:

| Approach | Category accuracy | Urgency accuracy |
|---|---|---|
| Rule-based (tuned to this dataset) | 98.0% | 76.0% |
| Real zero-shot (no tuning) | 66.0% | 33.3% |
| **Hybrid (shipped)** | **66.0%** (zero-shot) | **76.7%** (rule-based) |

Zero-shot handles *category* reasonably well  topic classification (billing
vs. bug vs. account) is close to what NLI-based zero-shot models are built
for. It handles *urgency* poorly, because urgency isn't a topic it's a
contextual, often implicit judgment about severity, which a generic entailment
model isn't well-suited to without fine tuning or much more careful prompt
design. Rather than force one model to do both, this pipeline uses zero-shot
where it's demonstrably reliable (category) and a fuzzy matched rule based
detector where it's demonstrably more reliable (urgency)  a deliberate,
measured tradeoff, not a limitation that was hidden.

The same pattern held for screenshots: BLIP image captioning versus Tesseract
OCR were tested head to head, and OCR won cleanly for extracting exact error
text  captioning models aren't built to read rendered text accurately, while
OCR is purpose built for it. Picking the right tool per sub-task, rather than
using "an AI model" for everything, was the consistent theme across this build.

## A real bug found and fixed

The eval also caught a genuine failure mode: simulated noisy-audio transcripts
sometimes truncate words (e.g. `"urgent"` → `"urge..."`), and the original
exact-substring urgency matcher missed truncated markers entirely, silently
misrouting a critical case to a lower urgency. Fixed via `_fuzzy_contains()`
in `perception/sentiment.py`, which recognizes a truncated word as matching a
marker if it's a genuine prefix (e.g. `"urge..."` correctly matches
`"urgent"`). Result: critical-escalation accuracy went from 33/34 to 34/34.

## Honest scope boundaries

Worth being precise about what this system doesn't do, since naming
limitations clearly matters as much as the results:

- **No real ingestion layer.** Cases are submitted manually through the
  dashboard or API — there's no integration with real email, phone systems,
  or ticketing platforms (e.g. Zendesk webhooks). That's a genuine, separate
  piece of engineering work, not built here.
- **The Queue view sorts into 4 urgency buckets, not a continuous score.**
  If many cases were genuinely critical at once (e.g. during a real outage),
  this wouldn't prioritize within that bucket or recognize they're one shared
  incident rather than many separate ones.
- **Urgency detection is inferred from text content**, which means it could
  in principle be gamed by someone learning which phrases trigger escalation.
  A production system would need a harder-to-game signal.
- **The dashboard still defaults to a quality-simulation toggle** for quick
  testing, alongside the real Whisper upload  a deliberate MVP scoping
  choice, not an oversight.

## What's simplified for this MVP (and how to upgrade it)

| Component | MVP version | Production upgrade |
|---|---|---|
| `perception/transcriber.py` | **Real Whisper (`transcribe_real`)** available; simulated version (`transcribe`) retained for fast, reproducible eval runs | Wire real Whisper into the eval harness once a real labeled audio dataset exists |
| `perception/vision_reader.py` | **Real OCR (`extract_text_ocr`) and BLIP captioning (`read_screenshot_real`)** both implemented and compared; simulated version retained for eval | Use OCR as primary; BLIP optionally for scene-level context only |
| `perception/sentiment.py` | Real rule-based scoring with fuzzy marker matching | Optionally upgrade to a real HF text-classification pipeline |
| `triage/classifier.py` | **Real zero-shot (category) + real rule-based (urgency)**, hybrid | Consider fine-tuning a small urgency classifier on real labeled tickets |
| `agents/response_agent.py` (TTS leg) | Stubbed | Swap for real HF text-to-speech |

`knowledge/kb_retriever.py`, the LangGraph orchestration, the escalation
branching logic, the FastAPI app, and the Streamlit dashboard (including the
real-audio-upload and Queue features) are already real.

## Running it

```bash
pip install -r requirements.txt

# Run the validation eval
python -m eval.run_eval

# Test real Whisper on your own recordings
python test_real_audio.py

# Test real OCR vs. BLIP captioning on your own screenshots
python test_real_screenshots.py

# Run the API
uvicorn api.main:app --reload --port 8001

# Run the dashboard (supports real audio upload + urgency-sorted Queue view)
streamlit run frontend/app_streamlit.py
```

## Repository structure
supportsense_mvp/
├── ingestion/
│   ├── case_generator.py     # Synthetic cases with known ground truth
│   └── audio_intake.py       # Real audio loading (librosa, 16kHz mono)
├── perception/
│   ├── transcriber.py        # Simulated ASR (eval) + real Whisper (transcribe_real)
│   ├── vision_reader.py      # Simulated vision (eval) + real BLIP + real OCR
│   └── sentiment.py          # Real rule-based frustration detection, fuzzy matching
├── triage/classifier.py      # Real zero-shot (category) + rule-based (urgency), hybrid
├── knowledge/
│   ├── kb_docs.py            # Help-center knowledge base content
│   └── kb_retriever.py       # Real TF-IDF retrieval
├── agents/
│   ├── nodes.py              # LangGraph node functions
│   ├── graph.py              # LangGraph supervisor + conditional escalation routing
│   └── response_agent.py     # Reply/escalation decision + TTS stub
├── api/main.py                # FastAPI app
├── frontend/app_streamlit.py  # Dashboard: submit case (+ real audio upload), batch eval, Queue
├── eval/run_eval.py           # Ground-truth validation script
├── sample_data/
│   ├── audio/                       # 3 self-recorded real audio clips
│   ├── screenshots/                 # 3 self-made error screenshots
│   ├── real_transcription_results.md
│   └── real_vision_results.md
├── test_real_audio.py         # Standalone real-Whisper test script
├── test_real_screenshots.py   # Standalone real BLIP-vs-OCR test script
├── progress.md                 # Build progress tracker
└── requirements.txt

## What to build next

1. Build a real ingestion layer (email/ticketing webhook → API) — currently
   cases are submitted manually.
2. Upgrade retrieval from TF-IDF to dense embeddings + pgvector once the real
   knowledge base is larger than a handful of documents.
3. Replace the 4-bucket urgency system with a continuous severity score, and
   add pattern/incident detection across simultaneous cases.
4. Explore fine-tuning a lightweight urgency classifier on real labeled
   support tickets, to see if it can beat both the rule-based approach and
   zero-shot.
5. Add CI gating (`.github/workflows/eval-gate.yml`) on routing-accuracy
   regressions, and deploy the API + dashboard publicly.
