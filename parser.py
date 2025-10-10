import pdfplumber
import re
from typing import Dict

def extract_text_from_pdf(pdf_path: str) -> str:
    text = ""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                
                page_text = page.extract_text() or ""
                text += page_text + "\n"
            # Section for links
            for page in pdf.pages:
                if page.annots:
                    for annot in page.annots:
                        uri = annot.get("uri")
                        if uri:
                            text += f"\n{uri}"
    except Exception as e:
        print("Error reading PDF:", e)
    return text

def _heuristic_ats_score(text: str) -> int:
    # we start at 100, deduct for potential ATS issues
    raw = text
    if not raw:
        return 40
    total_chars = len(raw)
    ascii_printable = sum(ch.isascii() and (31 < ord(ch) < 127 or ch in "\n\t") for ch in raw)
    non_ascii_ratio = 1 - (ascii_printable / max(total_chars, 1))
    score = 100
    
    if non_ascii_ratio > 0.02:
        score -= int(min(30, non_ascii_ratio * 100))
   
    if re.search(r'[ ]{6,}', raw):
        score -= 15
  
    if total_chars < 800:
        score -= 20
    return max(40, min(100, score))

def _heuristic_design_score(text: str) -> int:
    
    score = 70
    
    if re.search(r'(^|\n)\s*(•|-|\*)\s+', text):
        score += 10
    
    if re.search(r'https?://\S{60,}', text):
        score -= 10
    
    if re.search(r'\n\s*\n\s*\n', text):
        score -= 5
    
    long_line = any(len(line) > 140 for line in text.splitlines())
    if long_line:
        score -= 10
    return max(40, min(100, score))

def parse_resume(filepath: str) -> Dict:
    text = extract_text_from_pdf(filepath)
    ats_parse_rate = _heuristic_ats_score(text)
    design_score = _heuristic_design_score(text)

    return {
        "raw_text": text.lower(),
        "ats_parse_rate": ats_parse_rate,
        "design_score": design_score
    }
