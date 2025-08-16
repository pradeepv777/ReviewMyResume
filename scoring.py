import re
from collections import Counter
from typing import Dict, List, Tuple, Optional

# Try to load grammar tool lazily
def _get_language_tool():
    try:
        import language_tool_python
        return language_tool_python.LanguageTool('en-US')
    except Exception:
        return None

# Enhanced weights for more balanced scoring
WEIGHTS = {
    "ats": 12,           # ATS compatibility
    "design": 8,         # Visual design & layout  
    "grammar": 8,        # Grammar and spelling
    "sections": 12,      # Required sections presence
    "skills": 15,        # Technical skills diversity
    "experience": 12,    # Work experience quality
    "projects": 10,      # Projects with details
    "contact": 5,        # Contact information
    "quantification": 8, # Measurable achievements
    "keywords": 6,       # Industry keywords
    "length": 4          # Appropriate length
}

# Enhanced section detection with more synonyms
SECTION_SYNONYMS = {
    "experience": [
        "experience", "work experience", "professional experience", "employment history",
        "career summary", "job history", "work history", "professional background",
        "employment", "career", "positions", "roles"
    ],
    "education": [
        "education", "academics", "academic background", "educational qualifications",
        "academic qualifications", "education & certifications", "education and training", 
        "scholastics", "degrees", "university", "college", "school"
    ],
    "skills": [
        "skills", "technical skills", "tech stack", "technologies", "core competencies",
        "programming skills", "technical proficiency", "tools & technologies",
        "competencies", "abilities", "expertise", "proficiencies"
    ],
    "projects": [
        "projects", "personal projects", "academic projects", "project highlights",
        "notable projects", "key projects", "project work", "major projects",
        "portfolio", "work samples"
    ]
}

# Comprehensive skill categories
SKILL_CATEGORIES = {
    "programming": [
        "python", "java", "javascript", "c++", "c#", "go", "rust", "kotlin", 
        "swift", "php", "ruby", "scala", "typescript", "dart", "r"
    ],
    "web_frontend": [
        "react", "angular", "vue", "html", "css", "sass", "less", "bootstrap",
        "tailwind", "jquery", "webpack", "babel", "next.js", "gatsby"
    ],
    "web_backend": [
        "node.js", "express", "django", "flask", "spring", "laravel", "rails",
        "asp.net", "fastapi", "nestjs", "koa", "meteor"
    ],
    "databases": [
        "mysql", "postgresql", "mongodb", "redis", "cassandra", "sqlite",
        "oracle", "sql server", "dynamodb", "elasticsearch", "neo4j"
    ],
    "cloud": [
        "aws", "azure", "gcp", "docker", "kubernetes", "terraform", "ansible",
        "jenkins", "gitlab", "github actions", "heroku", "vercel", "netlify"
    ],
    "data_science": [
        "pandas", "numpy", "scikit-learn", "tensorflow", "pytorch", "keras",
        "matplotlib", "seaborn", "plotly", "jupyter", "spark", "hadoop"
    ],
    "mobile": [
        "android", "ios", "react native", "flutter", "xamarin", "cordova",
        "ionic", "unity", "unreal engine"
    ],
    "tools": [
        "git", "github", "gitlab", "jira", "confluence", "postman", "figma",
        "photoshop", "illustrator", "sketch", "linux", "bash", "powershell"
    ]
}

# Industry-specific keywords
INDUSTRY_KEYWORDS = [
    "agile", "scrum", "ci/cd", "devops", "microservices", "api", "rest",
    "graphql", "testing", "debugging", "optimization", "performance",
    "security", "authentication", "authorization", "scalability"
]

# Action verbs for experience descriptions
STRONG_ACTION_VERBS = [
    "developed", "built", "created", "designed", "implemented", "led", "managed",
    "optimized", "improved", "reduced", "increased", "achieved", "delivered",
    "launched", "established", "coordinated", "collaborated", "mentored"
]

# Contact patterns
CONTACT_PATTERNS = {
    "email": r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}",
    "phone": r"(\+\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}",
    "linkedin": r"linkedin\.com\/in\/[\w\-]+",
    "github": r"github\.com\/[\w\-]+",
    "portfolio": r"(https?:\/\/)?([\w\-]+\.)+[\w\-]+(\/[\w\-._~:\/?#[\]@!$&'()*+,;%=]*)?",
}

