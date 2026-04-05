import streamlit as st
from openai import OpenAI
from datetime import datetime
import tempfile
import os

client = OpenAI(api_key="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")


def transcribe_audio(file_path):
    with open(file_path, "rb") as audio_file:
        transcript = client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file
        )
    return transcript.text


def generate_note(raw_input, resident_name="", staff_name="", staff_role="RN"):
    timestamp = datetime.now().strftime("%d/%m/%Y %H:%M")

    prompt = f"""
You are a clinical documentation assistant for aged care nurses in Australia.

Convert the following raw observation into a professional progress note using the DAR format,
which is the standard used in Australian aged care facilities.

DAR FORMAT:
D - Data: Objective observations only. List vitals first, then physical observations, then behavioural.
A - Action: ONLY include actions explicitly mentioned in the input. If no action is mentioned, write "Nil reported."
R - Response: ONLY include resident response if explicitly mentioned in the input. If not mentioned, write "Nil reported."

STRICT RULES:
- Write in plain English using ACTIVE voice at all times
- NEVER invent, assume or imply anything not stated in the raw input
- NEVER drop any detail from the raw input - every piece of information mentioned must appear somewhere in the note
- If it was not said, it does not go in the note
- If it was said, it MUST be in the note
- Follow exception reporting: focus on what has changed or is abnormal
- Keep each section to 1-3 sentences
- Use 24-hour time if time is mentioned

Output in exactly this format:

Resident: {resident_name if resident_name else "[Resident Name]"}
Date/Time: {timestamp}
Staff: {staff_name if staff_name else "[Staff Name]"} ({staff_role})

D (Data):
[data here]

A (Action):
[action here]

R (Response):
[response here]

---
Raw observation:
{raw_input}
"""

    response = client.chat.completions.create(
        model="gpt-4.1-nano",
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    return response.choices[0].message.content


# --- STREAMLIT UI ---
st.title("AI Nurse Note Generator")
st.write("Upload a voice recording and generate a compliant DAR progress note instantly.")

st.divider()

col1, col2, col3 = st.columns(3)
with col1:
    resident_name = st.text_input("Resident Name")
with col2:
    staff_name = st.text_input("Staff Name")
with col3:
    staff_role = st.selectbox("Role", ["RN", "EN", "PCW", "Coordinator"])

st.divider()

audio_file = st.file_uploader("Upload voice recording", type=["mp3", "mp4", "wav", "m4a", "webm"])

if audio_file is not None:
    st.audio(audio_file)

    if st.button("Generate Note"):
        with st.spinner("Transcribing audio..."):
            # Save uploaded file to a temp location so Whisper can read it
            suffix = os.path.splitext(audio_file.name)[1]
            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                tmp.write(audio_file.read())
                tmp_path = tmp.name

            transcript = transcribe_audio(tmp_path)
            os.unlink(tmp_path)

        st.subheader("Transcript")
        st.info(transcript)

        with st.spinner("Generating note..."):
            note = generate_note(
                raw_input=transcript,
                resident_name=resident_name,
                staff_name=staff_name,
                staff_role=staff_role
            )

        st.subheader("Progress Note")
        st.text_area("", value=note, height=300)
        st.success("Note generated. Copy it and paste it into your system.")



        ''' cd C:\Users\USER\Desktop\python\nurse_ai_app
streamlit run app.py    '''