from openai import OpenAI
from datetime import datetime

client = OpenAI(api_key="")

def generate_note(raw_input, resident_name="", staff_name="", staff_role="RN"):

    # Auto-generate timestamp in Australian format
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
- Write in plain English using ACTIVE voice at all times (e.g. "Nurse administered medication" NOT "medication was administered")
- NEVER invent, assume or imply anything not stated in the raw input
- NEVER drop any detail from the raw input — every piece of information mentioned must appear somewhere in the note
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


# --- TEST IT ---
test_input = "gave david his morning meds, he refused the blood pressure tablet again, seemed agitated"

result = generate_note(
    raw_input=test_input,
    resident_name="John Smith",
    staff_name="Sarah Lee",
    staff_role="RN"
)

print(result)