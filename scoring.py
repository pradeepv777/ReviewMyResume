import re
from typing import Dict, List, Tuple

# Scoring weights
WEIGHTS = {
    "ats": 14,
    "design": 10,
    "sections": 14,
    "skills": 16,
    "experience": 14,
    "projects": 12,
    "contact": 6,
    "quantification": 8,
    "keywords": 6
}

SECTION_SYNONYMS = {
    "experience": ["experience", "work experience", "professional experience", "employment"],
    "education": ["education", "academics", "academic background"],
    "skills": ["skills", "technical skills", "tech stack", "technologies"],
    "projects": ["projects", "personal projects", "portfolio"]
}

SKILL_KEYWORDS = [
    "python", "java", "javascript", "c++", "c#", "go", "rust", "typescript",
    "react", "angular", "vue", "html", "css", "sass", "bootstrap", "tailwind",
    "node.js", "express", "django", "flask", "spring", "fastapi",
    "mysql", "postgresql", "mongodb", "redis", "sql",
    "aws", "azure", "gcp", "docker", "kubernetes", "jenkins",
    "git", "github", "gitlab", "jira", "linux", "bash"
]

INDUSTRY_KEYWORDS = [
    "agile", "scrum", "devops", "api", "rest", "testing", "ci/cd",
    "microservices", "cloud", "security", "performance", "optimization"
]

ACTION_VERBS = [
    "developed", "built", "created", "designed", "implemented",
    "led", "managed", "optimized", "improved", "achieved"
]
CONTACT_PATTERNS = {
    "email": r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}",
    "linkedin": r"linkedin\.com\/in\/[\w\-]+",
    "github": r"github\.com\/[\w\-]+"
}

def assign_tier(score: int) -> str:
    if score >= 85: return "A"
    elif score >= 70: return "B"
    elif score >= 50: return "C"
    else: return "D"

def count_skills(text: str) -> int:
    text_lower = text.lower()
    count = 0
    for skill in SKILL_KEYWORDS:
        if re.search(r'\b' + re.escape(skill) + r'\b', text_lower):
            count += 1
    return count

def check_experience(text: str) -> int:
    score = 40
    
    # Check for years of experience
    years_match = re.findall(r'(\d+)\s*(?:\+)?\s*years?', text, re.I)
    if years_match:
        max_years = max([int(y) for y in years_match])
        score += min(25, max_years * 4)
    
    # Check for job titles
    job_titles = ['engineer', 'developer', 'manager', 'analyst', 'architect', 'lead']
    title_count = sum(1 for title in job_titles if re.search(r'\b' + title + r'\b', text, re.I))
    score += min(20, title_count * 7)
    
    # Check for action verbs
    verb_count = sum(1 for verb in ACTION_VERBS if re.search(r'\b' + verb + r'\b', text, re.I))
    score += min(20, verb_count * 3)
    
    # Check for company mentions
    if re.search(r'(?:at|@)\s+[A-Z][a-zA-Z\s&]+', text):
        score += 15
    
    return min(100, score)

def check_projects(text: str) -> int:
    score = 30
    
    # Count project bullets
    project_count = len(re.findall(r'(^|\n)\s*[•\-\*]\s+', text))
    score += min(25, project_count * 8)
    
    # Check for GitHub links
    github_links = len(re.findall(r'github\.com/[\w\-]+/[\w\-]+', text, re.I))
    score += min(20, github_links * 10)
    
    # Check for technology mentions
    if re.search(r'(using|built with|technologies|stack)', text, re.I):
        score += 15
    
    # Check for project dates
    if re.search(r'\b\d{4}\b', text):
        score += 10
    
    return min(100, score)

def check_ats(text: str) -> Tuple[int, List[str]]:
    score = 100
    feedback = []
    word_count = len(text.split())
    
    # Word count check
    if word_count < 300:
        score -= 20
        feedback.append(f"Resume too short ({word_count} words)")
    elif word_count > 1200:
        score -= 10
        feedback.append(f"Resume too long ({word_count} words)")
    
    # Bullet points check
    bullet_count = len(re.findall(r'[•\-\*]', text))
    if bullet_count < 5:
        score -= 15
        feedback.append("Add more bullet points")
    elif bullet_count > 3:
        score += 5
    
    # Special characters check
    special_chars = len(re.findall(r'[^\w\s\.\,\-\(\)\[\]\/\@\#\%\&\+]', text))
    if special_chars > 30:
        score -= 10
        feedback.append("Too many special characters")
    
    # Section headers check
    headers = len(re.findall(r'^\s*[A-Z][A-Za-z\s&]+\s*$', text, re.M))
    if headers < 3:
        score -= 8
        feedback.append("Add clear section headers")
    
    return max(40, score), feedback

