from perception.transcriber import transcribe_real

files = ["sample_data/audio/Voice_1.mp4", "sample_data/audio/Voice_2.mp4", "sample_data/audio/Voice_3.mp4"]

for f in files:
    print(f"--- {f} ---")
    print(transcribe_real(f))
    print()