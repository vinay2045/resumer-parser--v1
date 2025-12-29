from fastapi import FastAPI, UploadFile, File
from parser import parse_resume
from db import candidates
from gemini_matcher import match_candidates

app = FastAPI()

@app.post("/upload")
async def upload_resume(file: UploadFile = File(...)):
    pdf_bytes = await file.read()
    profile = parse_resume(pdf_bytes)
    candidates.insert_one(profile)
    return {"message": "Uploaded", "candidate_id": profile["candidate_id"]}

@app.post("/match")
async def match(job_requirement: str):
    all_candidates = list(candidates.find({}, {"_id": 0}))  # get all profiles
    top_matches = match_candidates(job_requirement, all_candidates)
    return {"matches": top_matches}  # now includes full profile + score