def score_resume(parsed_data: Dict) -> Tuple[int, List[str], Dict]:
    text = parsed_data.get("raw_text", "").lower()
    original_text = parsed_data.get("raw_text", "")
    
    score = 0.0
    breakdown = {}
    feedback = []
    
    # 1. ATS Compatibility
    ats_score, ats_feedback = check_ats(original_text)
    breakdown["ats"] = ats_score
    score += ats_score * WEIGHTS["ats"] / 100
    feedback.extend(ats_feedback)
    
    # 2. Design & Layout
    design_score = int(parsed_data.get("design_score", 70))
    breakdown["design"] = design_score
    score += design_score * WEIGHTS["design"] / 100
    if design_score > 80:
        feedback.append("Clean, professional layout")
    else:
        feedback.append("Improve layout and formatting")
    
    # 3. Required Sections
    present = []
    missing = []
    for section, synonyms in SECTION_SYNONYMS.items():
        if any(re.search(r"\b" + re.escape(syn) + r"\b", text) for syn in synonyms):
            present.append(section)
        else:
            missing.append(section)
    
    section_score = (len(present) / len(SECTION_SYNONYMS)) * 100
    breakdown["sections"] = int(section_score)
    score += (section_score / 100) * WEIGHTS["sections"]
    
    if missing:
        feedback.append(f"Missing sections: {', '.join(missing)}")
    else:
        feedback.append("All essential sections present")
    
    # 4. Technical Skills
    skill_count = count_skills(original_text)
    skill_score = min(100, skill_count * 8 + 30)
    breakdown["skills"] = skill_score
    score += (skill_score / 100) * WEIGHTS["skills"]
    
    if skill_count >= 10:
        feedback.append(f"Strong technical skills ({skill_count} found)")
    elif skill_count >= 5:
        feedback.append(f"Good skills ({skill_count} found)")
    else:
        feedback.append(f"Add more technical skills ({skill_count} found)")
    
    # 5. Work Experience
    exp_score = check_experience(original_text)
    breakdown["experience"] = exp_score
    score += (exp_score / 100) * WEIGHTS["experience"]
    
    if exp_score >= 80:
        feedback.append("Well-detailed work experience")
    elif exp_score >= 60:
        feedback.append("Good experience section")
    else:
        feedback.append("Enhance experience with more details")
    
    # 6. Projects
    project_score = check_projects(original_text)
    breakdown["projects"] = project_score
    score += (project_score / 100) * WEIGHTS["projects"]
    
    if project_score >= 75:
        feedback.append("Strong project portfolio")
    else:
        feedback.append("Add more project details and links")
    
    # 7. Contact Information
    contact_score = 0
    contact_found = []
    for contact_type, pattern in CONTACT_PATTERNS.items():
        if re.search(pattern, original_text, re.I):
            contact_score += 33
            contact_found.append(contact_type)
    
    breakdown["contact"] = min(100, contact_score)
    score += (min(100, contact_score) / 100) * WEIGHTS["contact"]
    
    missing_contacts = [c for c in ['email', 'linkedin', 'github'] if c not in contact_found]
    if missing_contacts:
        feedback.append(f"Add missing contact: {', '.join(missing_contacts)}")
    
    # 8. Quantified Achievements
    quant_patterns = [r'\d+%', r'\d+\+', r'\d+x', r'\d+k\b', r'improved.*\d+', r'increased.*\d+']
    quant_count = sum(len(re.findall(p, original_text, re.I)) for p in quant_patterns)
    quant_score = min(100, quant_count * 15 + 40)
    breakdown["quantification"] = quant_score
    score += (quant_score / 100) * WEIGHTS["quantification"]
    
    if quant_count >= 5:
        feedback.append(f"Good use of metrics ({quant_count} found)")
    else:
        feedback.append("Add quantified achievements (numbers, %)")
    
    # 9. Industry Keywords
    keyword_count = sum(1 for kw in INDUSTRY_KEYWORDS if re.search(r'\b' + kw + r'\b', text, re.I))
    keyword_score = min(100, keyword_count * 12 + 40)
    breakdown["keywords"] = keyword_score
    score += (keyword_score / 100) * WEIGHTS["keywords"]
    
    if keyword_count >= 4:
        feedback.append(f"Good keyword usage ({keyword_count} found)")
    else:
        feedback.append("Add industry keywords (agile, API, testing)")
    
    # Final Score Calculation
    final_score = int(round(score))
    tier = assign_tier(final_score)
    
    # Summary message
    if final_score >= 85:
        summary = f"Overall Score: {final_score}/100 (Tier {tier}) - Excellent resume!"
    elif final_score >= 70:
        summary = f"Overall Score: {final_score}/100 (Tier {tier}) - Good foundation"
    elif final_score >= 50:
        summary = f"Overall Score: {final_score}/100 (Tier {tier}) - Needs improvement"
    else:
        summary = f"Overall Score: {final_score}/100 (Tier {tier}) - Significant work needed"
    
    feedback.insert(0, summary)
    return final_score, feedback, breakdown
