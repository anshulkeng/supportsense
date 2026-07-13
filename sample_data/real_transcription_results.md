# Real Whisper transcription test — Issue #2

Model: openai/whisper-base (no fine-tuning)

| File | Predicted transcript | Notes |
|---|---|---|
| Voice_1.mp4 | "The app keeps crashing every time and try to export my report. This is really urgent." | Minor error: "I" -> "and" |
| Voice_2.mp4 | "Hi, I was just twice for my subscription this month and I need a refund." | Dropped word: "charged" missing |
| Voice_3.mp4 | "Just a quick question, how do I change my billing email address?" | Perfect match |

Real ASR error rate observed on 3 self-recorded samples: 2/3 had minor
transcription errors (dropped/substituted words), consistent with expected
whisper-base behavior on casual speech. This is genuine, not simulated.