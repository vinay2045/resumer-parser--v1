import streamlit as st
import requests

st.title("Resume Matcher System")

st.header("Upload Resume")
file = st.file_uploader("Upload PDF", type="pdf")

if file:
    try:
        res = requests.post(
            "http://localhost:8000/upload",
            files={"file": (file.name, file.getvalue(), "application/pdf")}
        )
        if res.status_code == 200:
            st.success("Resume uploaded successfully")
            st.write(res.json())
        else:
            st.error(f"Upload failed: {res.text}")
    except Exception as e:
        st.error(f"Error uploading file: {e}")

st.header("Find Matching Candidates")
job_req = st.text_area("Enter Job Requirement")

if st.button("Find Candidates"):
    if not job_req.strip():
        st.warning("Please enter a job requirement")
    else:
        try:
            res = requests.post(
                "http://localhost:8000/match",
                params={"job_requirement": job_req.strip()}
            )
            if res.status_code == 200:
                matches = res.json().get("matches", [])
                if matches:
                    st.subheader("Top 5 Matches")
                    for i, cand in enumerate(matches, start=1):
                        st.markdown(f"### {i}. {cand.get('name', 'N/A')} - Score: {cand.get('score',0)}")
                        st.write(cand)  # full profile
                else:
                    st.info("No matching candidates found")
            else:
                st.error(f"Matching failed: {res.text}")
        except Exception as e:
            st.error(f"Error calling backend: {e}")
