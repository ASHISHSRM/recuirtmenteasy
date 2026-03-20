"""RecruitAI v2 — Flask Backend for Resume Screening"""

import os
import io
import json
import PyPDF2
import docx
import requests
from dotenv import load_dotenv

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

load_dotenv()

print("=" * 60)
print("🚀 RecruitAI v2 Backend Starting...")
print("=" * 60)

# Get the directory where this app.py is located
APP_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.join(APP_DIR, "frontend")

# Configure Flask with static folder for frontend files
app = Flask(
    __name__, 
    static_folder=FRONTEND_DIR,
    static_url_path=""
)
CORS(app)

# Health check endpoint (keeps Railway from stopping the app)
@app.route("/health", methods=["GET"])
def health():
    """Health check endpoint for deployment monitoring"""
    return jsonify({
        "status": "ok",
        "app": "RecruitAI Resume Screening Backend",
        "version": "2.0",
        "tfidf_ready": True,
        "external_apis_needed": False,
        "processing_mode": "Local (100% offline)"
    }), 200

@app.route("/")
def serve_index():
    """Serve frontend index.html"""
    try:
        return send_from_directory(FRONTEND_DIR, "index.html")
    except Exception as e:
        print(f"[ERROR] Failed to serve index.html: {e}")
        print(f"[DEBUG] FRONTEND_DIR = {FRONTEND_DIR}")
        print(f"[DEBUG] Frontend exists: {os.path.exists(FRONTEND_DIR)}")
        if os.path.exists(FRONTEND_DIR):
            print(f"[DEBUG] Files: {os.listdir(FRONTEND_DIR)}")
        return jsonify({"error": "Frontend not found"}), 500

@app.route("/<path:path>")
def serve_static(path):
    """Serve frontend static assets"""
    file_path = os.path.join(FRONTEND_DIR, path)
    
    # Security check
    if not os.path.abspath(file_path).startswith(os.path.abspath(FRONTEND_DIR)):
        return jsonify({"error": "Forbidden"}), 403
    
    if os.path.isfile(file_path):
        return send_from_directory(FRONTEND_DIR, path)
    
    # SPA fallback
    if not path.startswith("screen") and not path.startswith("export"):
        try:
            return send_from_directory(FRONTEND_DIR, "index.html")
        except Exception as e:
            return jsonify({"error": f"Not found: {path}"}), 404
    
    return jsonify({"error": f"Not found: {path}"}), 404

print("⏳ Initializing TF-IDF vectorizer...")
VECTORIZER = TfidfVectorizer(max_features=500, stop_words='english')
print("✅ TF-IDF vectorizer ready.")

# Scoring weights - 100% local processing, NO external APIs needed
# Hybrid scoring: 75% Skill Match + 25% TF-IDF
SKILL_WEIGHT = 0.75
TFIDF_WEIGHT = 0.25

print("✅ All processing will be done locally (no external APIs required).")
print("📊 Scoring: 75% Skill Match + 25% TF-IDF")

print("=" * 60)
print("✅ RecruitAI v2 Backend Ready!")
print("=" * 60)

SUPPORTED_EXTS = {"pdf", "docx", "doc", "txt"}

# Technical Skills Database
TECHNICAL_SKILLS = {
    "programming": ["python", "javascript", "java", "c++", "c#", "php", "ruby", "go", "rust", "kotlin", "typescript"],
    "frontend": ["html", "css", "react", "angular", "vue", "vuejs", "tailwind", "bootstrap", "webpack"],
    "backend": ["django", "flask", "nodejs", "express", "spring", "fastapi", "graphql", "rest api"],
    "databases": ["sql", "mysql", "postgresql", "mongodb", "firebase", "redis", "elasticsearch"],
    "devops": ["docker", "kubernetes", "aws", "gcp", "azure", "jenkins", "gitlab", "github", "terraform"],
    "ai_ml": ["machine learning", "deep learning", "tensorflow", "keras", "pytorch", "scikit-learn", "nlp", "cv"],
    "tools": ["git", "jira", "agile", "scrum", "linux", "unix", "windows"],
}

