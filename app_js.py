import streamlit as st
from openai import OpenAI
from datetime import datetime
import tempfile
import os
import base64

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])


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
st.write("Record your observation and generate a compliant DAR progress note instantly.")

st.divider()

col1, col2, col3 = st.columns(3)
with col1:
    resident_name = st.text_input("Resident Name")
with col2:
    staff_name = st.text_input("Staff Name")
with col3:
    staff_role = st.selectbox("Role", ["RN", "EN", "PCW", "Coordinator"])

st.divider()

st.subheader("Record your observation")

# HTML/JS recorder component
recorder_html = """
<script>
let mediaRecorder;
let audioChunks = [];
let isRecording = false;

async function toggleRecording() {
    const btn = document.getElementById('recordBtn');
    const status = document.getElementById('status');

    if (!isRecording) {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        mediaRecorder = new MediaRecorder(stream);
        audioChunks = [];

        mediaRecorder.ondataavailable = e => audioChunks.push(e.data);

        mediaRecorder.onstop = () => {
            const blob = new Blob(audioChunks, { type: 'audio/webm' });
            const reader = new FileReader();
            reader.onloadend = () => {
                const base64 = reader.result.split(',')[1];
                const input = document.getElementById('audioData');
                input.value = base64;
                const form = document.getElementById('audioForm');
                form.requestSubmit();
            };
            reader.readAsDataURL(blob);
            stream.getTracks().forEach(t => t.stop());
        };

        mediaRecorder.start();
        isRecording = true;
        btn.innerText = '⏹️ Stop Recording';
        btn.style.background = '#ff4b4b';
        status.innerText = '🔴 Recording...';
    } else {
        mediaRecorder.stop();
        isRecording = false;
        btn.innerText = '🎙️ Start Recording';
        btn.style.background = '#0068c9';
        status.innerText = '⏳ Processing...';
    }
}
</script>

<form id="audioForm" method="POST">
    <input type="hidden" id="audioData" name="audioData" />
</form>

<button id="recordBtn" onclick="toggleRecording()"
    style="background:#0068c9; color:white; border:none; padding:14px 28px;
    font-size:16px; border-radius:8px; cursor:pointer; margin-bottom:12px;">
    🎙️ Start Recording
</button>
<p id="status" style="color:gray; font-size:14px;">Press the button to start recording.</p>
"""

st.components.v1.html(recorder_html, height=120)

st.write("Or upload an audio file:")
audio_file = st.file_uploader("Upload voice recording", type=["mp3", "mp4", "wav", "m4a", "webm"])

audio_b64 = st.text_input("", key="audio_b64", label_visibility="collapsed", placeholder="audio data")

if audio_file is not None or (audio_b64 and len(audio_b64) > 100):
    if st.button("Generate Note"):
        with st.spinner("Transcribing audio..."):
            if audio_file is not None:
                suffix = os.path.splitext(audio_file.name)[1]
                with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                    tmp.write(audio_file.read())
                    tmp_path = tmp.name
            else:
                audio_bytes = base64.b64decode(audio_b64)
                with tempfile.NamedTemporaryFile(delete=False, suffix=".webm") as tmp:
                    tmp.write(audio_bytes)
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