from openai import OpenAI

client = OpenAI(api_key="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")

def transcribe_audio(file_path):
    with open(file_path, "rb") as audio_file:
        transcript = client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file
        )
    return transcript.text


# --- TEST IT ---
result = transcribe_audio(r"C:\Users\USER\Desktop\python\nurse_ai_app\Voice 290.mp3")
print(result)