SOFT_SKILLS = ["communication", "leadership", "teamwork", "problem solving", "project management", 
               "time management", "collaboration", "analytical", "critical thinking", "adaptability"]

def extract_skills(text: str) -> dict:
    """Extract technical and soft skills from text"""
    text_lower = text.lower()
    found_technical = {}
    found_soft = []
    
    for category, skills in TECHNICAL_SKILLS.items():
        for skill in skills:
            if skill in text_lower:
                if category not in found_technical:
                    found_technical[category] = []
                found_technical[category].append(skill.upper())
    
    for skill in SOFT_SKILLS:
        if skill in text_lower:
            found_soft.append(skill.title())
    
    return {
        "technical": found_technical,
        "soft": list(set(found_soft))  # Remove duplicates
    }

def extract_requirements(jd: str) -> dict:
    """Extract key requirements from JD"""
    jd_lower = jd.lower()
    
    # Look for experience level
    experience_level = "Not Specified"
    if "internship" in jd_lower or "entry level" in jd_lower:
        experience_level = "Entry Level"
    elif "0-2 years" in jd_lower or "junior" in jd_lower:
        experience_level = "Junior (0-2 years)"
    elif "2-5 years" in jd_lower or "mid level" in jd_lower or "mid-level" in jd_lower:
        experience_level = "Mid-Level (2-5 years)"
    elif "5+ years" in jd_lower or "senior" in jd_lower:
        experience_level = "Senior (5+ years)"
    
    required_skills = extract_skills(jd)
    
    return {
        "experience_level": experience_level,
        "required_skills": required_skills
    }

def calculate_skill_match(jd_skills: dict, resume_skills: dict) -> float:
    """Calculate skill match percentage"""
    jd_tech_skills = set()
    for category_skills in jd_skills.get("technical", {}).values():
        jd_tech_skills.update([s.lower() for s in category_skills])
    
    resume_tech_skills = set()
    for category_skills in resume_skills.get("technical", {}).values():
        resume_tech_skills.update([s.lower() for s in category_skills])
    
    if not jd_tech_skills:
        return 50.0  # Neutral score if JD has no identified skills
    
    matched = len(jd_tech_skills.intersection(resume_tech_skills))
    match_percentage = (matched / len(jd_tech_skills)) * 100
    return min(100, match_percentage)

def extract_text(file) -> str:
    """Extract text from PDF, DOCX, DOC, or TXT files"""
    filename = file.filename.lower()
    
    try:
        if filename.endswith('.pdf'):
            pdf_reader = PyPDF2.PdfReader(file)
            text = "\n".join(page.extract_text() for page in pdf_reader.pages)
            return text.strip()
        
        elif filename.endswith('.docx'):
            doc = docx.Document(file)
            return "\n".join(paragraph.text for paragraph in doc.paragraphs)
        
        elif filename.endswith('.doc'):
            print(f"⚠️  .doc format detected. Converting...")
            return "[DOC file detected - limited support]"
        
        elif filename.endswith('.txt'):
            return file.read().decode('utf-8', errors='ignore')
        
        else:
            return ""
    
    except Exception as e:
        print(f"[ERROR] extract_text: {str(e)}")
        return ""

def compute_bert_score(jd: str, resume: str) -> int:
    """Compute resume-JD similarity using TF-IDF (0-100)"""
    try:
        if not jd or not resume:
            return 0
        
        corpus = [jd, resume]
        tfidf_matrix = VECTORIZER.fit_transform(corpus)
        similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
        
        score = int(round(similarity * 100))
        return max(0, min(100, score))
    
    except Exception as e:
        print(f"[ERROR] compute_bert_score: {str(e)}")
        return 0

