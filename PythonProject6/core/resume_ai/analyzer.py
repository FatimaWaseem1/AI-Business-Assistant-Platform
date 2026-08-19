"""
core/resume_ai/analyzer.py

Ported from resume-analyzer-nlp (unchanged logic, only the import path for
skills_list is adjusted for this package's location). Runs entirely offline:
TF-IDF + cosine similarity (keyword-based) blended with Sentence Transformer
embeddings (meaning-based), plus rule-based checks for sections, action
verbs, quantified achievements, and contact info completeness.
"""

import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer, util

from .skills_list import SKILLS_LIST

# Loaded once at import time — sentence-transformers downloads/caches this
# model on first run (30-60s the very first time, then instant).
semantic_model = SentenceTransformer('all-MiniLM-L6-v2')

REQUIRED_SECTIONS = ["experience", "education", "skills"]
RECOMMENDED_SECTIONS = ["summary", "projects", "certifications"]

STRONG_VERBS = [
    "led", "managed", "developed", "designed", "implemented", "built",
    "created", "launched", "optimized", "improved", "increased", "reduced",
    "achieved", "delivered", "architected", "spearheaded", "drove",
    "streamlined", "automated", "negotiated", "mentored"
]

WEAK_PHRASES = [
    "responsible for", "worked on", "helped with", "was involved in",
    "duties included", "tasked with"
]


def clean_text(text):
    text = text.lower()
    text = re.sub(r'[^a-z0-9\s]', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def extract_skills(text):
    text = text.lower()
    return [skill for skill in SKILLS_LIST if skill in text]


def get_match_score(resume_text, jd_text):
    resume_clean = clean_text(resume_text)
    jd_clean = clean_text(jd_text)
    documents = [resume_clean, jd_clean]
    vectorizer = TfidfVectorizer(stop_words="english")
    tfidf_matrix = vectorizer.fit_transform(documents)
    score = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])
    return round(float(score[0][0]) * 100, 2)


def get_semantic_score(resume_text, jd_text):
    embeddings = semantic_model.encode([resume_text, jd_text])
    similarity = util.cos_sim(embeddings[0], embeddings[1])
    return round(float(similarity[0][0]) * 100, 2)


def detect_sections(resume_text):
    text_lower = resume_text.lower()
    found_required = [s for s in REQUIRED_SECTIONS if s in text_lower]
    found_recommended = [s for s in RECOMMENDED_SECTIONS if s in text_lower]
    missing_required = [s for s in REQUIRED_SECTIONS if s not in found_required]
    return {
        "found_required": found_required,
        "missing_required": missing_required,
        "found_recommended": found_recommended
    }


def check_quantifiable_achievements(resume_text):
    number_pattern = r'\b\d+[\d,]*\.?\d*\s*(%|percent|\$|million|thousand|k\b)?'
    matches = re.findall(number_pattern, resume_text.lower())
    quantified_count = len([m for m in matches if m])
    lines = resume_text.split('\n')
    bullet_lines = [l for l in lines if len(l.strip()) > 20]
    total_bullets = max(len(bullet_lines), 1)
    quantified_ratio = round((quantified_count / total_bullets) * 100, 1)
    return {
        "quantified_count": quantified_count,
        "quantified_ratio": min(quantified_ratio, 100)
    }


def check_action_verbs(resume_text):
    text_lower = resume_text.lower()
    strong_count = sum(1 for verb in STRONG_VERBS if verb in text_lower)
    weak_matches = [phrase for phrase in WEAK_PHRASES if phrase in text_lower]
    return {
        "strong_verb_count": strong_count,
        "weak_phrases_found": weak_matches
    }


def check_contact_info(resume_text):
    issues = []
    has_email = bool(re.search(r'[\w.-]+@[\w.-]+\.\w+', resume_text))
    has_phone = bool(re.search(r'(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}', resume_text))
    has_linkedin = "linkedin" in resume_text.lower()
    if not has_email:
        issues.append("No email address found.")
    if not has_phone:
        issues.append("No phone number found.")
    if not has_linkedin:
        issues.append("No LinkedIn profile mentioned — consider adding one.")
    return {
        "has_email": has_email,
        "has_phone": has_phone,
        "has_linkedin": has_linkedin,
        "issues": issues
    }


def student_specific_tips(resume_text):
    tips = []
    text_lower = resume_text.lower()
    if "project" not in text_lower:
        tips.append("As a student, consider adding a 'Projects' section.")
    if "certification" not in text_lower and "certificate" not in text_lower:
        tips.append("Consider adding relevant certifications if you have any.")
    if "gpa" not in text_lower:
        tips.append("If your GPA is strong (3.5+), consider including it.")
    return tips


def generate_suggestions(missing_skills, score):
    suggestions = []
    if missing_skills:
        skills_str = ", ".join(missing_skills)
        suggestions.append(f"Consider highlighting these skills if you have them: {skills_str}")
    if score < 40:
        suggestions.append("Your resume has low overlap with this job description. Try using more of the same keywords and phrasing found in the JD.")
    elif score < 70:
        suggestions.append("Decent overlap, but there's room to better align your resume's language with the job description.")
    else:
        suggestions.append("Strong match! Your resume aligns well with this job description.")
    if len(missing_skills) > 5:
        suggestions.append("You're missing several key skills the JD asks for.")
    return suggestions


def analyze_resume(resume_text, jd_text):
    try:
        resume_skills = extract_skills(resume_text)
        jd_skills = extract_skills(jd_text)
        matched = list(set(resume_skills) & set(jd_skills))
        missing = list(set(jd_skills) - set(resume_skills))

        tfidf_score = get_match_score(resume_text, jd_text)
        semantic_score = get_semantic_score(resume_text, jd_text)
        final_score = round((tfidf_score * 0.3) + (semantic_score * 0.7), 2)

        sections = detect_sections(resume_text)
        achievements = check_quantifiable_achievements(resume_text)
        verbs = check_action_verbs(resume_text)
        contact = check_contact_info(resume_text)

        content_score = min(100, (achievements['quantified_ratio'] * 0.6) + (verbs['strong_verb_count'] * 4))
        format_score = 100 - (len(sections['missing_required']) * 25) - (len(contact['issues']) * 10)
        format_score = max(format_score, 0)
        keyword_score = final_score

        overall_professional_score = round(
            (content_score * 0.35) + (format_score * 0.25) + (keyword_score * 0.4), 1
        )

        suggestions = generate_suggestions(missing, final_score)
        if sections['missing_required']:
            suggestions.append(f"Add these missing sections: {', '.join(sections['missing_required'])}.")
        if verbs['weak_phrases_found']:
            suggestions.append(f"Replace weak phrases like '{verbs['weak_phrases_found'][0]}' with strong action verbs.")
        if achievements['quantified_ratio'] < 30:
            suggestions.append("Add more numbers/metrics to quantify your achievements.")
        suggestions.extend(contact['issues'])
        suggestions.extend(student_specific_tips(resume_text))

        return {
            "resume_skills": resume_skills,
            "jd_required_skills": jd_skills,
            "matched_skills": matched,
            "missing_skills": missing,
            "tfidf_score": tfidf_score,
            "semantic_score": semantic_score,
            "match_score": final_score,
            "overall_professional_score": overall_professional_score,
            "content_score": round(content_score, 1),
            "format_score": round(format_score, 1),
            "keyword_score": round(keyword_score, 1),
            "sections": sections,
            "achievements": achievements,
            "verbs": verbs,
            "contact": contact,
            "suggestions": suggestions
        }
    except Exception as e:
        return {"error": f"Something went wrong: {str(e)}"}