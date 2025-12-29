import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
print("GEMINI KEY:", os.getenv("GEMINI_API_KEY"))

# Use a free model that works reliably
model = genai.GenerativeModel("gemini-2.5-flash-lite")


def match_candidates(job_requirement, candidates_list):
    matches = []
    jd_lower = job_requirement.lower()

    for candidate in candidates_list:
        score = 0

        # Skills match
        skills = [s.lower() for s in candidate.get("skills", []) if isinstance(s, str)]
        for skill in skills:
            if skill in jd_lower:
                score += 10

        # Experience match
        exp_list = candidate.get("experience", [])
        exp_text = ""
        if isinstance(exp_list, list):
            for exp in exp_list:
                if isinstance(exp, dict):
                    exp_text += " " + exp.get("description", "")
                elif isinstance(exp, str):
                    exp_text += " " + exp  # handle string experience
        elif isinstance(exp_list, str):
            exp_text = exp_list

        if any(word in exp_text.lower() for word in jd_lower.split()):
            score += 5

        # Education / Certifications match
        edu_list = candidate.get("education", [])
        edu_text = ""
        if isinstance(edu_list, list):
            for edu in edu_list:
                if isinstance(edu, dict):
                    edu_text += " " + edu.get("degree", "") + " " + edu.get("institution", "")
                elif isinstance(edu, str):
                    edu_text += " " + edu
        elif isinstance(edu_list, str):
            edu_text = edu_list

        if any(word in edu_text.lower() for word in jd_lower.split()):
            score += 2

        candidate_copy = candidate.copy()
        candidate_copy["score"] = score
        matches.append(candidate_copy)

    # Sort by score descending and return top 5
    top_matches = sorted(matches, key=lambda x: x["score"], reverse=True)[:5]
    return top_matches