def assign_tier(score: int) -> str:
    """Enhanced tier assignment with better thresholds"""
    if score >= 90:
        return "S"
    elif score >= 80:
        return "A"
    elif score >= 70:
        return "B"
    elif score >= 60:
        return "C"
    else:
        return "D"

def extract_skills_by_category(text: str) -> Dict[str, List[str]]:
    """Extract skills organized by category"""
    found_skills = {}
    text_lower = text.lower()
    
    for category, skills in SKILL_CATEGORIES.items():
        found_skills[category] = []
        for skill in skills:
            # Use word boundary matching for better accuracy
            pattern = r'\b' + re.escape(skill) + r'\b'
            if re.search(pattern, text_lower):
                found_skills[category].append(skill.title())
    
    return found_skills

def analyze_experience_quality(text: str) -> Dict:
    """Analyze quality of work experience descriptions"""
    analysis = {
        'years_mentioned': 0,
        'companies_count': 0,
        'roles_count': 0,
        'action_verbs_count': 0,
        'has_job_titles': False,
        'has_duration': False
    }
    
    # Extract years of experience
    years_pattern = re.compile(r'(\d+)\s*(?:\+)?\s*years?', re.I)
    years_matches = years_pattern.findall(text)
    if years_matches:
        analysis['years_mentioned'] = max([int(y) for y in years_matches])
    
    # Count companies (look for patterns like "at Company" or "Company, Location")
    company_patterns = [
        r'(?:at|@)\s+([A-Z][a-zA-Z\s&.,]+?)(?:\s*[-–]|\s*\n|,)',
        r'([A-Z][a-zA-Z\s&.]+),\s+[A-Z][a-zA-Z\s]+\s*(?:\d{4}|\n)'
    ]
    companies = set()
    for pattern in company_patterns:
        matches = re.findall(pattern, text, re.M)
        companies.update([c.strip() for c in matches if len(c.strip()) > 2])
    analysis['companies_count'] = len(companies)
    
    # Count different role types
    role_patterns = [
        'software engineer', 'developer', 'analyst', 'manager', 'intern',
        'consultant', 'architect', 'lead', 'senior', 'junior', 'principal'
    ]
    roles_found = set()
    for role in role_patterns:
        if re.search(r'\b' + role + r'\b', text, re.I):
            roles_found.add(role)
    analysis['roles_count'] = len(roles_found)
    
    # Count strong action verbs
    action_count = 0
    for verb in STRONG_ACTION_VERBS:
        matches = len(re.findall(r'\b' + verb + r'\b', text, re.I))
        action_count += matches
    analysis['action_verbs_count'] = action_count
    
    # Check for job titles
    job_title_pattern = r'\b(engineer|developer|manager|analyst|consultant|architect|designer|specialist)\b'
    analysis['has_job_titles'] = bool(re.search(job_title_pattern, text, re.I))
    
    # Check for duration mentions (months, years)
    duration_pattern = r'\b(\d+\s*(months?|years?|yrs?)|\w+\s+\d{4}\s*[-–]\s*\w+\s+\d{4})'
    analysis['has_duration'] = bool(re.search(duration_pattern, text, re.I))
    
    return analysis

