from openai import OpenAI

client = OpenAI(api_key="")

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