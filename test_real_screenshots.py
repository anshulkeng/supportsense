from perception.vision_reader import read_screenshot_real, extract_text_ocr

files = [
    "sample_data/screenshots/payment_error.png",
    "sample_data/screenshots/sync_error.png",
    "sample_data/screenshots/login_error.png",
]

for f in files:
    print(f"--- {f} ---")
    print("BLIP caption:", read_screenshot_real(f))
    print("OCR text:", extract_text_ocr(f))
    print()