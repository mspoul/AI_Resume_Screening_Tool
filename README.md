# 🤖 AI Resume Screening Tool

This project is an **AI-powered Resume Screening Tool** built using **Streamlit** and **Sentence Transformers**.  
It compares multiple resumes (PDF or DOCX) against a given Job Description (JD) and ranks candidates by relevance.

---

## 🚀 Features
- Upload and analyze **multiple resumes** (PDF/DOCX)
- Extracts key details like **Experience**, **Email**, and **Contact**
- Calculates **Match Score** using sentence similarity (Hugging Face)
- Generates a **Final Score** combining match score and experience
- Displays results in a **sorted, interactive table**

---

## 🧠 Tech Stack
- **Python 3**
- **Streamlit** (Frontend)
- **Sentence Transformers (MiniLM)** (AI Model)
- **PyMuPDF & python-docx** (File reading)
- **Pandas** (Data handling)

---

## ⚙️ Installation & Run
1. Clone this repository:
   ```bash
   git clone https://github.com/<your-username>/AI_Resume_Screening_Tool.git

   cd AI_Resume_Screening_Tool

   pip install -r requirements.txt

   streamlit run app.py


## 🧩 Input Format

- **Job Description (JD)** → Paste text or upload a PDF file  
- **Resumes** → Upload multiple `.pdf` or `.docx` files  

---

## 🧾 Output Format

- **Extracted Information** → Key details parsed from resumes  
- **Match Score** → Similarity percentage between Job Description and Resume  
- **Final Score** → Weighted combination of Match Score + Candidate Experience  
- **Ranked Results Table** → Displays candidates sorted by highest relevance  


## 👨‍💻 Author

Developed by Suraj — Computer Science Student