def analyze_projects_quality(text: str) -> Dict:
    """Analyze quality of project descriptions"""
    analysis = {
        'project_count': 0,
        'has_technologies': False,
        'has_links': False,
        'has_dates': False,
        'has_metrics': False,
        'description_quality': 0
    }
    
    # Count projects (look for bullet points in projects section)
    project_bullets = len(re.findall(r'(^|\n)\s*[•\-\*]\s+', text))
    analysis['project_count'] = project_bullets
    
    # Check for technology mentions
    tech_pattern = r'(?:using|with|built\s+with|technologies?:?|stack:?)\s*([a-zA-Z,\s&.+#-]+)'
    tech_mentions = re.findall(tech_pattern, text, re.I)
    analysis['has_technologies'] = len(tech_mentions) > 0
    
    # Check for project links (GitHub, live demo, etc.)
    link_patterns = [
        r'github\.com\/[\w\-]+\/[\w\-]+',
        r'(demo|live|deployed|hosted).*https?:\/\/[\w\-\.]+',
        r'https?:\/\/[\w\-\.]+\.(herokuapp|vercel|netlify|github\.io)'
    ]
    has_links = any(re.search(pattern, text, re.I) for pattern in link_patterns)
    analysis['has_links'] = has_links
    
    # Check for project dates
    date_patterns = [
        r'\b\d{4}\b',
        r'\b\d{1,2}\/\d{4}\b',
        r'\b(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\w*\s+\d{4}\b'
    ]
    has_dates = any(re.search(pattern, text, re.I) for pattern in date_patterns)
    analysis['has_dates'] = has_dates
    
    # Check for metrics/quantification in projects
    metric_patterns = [
        r'\d+%', r'\d+\+', r'\d+x', r'\d+k\s+(users|downloads|views)',
        r'improved.*\d+', r'reduced.*\d+', r'increased.*\d+'
    ]
    has_metrics = any(re.search(pattern, text, re.I) for pattern in metric_patterns)
    analysis['has_metrics'] = has_metrics
    
    # Assess description quality (length, detail)
    project_section = extract_project_section(text)
    if project_section:
        words_in_projects = len(project_section.split())
        analysis['description_quality'] = min(100, (words_in_projects / 100) * 100)
    
    return analysis

def extract_project_section(text: str) -> str:
    """Extract the projects section from resume text"""
    project_keywords = ['projects', 'portfolio', 'work samples']
    for keyword in project_keywords:
        pattern = rf'(?i)\b{keyword}\b.*?(?=\n\s*\n|\n\s*[A-Z][A-Za-z\s]+:|\Z)'
        match = re.search(pattern, text, re.DOTALL)
        if match:
            return match.group(0)
    return ""

def calculate_ats_score(text: str, parsed_data: Dict) -> Tuple[int, List[str]]:
    """Enhanced ATS compatibility scoring"""
    score = 100
    feedback = []
    
    # Word count analysis (ideal: 400-800 words)
    word_count = len(text.split())
    if word_count < 300:
        score -= 15
        feedback.append(f"Resume too brief ({word_count} words) - add more detail")
    elif word_count > 1200:
        score -= 10
        feedback.append(f"Resume too lengthy ({word_count} words) - consider condensing")
    
    # Check for problematic formatting
    special_chars = len(re.findall(r'[^\w\s\.\,\-\(\)\[\]\/\@\#\%\&\+]', text))
    if special_chars > 30:
        score -= 12
        feedback.append("Too many special characters may confuse ATS systems")
    
    # Check for proper bullet point usage
    bullet_count = len(re.findall(r'(^|\n)\s*[•\-\*]\s+', text))
    if bullet_count < 5:
        score -= 8
        feedback.append("Add more bullet points for better structure")
    
    # Check for consistent date formatting
    date_formats = set()
    date_patterns = [r'\d{4}', r'\d{1,2}\/\d{4}', r'\d{1,2}-\d{4}']
    for pattern in date_patterns:
        if re.search(pattern, text):
            date_formats.add(pattern)
    
    if len(date_formats) > 2:
        score -= 5
        feedback.append("Use consistent date formatting throughout")
    
    # Check for proper section headers
    section_headers = len(re.findall(r'^\s*[A-Z][A-Za-z\s&]+\s*$', text, re.M))
    if section_headers < 3:
        score -= 8
        feedback.append("Add clear section headers")
    
    return max(40, score), feedback

