# SupportSense — Build Progress

## Done
- [x] Baseline MVP running locally, eval verified (98.0% category / 76.0% urgency / 99.1% KB / 33/34 escalation)
- [x] Git set up correctly (.venv excluded, LICENSE added, pushed to GitHub as anshulkeng/supportsense)
- [x] requirements.txt pinned to installed versions
- [x] 6 GitHub Issues created (#1-#6)
- [x] Issue #1: Real zero shot classifier (BART-MNLI) added via triage_real(), hybrid with
      rule-based urgency via triage_hybrid() -- zero shot urgency was only 33% (near-random),
      so kept rule-based urgency (76%) while using zero shot for category (66%)
- [x] Issue #4: Fixed urgency-detection miss on noisy transcripts -- added _fuzzy_contains()
      prefix-matching in perception/sentiment.py so truncated words (e.g. "urge...") still
      match markers like "urgent"; also applied same fuzzy matching to CRITICAL_MARKERS/
      HIGH_MARKERS checks in triage/classifier.py
- [x] Issue #5: README rewritten with honest before/after numbers and design rationale   
- [x] Issue #2: Real Whisper (openai/whisper-base) tested on 3 self-recorded audio clips,
      results saved in sample_data/real_transcription_results.md -- 2/3 had minor real ASR
      errors (dropped/substituted words), 1/3 perfect
- [x] Issue #3: Real BLIP captioning + Tesseract OCR tested on 3 self-made error screenshots
      (sample_data/real_vision_results.md) -- BLIP captioning failed on all 3, OCR succeeded
      on all 3; OCR is the correct tool for this sub-task

## Current verified numbers (after #1 and #4)
- Category routing accuracy: 66.0% (real zero shot, BART-MNLI)
- Urgency routing accuracy: 76.7% (rule-based, fuzzy-matched)
- KB retrieval accuracy: 100.0%
- Critical-urgency escalation: 34/34 (PASS)

## Not started
- [ ] Issue #6: Demo video + resume bullets