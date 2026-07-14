# Real vision model test — Issue #3

## Models tested
- BLIP image captioning (Salesforce/blip-image-captioning-base) — general-purpose
  image captioning, not built for reading rendered text
- Tesseract OCR (pytesseract) — purpose-built text extraction

## Results on 3 self-made error screenshots

| File | BLIP caption | OCR text |
|---|---|---|
| payment_error.png | "the text reads, ' for the first time, you can ' tweet the text" | "Error 402: Payment Failed / Your card was declined. Please update your billing details and try again." |
| sync_error.png | "a white background with the words ' eron - failed '" | "Error: Sync Failed / Unable to sync your data. Some changes may not be saved. [Retry] [Cancel]" |
| login_error.png | "a white background with the words high paid, low paid, low paid, low paid" | "Login Failed / Incorrect password. You have 2 attempts remaining." |

## Finding

BLIP captioning failed to read any error text accurately across all 3
screenshots -- expected, since it's trained on natural photo captioning,
not rendered UI text. OCR (Tesseract) correctly and near-perfectly
extracted the exact error text in all 3 cases. This mirrors the earlier
zero-shot-vs-rule-based urgency finding: picking the right tool for the
sub-task matters more than using "the AI model" for everything. For this
pipeline, OCR is the correct primary tool for screenshot text extraction;
BLIP could still add scene-level context (e.g. "this looks like a mobile
app error dialog") as a secondary signal, but should not be relied on for
exact error codes or messages.