def score_resume(parsed_data: Dict) -> Tuple[int, List[str], Dict]:
    """Enhanced resume scoring with comprehensive analysis"""
    text = parsed_data.get("raw_text", "").lower()
    original_text = parsed_data.get("raw_text", "")  # Keep original case for some analysis
    
    score = 0.0
    breakdown = {}
    feedback = []
    
    # 1. ATS Compatibility
    ats_score, ats_feedback = calculate_ats_score(original_text, parsed_data)
    breakdown["ats"] = ats_score
    score += ats_score * WEIGHTS["ats"] / 100
    feedback.extend(ats_feedback)
    
    # 2. Design & Layout
    design_score = int(parsed_data.get("design_score", 70))
    breakdown["design"] = design_score
    score += design_score * WEIGHTS["design"] / 100
    if design_score > 80:
        feedback.append("✅ Clean, professional layout")
    else:
        feedback.append("📐 Improve layout consistency and visual hierarchy")
    
    # 3. Grammar & Spelling
    tool = _get_language_tool()
    if tool and text.strip():
        try:
            matches = tool.check(original_text[:1000])  # Check first 1000 chars for performance
            grammar_issues = len(matches)
            grammar_score = max(30, 100 - (grammar_issues * 3))
            breakdown["grammar"] = grammar_score
            score += (grammar_score / 100) * WEIGHTS["grammar"]
            
            if grammar_issues == 0:
                feedback.append("✅ No grammar issues detected")
            else:
                feedback.append(f"📝 Fix {grammar_issues} grammar/spelling issue{'s' if grammar_issues != 1 else ''}")
                # Show top issues
                for match in matches[:3]:
                    feedback.append(f"   • {match.message}")
        except Exception:
            breakdown["grammar"] = 75
            score += 0.75 * WEIGHTS["grammar"]
            feedback.append("⚠️ Grammar check unavailable")
    else:
        breakdown["grammar"] = 75
        score += 0.75 * WEIGHTS["grammar"]
        feedback.append("⚠️ Grammar check unavailable")
    
    # 4. Required Sections
    present_sections = []
    missing_sections = []
    
    for section, synonyms in SECTION_SYNONYMS.items():
        found = any(re.search(r"\b" + re.escape(syn) + r"\b", text) for syn in synonyms)
        if found:
            present_sections.append(section)
        else:
            missing_sections.append(section)
    
    section_score = (len(present_sections) / len(SECTION_SYNONYMS)) * 100
    breakdown["sections"] = int(section_score)
    score += (section_score / 100) * WEIGHTS["sections"]
    
    if missing_sections:
        feedback.append(f"📋 Add missing sections: {', '.join(missing_sections)}")
    else:
        feedback.append("✅ All essential sections present")
    
    # 5. Skills Analysis
    skills_by_category = extract_skills_by_category(original_text)
    total_skills = sum(len(skills) for skills in skills_by_category.values())
    skill_categories = len([cat for cat, skills in skills_by_category.items() if skills])
    
    # Score based on both quantity and diversity
    skill_score = min(100, (total_skills * 3) + (skill_categories * 10))
    breakdown["skills"] = skill_score
    score += (skill_score / 100) * WEIGHTS["skills"]
    
    if skill_score >= 80:
        feedback.append(f"✅ Strong technical skills ({total_skills} across {skill_categories} categories)")
    else:
        feedback.append(f"🛠️ Expand technical skills ({total_skills} found) - add more technologies")
    
    # 6. Experience Quality
    exp_analysis = analyze_experience_quality(original_text)
    exp_score = 0
    
    # Score factors
    if exp_analysis['years_mentioned'] > 0:
        exp_score += min(30, exp_analysis['years_mentioned'] * 5)
    if exp_analysis['companies_count'] > 0:
        exp_score += min(20, exp_analysis['companies_count'] * 10)
    if exp_analysis['has_job_titles']:
        exp_score += 20
    if exp_analysis['has_duration']:
        exp_score += 15
    if exp_analysis['action_verbs_count'] > 5:
        exp_score += 15
    
    exp_score = min(100, max(30, exp_score))
    breakdown["experience"] = exp_score
    score += (exp_score / 100) * WEIGHTS["experience"]
    
    if exp_score >= 80:
        feedback.append("✅ Well-detailed work experience")
    else:
        feedback.append("💼 Enhance experience with more details, action verbs, and quantified results")
    
    # 7. Projects Quality
    project_analysis = analyze_projects_quality(original_text)
    project_score = 40  # Base score
    
    if project_analysis['project_count'] > 0:
        project_score += min(20, project_analysis['project_count'] * 5)
    if project_analysis['has_technologies']:
        project_score += 15
    if project_analysis['has_links']:
        project_score += 15
    if project_analysis['has_dates']:
        project_score += 10
    
    project_score = min(100, project_score)
    breakdown["projects"] = project_score
    score += (project_score / 100) * WEIGHTS["projects"]
    
    if project_score >= 80:
        feedback.append("✅ Strong project portfolio")
    else:
        improvements = []
        if not project_analysis['has_technologies']:
            improvements.append("technologies used")
        if not project_analysis['has_links']:
            improvements.append("GitHub links")
        if not project_analysis['has_dates']:
            improvements.append("project dates")
        feedback.append(f"🚀 Enhance projects by adding: {', '.join(improvements)}")
    
    # 8. Contact Information
    contact_score = 0
    contact_found = []
    
    for contact_type, pattern in CONTACT_PATTERNS.items():
        if re.search(pattern, original_text, re.I):
            contact_found.append(contact_type)
            contact_score += 20
    
    contact_score = min(100, contact_score)
    breakdown["contact"] = contact_score
    score += (contact_score / 100) * WEIGHTS["contact"]
    
    missing_contacts = [c for c in ['email', 'linkedin', 'github'] if c not in contact_found]
    if missing_contacts:
        feedback.append(f"📧 Add missing contact info: {', '.join(missing_contacts)}")
    else:
        feedback.append("✅ Complete contact information")
    
    # 9. Quantification
    quantification_patterns = [
        r'\d+%', r'\d+\+', r'\d+x', r'\d+k\b', r'\d+m\b',
        r'\$\d+', r'\d+\s*(users|customers|projects|hours)',
        r'(improved|increased|reduced|decreased).*\d+'
    ]
    
    quantified_results = []
    for pattern in quantification_patterns:
        matches = re.findall(pattern, original_text, re.I)
        quantified_results.extend(matches)
    
    quant_score = min(100, len(quantified_results) * 15 + 40)
    breakdown["quantification"] = quant_score
    score += (quant_score / 100) * WEIGHTS["quantification"]
    
    if quant_score >= 80:
        feedback.append(f"✅ Good use of metrics ({len(quantified_results)} quantified results)")
    else:
        feedback.append("📊 Add more quantified achievements (percentages, numbers, impact)")
    
    # 10. Industry Keywords
    keyword_count = 0
    for keyword in INDUSTRY_KEYWORDS:
        if re.search(r'\b' + re.escape(keyword) + r'\b', text, re.I):
            keyword_count += 1
    
    keyword_score = min(100, (keyword_count / len(INDUSTRY_KEYWORDS)) * 100 + 40)
    breakdown["keywords"] = keyword_score
    score += (keyword_score / 100) * WEIGHTS["keywords"]
    
    if keyword_score >= 70:
        feedback.append(f"✅ Good industry keyword usage ({keyword_count} found)")
    else:
        feedback.append("🔍 Include more industry-relevant keywords (agile, API, testing, etc.)")
    
    # 11. Length Appropriateness
    word_count = len(original_text.split())
    if 400 <= word_count <= 800:
        length_score = 100
    elif 300 <= word_count <= 1000:
        length_score = 85
    elif word_count < 300:
        length_score = max(40, (word_count / 300) * 100)
    else:  # > 1000
        length_score = max(60, 100 - ((word_count - 1000) / 20))
    
    breakdown["length"] = int(length_score)
    score += (length_score / 100) * WEIGHTS["length"]
    
    # Final calculations
    final_score = int(round(score))
    tier = assign_tier(final_score)
    
    # Add summary feedback at the beginning
    summary = f"🎯 Overall Score: {final_score}/100 (Tier {tier})"
    if final_score >= 90:
        summary += " - Outstanding! Your resume is highly competitive."
    elif final_score >= 80:
        summary += " - Excellent! Minor improvements will make it perfect."
    elif final_score >= 70:
        summary += " - Good foundation with room for enhancement."
    elif final_score >= 60:
        summary += " - Decent start, focus on key improvements."
    else:
        summary += " - Significant improvements needed."
    
    feedback.insert(0, summary)
    
    return final_score, feedback, breakdown