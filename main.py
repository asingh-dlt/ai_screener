import sqlite3
import fitz  # PyMuPDF
import re

# Database Setup
def init_db():
    conn = sqlite3.connect('recruiter.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS Jobs 
                      (job_id TEXT PRIMARY KEY, job_title TEXT, job_description TEXT)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS Resumes 
                      (resume_id INTEGER PRIMARY KEY AUTOINCREMENT, job_id TEXT, 
                       name TEXT, score INTEGER, summary TEXT, status TEXT)''')
    conn.commit()
    conn.close()

# PDF Text Extraction
def extract_text_from_pdf(file_bytes):
    doc = fitz.open(stream=file_bytes, filetype="pdf")
    text = ""
    for page in doc:
        text += page.get_text()
    
    # Cleaning: Remove extra whitespaces and non-standard characters
    text = re.sub(r'\s+', ' ', text).strip()
    return text if text else "Error: No text found (Scan/Image?)"
import ollama
import json

def analyze_resume(resume_text, job_desc):
    # Constructing a clear system prompt for local LLMs
    system_prompt = "You are a recruitment assistant. You must analyze the resume against the job description and return ONLY valid JSON."
    
    user_prompt = f"""
    Job Description: {job_desc}
    Resume Text: {resume_text}

    Return a JSON object with:
    {{
        "name": "string",
        "email": "string",
        "experience_years": integer,
        "skills_match_score": integer (0-100),
        "education_score": integer (0-100),
        "summary": "string"
    }}
    """

    response = ollama.chat(
        model='gemma3:4b',
        messages=[
            {'role': 'system', 'content': system_prompt},
            {'role': 'user', 'content': user_prompt}
        ],
        format='json',  # This ensures the output is valid JSON
        options={'temperature': 0}  # Keep it deterministic for scoring
    )
    
    # Ollama returns a dictionary; extract the content string and parse it
    return json.loads(response['message']['content'])
import streamlit as st
import pandas as pd

st.set_page_config(page_title="Recruiter AI Dashboard", layout="wide")
init_db()

st.title("🎯 AI Recruitment Hub")

# Sidebar/Tabs Implementation
tab1, tab2, tab3 = st.tabs(["🆕 Create New Job", "📄 Screening Room", "📊 Results Dashboard"])

# --- TAB 1: CREATE NEW JOB ---
with tab1:
    with st.form("job_form"):
        job_id = st.text_input("Job ID (e.g., SE-101)")
        job_title = st.text_input("Job Title")
        job_desc = st.text_area("Job Description")
        if st.form_submit_button("Save Job"):
            conn = sqlite3.connect('recruiter.db')
            conn.execute("INSERT INTO Jobs VALUES (?, ?, ?)", (job_id, job_title, job_desc))
            conn.commit()
            st.success(f"Job {job_id} saved successfully!")

# --- TAB 2: SCREENING ROOM ---
with tab2:
    conn = sqlite3.connect('recruiter.db')
    jobs_df = pd.read_sql_query("SELECT job_id FROM Jobs", conn)
    
    selected_job = st.selectbox("Select Job ID to Screen For", jobs_df['job_id'])
    
    if selected_job:
        uploaded_files = st.file_uploader("Upload Resumes (PDF)", type="pdf", accept_multiple_files=True)
        
        if st.button("Start Screening") and uploaded_files:
            progress_bar = st.progress(0)
            
            # Fetch the JD for this job
            jd = conn.execute("SELECT job_description FROM Jobs WHERE job_id=?", (selected_job,)).fetchone()[0]
            
            for i, file in enumerate(uploaded_files):
                # 1. Extract
                text = extract_text_from_pdf(file.read())
                
                # 2. Analyze (Gemini)
                data = analyze_resume(text, jd)
                
                # 3. Fitment Logic (Weighting)
                # 60% Skills, 30% Exp (normalized to 100), 10% Education
                weighted_score = (data['skills_match_score'] * 0.6) + \
                                 (min(data['experience_years'] * 10, 100) * 0.3) + \
                                 (data['education_score'] * 0.1)
                
                status = "Shortlisted" if weighted_score >= 70 else "Rejected"
                
                # 4. Save to DB
                conn.execute("INSERT INTO Resumes (job_id, name, score, summary, status) VALUES (?, ?, ?, ?, ?)",
                             (selected_job, data['name'], int(weighted_score), data['summary'], status))
                conn.commit()
                
                progress_bar.progress((i + 1) / len(uploaded_files))
            
            st.success("Screening Complete!")

# --- TAB 3: RESULTS DASHBOARD ---
with tab3:
    conn = sqlite3.connect('recruiter.db')
    results_df = pd.read_sql_query("SELECT * FROM Resumes ORDER BY score DESC", conn)
    
    if not results_df.empty:
        st.dataframe(results_df, use_container_width=True)
    else:
        st.info("No results found. Start screening in the 'Screening Room'.")