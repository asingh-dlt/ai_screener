Local Setup Guide: AI Recruiter Dashboard
This guide focuses on running the application directly on your machine using Ollama and Gemma 3.

1. Prerequisites
Before starting, ensure you have the following installed:

Python 3.10 or higher

Ollama: Download from ollama.com

Once Ollama is installed, open your terminal and download the model:
ollama pull gemma3:4b

2. Install Dependencies
Open your terminal in the project folder and run the following command to install all necessary Python libraries:
pip install streamlit pymupdf ollama pandas

What these do:
streamlit: The web interface framework.
pymupdf: Extracts text from PDF resumes.
ollama: Connects the app to your local Gemma 3 model.
pandas: Handles the data tables in the dashboard.

3. How to Run the Project
Start the Ollama Service: Ensure the Ollama app is running in your system tray or background.
Launch the Dashboard: Navigate to your project directory in the terminal and run:
in terminal enter:
streamlit run app.py

Access the App: Your default web browser will open a new tab at: http://localhost:8501

5. Step-by-Step Usage
Tab 1 (Create New Job): Enter a Job ID and paste your Job Description. Click "Save".

Tab 2 (Screening Room): Select the Job ID you just created. Drag and drop your PDF resumes into the uploader. Click "Start Screening".

Tab 3 (Results Dashboard): View the candidates ranked by their match score.

🛠️ Quick Troubleshooting
"Ollama not found": Make sure you ran ollama pull gemma3:4b before starting the app.

PDF Errors: If a resume is a scanned image (not selectable text), PyMuPDF might return empty text. The app is designed to notify you if no text is found.

Database: The app creates a file named recruiter.db in your folder. Do not delete this if you want to keep your saved data.
