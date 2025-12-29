import pdfplumber
from io import BytesIO
import uuid
from datetime import datetime
import google.generativeai as genai
import os
import json
import re
from dotenv import load_dotenv

# ================= ENV =================
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

MODEL_NAME = "models/gemini-2.5-flash"
MODEL = genai.GenerativeModel(MODEL_NAME)

# ================= PDF TEXT =================
def extract_text(pdf_bytes):
    text = ""
    with pdfplumber.open(BytesIO(pdf_bytes)) as pdf:
        for page in pdf.pages:
            text += (page.extract_text() or "") + "\n"
    return text.strip()

# ================= GEMINI CORE =================
def call_gemini(prompt):
    response = MODEL.generate_content(prompt)
    text = response.text.strip()

    # 🔥 Extract JSON even if Gemini adds junk
    match = re.search(r"\{.*\}", text, re.S)
    if not match:
        raise ValueError("No JSON found in Gemini output")

    return json.loads(match.group())

# ================= SCHEMA ENFORCER =================
def enforce_schema(data, raw_text):

    schema = {
        "name": "",
        "email": "",
        "phone": "",
        "objective": "",
        "skills": [],
        "education": [],
        "projects": [],
        "experience": [],
        "achievements": [],
        "extra_curricular_activities": [],
        "certifications": [],
        "dates_mentioned": []
    }

    # Merge Gemini output
    for key in schema:
        if key in data and data[key]:
            schema[key] = data[key]

    # 🔥 Hard backfill from raw text
    if not schema["name"]:
        schema["name"] = raw_text.splitlines()[0].strip()

    if not schema["email"]:
        emails = re.findall(r"\S+@\S+", raw_text)
        schema["email"] = emails[0] if emails else ""

    if not schema["phone"]:
        phones = re.findall(r"\+?\d[\d\s\-]{8,15}\d", raw_text)
        schema["phone"] = phones[0] if phones else ""

    if not schema["skills"]:
        COMMON_SKILLS = [
            "Python","Java","JavaScript","React","Node.js","HTML","CSS",
            "Django","Express","MongoDB","MySQL","Git","GitHub"
        ]
        schema["skills"] = [s for s in COMMON_SKILLS if s.lower() in raw_text.lower()]

    if not schema["dates_mentioned"]:
        schema["dates_mentioned"] = list(set(re.findall(r"\b(19|20)\d{2}\b", raw_text)))

    return schema

# ================= GEMINI PROMPT =================
def parse_with_gemini(text):

    prompt = f"""
You are a production-grade resume parsing system like Google or LinkedIn.

STRICT RULES:
- Extract ALL possible information.
- Infer missing structure from context.
- Do NOT leave fields empty if data exists.
- Return ONLY valid JSON.
- No markdown. No explanations.

JSON SCHEMA:
{{
  "name": "",
  "email": "",
  "phone": "",
  "objective": "",
  "skills": [],
  "education": [
    {{
      "degree": "",
      "institution": "",
      "year": "",
      "cgpa_or_percentage": ""
    }}
  ],
  "projects": [
    {{
      "name": "",
      "description": "",
      "skills_used": []
    }}
  ],
  "experience": [
    {{
      "role": "",
      "company": "",
      "duration": "",
      "description": ""
    }}
  ],
  "achievements": [],
  "extra_curricular_activities": [],
  "certifications": [],
  "dates_mentioned": []
}}

RESUME TEXT:
{text}
"""
    return call_gemini(prompt)

# ================= MAIN ENTRY =================
def parse_resume(pdf_bytes):

    raw_text = extract_text(pdf_bytes)

    gemini_data = parse_with_gemini(raw_text)
    final_data = enforce_schema(gemini_data, raw_text)

    # Production metadata
    final_data["candidate_id"] = str(uuid.uuid4())
    final_data["uploaded_at"] = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    final_data["raw_text"] = raw_text[:5000]

    return final_data
