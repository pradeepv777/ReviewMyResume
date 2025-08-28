import re
from collections import Counter
from typing import Dict, List, Tuple, Optional

# Enhanced grammar checking with fallback mechanisms
def _get_language_tool():
    """Initialize language tool with multiple fallback options"""
    try:
        import language_tool_python
        
        # Try different initialization methods in order of preference
        init_methods = [
            # Method 1: Try remote API first (most reliable)
            lambda: language_tool_python.LanguageToolPublicAPI('en-US'),
            # Method 2: Try local installation
            lambda: language_tool_python.LanguageTool('en-US'),
        ]
        
        for i, method in enumerate(init_methods):
            try:
                print(f"Attempting grammar tool initialization method {i+1}...")
                tool = method()
                # Test the tool with a simple sentence
                test_result = tool.check("This is a test.")
                print(f"Grammar tool initialized successfully!")
                return tool
            except Exception as e:
                print(f"Method {i+1} failed: {str(e)}")
                continue
        
        print("All grammar tool initialization methods failed")
        return None
        
    except ImportError as e:
        print(f"language-tool-python not installed: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error initializing language tool: {e}")
        return None

def _basic_grammar_check(text: str) -> Tuple[int, List[str]]:
    """Fallback grammar checker using basic rules"""
    issues = []
    score = 100
    
    # Check for common grammar issues with regex
    checks = [
        (r'\bi\s', "Use capital 'I' instead of lowercase 'i'"),
        (r'\s+([.,:;!?])', "Remove space before punctuation"),
        (r'([.!?])\s*([a-z])', "Capitalize first letter after sentence"),
        (r'\s{2,}', "Remove multiple spaces"),
        (r'\b(teh|tehm|adn|nad|hte)\b', "Fix common typos"),
        (r'\b(recieve)\b', "Correct spelling: 'receive'"),
        (r'\b(seperate)\b', "Correct spelling: 'separate'"),
        (r'\b(definately)\b', "Correct spelling: 'definitely'"),
        (r'\b(managment)\b', "Correct spelling: 'management'"),
        (r'\b(responsibile)\b', "Correct spelling: 'responsible'"),
        (r'\b(experiance)\b', "Correct spelling: 'experience'"),
        (r'\b(developement)\b', "Correct spelling: 'development'"),
    ]
    
    for pattern, message in checks:
        matches = re.findall(pattern, text, re.IGNORECASE)
        if matches:
            issues.append(message)
            score -= min(5, len(matches) * 2)
    
    # Check for sentence structure
    sentences = re.split(r'[.!?]+', text)
    for sentence in sentences[:10]:  # Check first 10 sentences
        sentence = sentence.strip()
        if sentence and len(sentence) > 100:
            issues.append("Consider breaking up long sentences")
            score -= 3
            break
    
    return max(30, score), issues[:5]  # Return max 5 issues

def check_grammar(text: str) -> Tuple[int, List[str]]:
    """Main grammar checking function with fallbacks"""
    if not text or len(text.strip()) < 10:
        return 75, ["Text too short for grammar analysis"]
    
    # Try to use language_tool_python first
    tool = _get_language_tool()
    if tool:
        try:
            # Check first 2000 characters for performance
            check_text = text[:2000] if len(text) > 2000 else text
            matches = tool.check(check_text)
            
            if not matches:
                return 100, ["No grammar issues detected"]
            
            # Filter out style suggestions, keep only real errors
            real_errors = []
            error_messages = []
            
            for match in matches:
                # Skip style suggestions and focus on real errors
                if any(word in match.ruleId.lower() for word in ['style', 'typography', 'whitespace']):
                    continue
                if any(word in match.message.lower() for word in ['consider', 'possible', 'style']):
                    continue
                    
                real_errors.append(match)
                if len(error_messages) < 5:  # Limit to 5 messages
                    error_messages.append(f"{match.message}")
            
            error_count = len(real_errors)
            grammar_score = max(40, 100 - (error_count * 8))
            
            if error_count == 0:
                return 95, ["Excellent grammar and spelling"]
            else:
                return grammar_score, error_messages
                
        except Exception as e:
            print(f"Language tool check failed: {e}")
            # Fall back to basic grammar check
            return _basic_grammar_check(text)
    else:
        # Use basic grammar check as fallback
        print("Using fallback grammar checker")
        return _basic_grammar_check(text)

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
        r'(?:at|@)\s+([A-Z][a-zA-Z\s&.,]+?)(?:\s*[-—"]|\s*\n|,)',
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
    duration_pattern = r'\b(\d+\s*(months?|years?|yrs?)|\w+\s+\d{4}\s*[-—]\s*\w+\s+\d{4})'
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
        feedback.append("Clean, professional layout")
    else:
        feedback.append("🔧 Improve layout consistency and visual hierarchy")
    
    # 3. Grammar & Spelling - ENHANCED VERSION
    print("Starting grammar check...")
    grammar_score, grammar_feedback = check_grammar(original_text)
    breakdown["grammar"] = grammar_score
    score += (grammar_score / 100) * WEIGHTS["grammar"]
    
    if grammar_score >= 95:
        feedback.append("✅ Excellent grammar and spelling")
    elif grammar_score >= 80:
        feedback.append("✅ Good grammar with minor issues")
    else:
        feedback.append("📝 Grammar needs improvement")
    
    # Add specific grammar feedback
    for gf in grammar_feedback[:3]:  # Show max 3 grammar issues
        feedback.append(f"   • {gf}")
    
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
        feedback.append(f"💪 Strong technical skills ({total_skills} across {skill_categories} categories)")
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
        feedback.append(f"📊 Good use of metrics ({len(quantified_results)} quantified results)")
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
        feedback.append(f"🔑 Good industry keyword usage ({keyword_count} found)")
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
    summary = f"Overall Score: {final_score}/100 (Tier {tier})"
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