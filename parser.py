import pdfplumber
import re
from typing import Dict, List, Tuple

SECTION_SYNONYMS = {
    "experience": [
        "experience", "work experience", "professional experience", "employment history",
        "career summary", "job history", "work history", "professional background"
    ],
    "education": [
        "education", "academics", "academic background", "educational qualifications",
        "academic qualifications", "education & certifications", "education and training", "scholastics"
    ],
    "skills": [
        "skills", "technical skills", "tech stack", "technologies", "core competencies",
        "programming skills", "technical proficiency", "tools & technologies"
    ],
    "projects": [
        "projects", "personal projects", "academic projects", "project highlights",
        "notable projects", "key projects", "project work", "major projects"
    ]
}

def extract_text_from_pdf(pdf_path: str) -> str:
    text = ""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                # prefer extract_text over raw chars so ligatures get normalized
                page_text = page.extract_text() or ""
                text += page_text + "\n"
            # annotations (hyperlinks)
            for page in pdf.pages:
                if page.annots:
                    for annot in page.annots:
                        uri = annot.get("uri")
                        if uri:
                            text += f"\n{uri}"
    except Exception as e:
        print("Error reading PDF:", e)
    return text

def extract_email(text: str) -> str:
    match = re.search(r'[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}', text)
    return match.group(0) if match else "Not Found"

def extract_phone(text: str) -> str:
    match = re.search(r'\+?\d[\d\s\-\(\)]{8,}\d', text)
    return match.group(0) if match else "Not Found"

def extract_links(text: str) -> Tuple[str, str]:
    linkedin = re.search(r'(https?://)?(www\.)?linkedin\.com/in/[A-Za-z0-9\-_]+', text, flags=re.I)
    github = re.search(r'(https?://)?(www\.)?github\.com/[A-Za-z0-9\-_]+', text, flags=re.I)
    return (
        linkedin.group(0) if linkedin else "Not Found",
        github.group(0) if github else "Not Found"
    )

def extract_skills(text: str) -> List[str]:
    skill_keywords = [
        "python", "java", "sql", "html", "css", "javascript", "react", "node.js",
        "flask", "docker", "pandas", "scikit-learn", "tensorflow", "aws",
        "linux", "git", "github", "mongodb", "machine learning", "deep learning",
        "django", "numpy"
    ]
    skills_found = []
    lower = text.lower()
    for skill in skill_keywords:
        if re.search(r'\b' + re.escape(skill) + r'\b', lower, re.IGNORECASE):
            skills_found.append(skill.title())
    return sorted(set(skills_found))

def _heuristic_ats_score(text: str) -> int:
    # Start at 100, deduct for potential ATS issues
    raw = text
    if not raw:
        return 40
    total_chars = len(raw)
    ascii_printable = sum(ch.isascii() and (31 < ord(ch) < 127 or ch in "\n\t") for ch in raw)
    non_ascii_ratio = 1 - (ascii_printable / max(total_chars, 1))
    score = 100
    # Deduct if many non-ascii/ligature characters
    if non_ascii_ratio > 0.02:
        score -= int(min(30, non_ascii_ratio * 100))
    # Deduct if many consecutive spaces (likely multi-column/tabular layout)
    if re.search(r'[ ]{6,}', raw):
        score -= 15
    # Deduct if very short (low extractable text)
    if total_chars < 800:
        score -= 20
    return max(40, min(100, score))

def _heuristic_design_score(text: str) -> int:
    # Basic readability/layout heuristics
    score = 70
    # Bonus for bullets
    if re.search(r'(^|\n)\s*(•|-|\*)\s+', text):
        score += 10
    # Penalize for long URLs or excessive underlines
    if re.search(r'https?://\S{60,}', text):
        score -= 10
    # Penalize for inconsistent spacing
    if re.search(r'\n\s*\n\s*\n', text):
        score -= 5
    # Penalize if lines are extremely long (no wrapping)
    long_line = any(len(line) > 140 for line in text.splitlines())
    if long_line:
        score -= 10
    return max(40, min(100, score))

def parse_resume(filepath: str) -> Dict:
    text = extract_text_from_pdf(filepath)
    # Keep original-case text for display, lower for detection
    email = extract_email(text)
    phone = extract_phone(text)
    linkedin, github = extract_links(text)
    skills = extract_skills(text)
    ats_parse_rate = _heuristic_ats_score(text)
    design_score = _heuristic_design_score(text)

    return {
        "email": email,
        "phone": phone,
        "linkedin": linkedin,
        "github": github,
        "skills": skills,
        "raw_text": text.lower(),
        "ats_parse_rate": ats_parse_rate,
        "design_score": design_score,
        "file_format": "pdf"
    }
