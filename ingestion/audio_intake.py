import librosa

def load_audio(path: str):
    """Loads and resamples any audio file to 16kHz mono, what Whisper expects."""
    audio, sr = librosa.load(path, sr=16000, mono=True)
    return audio