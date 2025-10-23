import streamlit as st
import pandas as pd
import fitz
import re
import os
from sentence_transformers import SentenceTransformer, util
from io import BytesIO
from docx import Document
from PIL import Image

# Optional: pytesseract only if installed
try:
    import pytesseract
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False

# Streamlit page config
st.set_page_config(page_title="📄 AI Resume Screening Tool", layout="wide")
st.markdown("<h2 style='text-align: center;'>🤖 AI Resume Screening Tool</h2>", unsafe_allow_html=True)

# Load SentenceTransformer model
@st.cache_resource
def load_model():
    return SentenceTransformer('all-MiniLM-L6-v2')
model = load_model()

# Job Description Input
st.markdown("### 📄 Upload or Paste Job Description")
jd_option = st.radio("Choose JD Input Method:", ["Paste Text", "Upload PDF"])
jd_text = ""
if jd_option == "Paste Text":
    jd_text = st.text_area("Paste the Job Description here:", height=200)
elif jd_option == "Upload PDF":
    jd_pdf = st.file_uploader("Upload JD PDF", type=["pdf"])
    if jd_pdf:
        doc = fitz.open(stream=jd_pdf.read(), filetype="pdf")
        jd_text = "".join([page.get_text("text") for page in doc])

# Resumes Upload
st.markdown("### 📁 Upload Resumes (PDF or DOCX)")
resume_files = st.file_uploader("Upload multiple resumes", type=["pdf", "docx"], accept_multiple_files=True)

# Helper Functions
def extract_text_from_docx(file):
    try:
        doc = Document(file)
        return '\n'.join([para.text for para in doc.paragraphs])
    except:
        return ""

def extract_text_with_ocr(file):
    if not OCR_AVAILABLE:
        return ""
    file.seek(0)
    doc = fitz.open(stream=file.read(), filetype="pdf")
    text = ""
    for page in doc:
        pix = page.get_pixmap(matrix=fitz.Matrix(2,2))
        img_bytes = pix.tobytes("png")
        img = Image.open(BytesIO(img_bytes))
        text += pytesseract.image_to_string(img)
    return text

def extract_resume_text(file):
    file.seek(0)
    if file.type == "application/pdf":
        pdf_text = ""
        doc = fitz.open(stream=file.read(), filetype="pdf")
        for page in doc:
            pdf_text += page.get_text("text")
        if not pdf_text.strip() and OCR_AVAILABLE:
            pdf_text = extract_text_with_ocr(file)
        return pdf_text
    elif file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        return extract_text_from_docx(file)
    return ""

def extract_experience(text):
    patterns = [r'(\d+\.?\d*)\s*(?:\+?\s*)years?.*experience', r'over\s+(\d+\.?\d*)\s*years?', r'(\d+)\s*yrs?\s*exp']
    for p in patterns:
        m = re.search(p, text.lower())
        if m: return f"{m.group(1)} years"
    return "Not mentioned"

def extract_email(text):
    m = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', text)
    return m.group(0) if m else "Not found"

def extract_contact_number(text):
    matches = re.findall(r'(?:\+91|91|0)?[\s\-]?\d{10}', text)
    for match in matches:
        cleaned = re.sub(r'\D', '', match)
        if len(cleaned)>=10:
            return cleaned[-10:]
    return "Not found"

def compute_similarity_score(jd_text, resume_text):
    jd_emb = model.encode(jd_text, convert_to_tensor=True)
    res_emb = model.encode(resume_text, convert_to_tensor=True)
    return round(util.cos_sim(jd_emb,res_emb).item()*100,2)

def composite_score(match_score, experience):
    try: exp_years = float(experience.split()[0])
    except: exp_years=0
    exp_score = min(exp_years*10,30)
    return round(0.7*match_score + exp_score,2)

# Process resumes
if st.button("🔍 Match Resumes"):
    if not jd_text or not resume_files:
        st.warning("Please provide both JD and resumes")
    else:
        st.info("Processing resumes...")
        results=[]
        for f in resume_files:
            text = extract_resume_text(f)
            if not text.strip(): continue
            name = os.path.splitext(f.name)[0]
            exp = extract_experience(text)
            email = extract_email(text)
            contact = extract_contact_number(text)
            match_score = compute_similarity_score(jd_text, text)
            final_score = composite_score(match_score, exp)
            results.append({
                "Rank":0,
                "Name":name,
                "Experience":exp,
                "Email":email,
                "Contact":contact,
                "Match Score":match_score,
                "Final Score":final_score
            })
        if results:
            results_df = pd.DataFrame(results).sort_values(by="Final Score", ascending=False)
            results_df.reset_index(drop=True, inplace=True)
            results_df['Rank'] = range(1,len(results_df)+1)
            st.dataframe(results_df, use_container_width=True)
        else:
            st.warning("No readable resumes found")