def screen_resume(jd: str, resume: str, candidate_name: str = "Unknown") -> dict:
    """Local resume screening with skill analysis (no external APIs required)"""
    
    # TF-IDF semantic similarity score
    tfidf_score = compute_bert_score(jd, resume)
    
    # Extract requirements and skills
    jd_requirements = extract_requirements(jd)
    jd_skills = jd_requirements["required_skills"]
    resume_skills = extract_skills(resume)
    
    # Calculate skill match percentage
    skill_match = calculate_skill_match(jd_skills, resume_skills)
    
    # Identify strengths and gaps
    jd_tech_skills = set()
    for category_skills in jd_skills.get("technical", {}).values():
        jd_tech_skills.update([s.lower() for s in category_skills])
    
    resume_tech_skills = set()
    for category_skills in resume_skills.get("technical", {}).values():
        resume_tech_skills.update([s.lower() for s in category_skills])
    
    strengths = list(jd_tech_skills.intersection(resume_tech_skills))
    gaps = list(jd_tech_skills - resume_tech_skills)
    
    # Hybrid score: 75% Skill Match + 25% TF-IDF
    combined_score = (skill_match * SKILL_WEIGHT) + (tfidf_score * TFIDF_WEIGHT)
    
    # Classification: Strong Hire (>=75), Mid Hire (60-75), No Hire (<60)
    if combined_score >= 75:
        recommendation = "🟢 Strong Hire"
    elif combined_score >= 60:
        recommendation = "🟡 Mid Hire"
    else:
        recommendation = "🔴 No Hire"
    
    return {
        "candidate_name": candidate_name,
        "tfidf_score": tfidf_score,
        "skill_match": round(skill_match, 2),
        "combined_score": round(combined_score, 2),
        "recommendation": recommendation,
        "key_strengths": [s.title() for s in list(strengths)[:5]],
        "key_gaps": [s.title() for s in list(gaps)[:5]],
        "total_required_skills": len(jd_tech_skills),
        "matched_skills": len(strengths)
    }

@app.route("/screen", methods=["POST"])
def screen():
    """Screen resumes against job description"""
    print(f"[SCREEN] Screening request received")
    
    try:
        jd = ""
        jd_file = request.files.get("jd_file")
        jd_text = request.form.get("jd_text", "").strip()
        
        if jd_file:
            jd = extract_text(jd_file)
        elif jd_text:
            jd = jd_text
        
        if not jd:
            return jsonify({"success": False, "error": "No job description provided"}), 400
        
        resume_files = request.files.getlist("resume_files")
        if not resume_files:
            return jsonify({"success": False, "error": "No resumes provided"}), 400
        
        results = []
        errors = []
        
        for file in resume_files:
            if not file or not file.filename:
                continue
            
            ext = file.filename.rsplit(".", 1)[-1].lower()
            if ext not in SUPPORTED_EXTS:
                errors.append(f"{file.filename}: Unsupported format")
                continue
            
            try:
                resume_text = extract_text(file)
                if not resume_text:
                    errors.append(f"{file.filename}: Could not extract text")
                    continue
                
                filename = file.filename.rsplit(".", 1)[0]
                screening_result = screen_resume(jd, resume_text, filename)
                
                results.append({
                    "filename": file.filename,
                    "candidate_name": screening_result["candidate_name"],
                    "tfidf_score": screening_result["tfidf_score"],
                    "skill_match": screening_result["skill_match"],
                    "combined_score": screening_result["combined_score"],
                    "recommendation": screening_result["recommendation"],
                    "strengths": screening_result["key_strengths"],
                    "gaps": screening_result["key_gaps"],
                    "matched_skills": screening_result["matched_skills"],
                    "total_required_skills": screening_result["total_required_skills"]
                })
            
            except Exception as e:
                print(f"[ERROR] {file.filename}: {str(e)}")
                errors.append(f"{file.filename}: {str(e)}")
                continue
        
        if not results:
            return jsonify({
                "success": False,
                "error": "No candidates could be processed.",
                "details": errors
            }), 500
        
        results.sort(key=lambda x: x["combined_score"], reverse=True)
        
        return jsonify({
            "success": True,
            "total": len(results),
            "errors": errors,
            "results": results
        })
    
    except Exception as e:
        print(f"[ERROR] Screening failed: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500

# Production: Gunicorn runs the app directly
# No app.run() needed - gunicorn handles the server
