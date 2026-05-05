from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import re


def extract_keywords_tfidf(job_description: str, top_n: int = 15) -> list:
    """
    Extract most important keywords from job description using TF-IDF.
    These are the words an ATS system would weight most heavily.
    """
    # Clean text
    cleaned = re.sub(r'[^\w\s]', ' ', job_description.lower())
    
    # Common stopwords to filter
    stopwords = {
        'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to',
        'for', 'of', 'with', 'by', 'from', 'is', 'are', 'was', 'were',
        'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did', 'will',
        'would', 'could', 'should', 'may', 'might', 'shall', 'can',
        'we', 'you', 'they', 'it', 'this', 'that', 'our', 'your',
        'their', 'its', 'we', 'us', 'him', 'her', 'them', 'who', 'which',
        'also', 'as', 'if', 'than', 'then', 'so', 'yet', 'both', 'each',
        'more', 'most', 'other', 'some', 'such', 'no', 'not', 'only',
        'same', 'any', 'including', 'good', 'strong', 'understanding',
        'experience', 'knowledge', 'ability', 'skills', 'looking', 'role',
        'candidate', 'team', 'work', 'working', 'using', 'use', 'used'
    }
    
    words = [w for w in cleaned.split() if w not in stopwords and len(w) > 2]
    
    if not words:
        return []
    
    # Use TF-IDF on individual document + augmented corpus
    # We create slight variations to make TF-IDF meaningful
    corpus = [
        ' '.join(words),
        ' '.join(words[::2]),   # every other word
        ' '.join(words[1::2]),  # offset words
    ]
    
    vectorizer = TfidfVectorizer(ngram_range=(1, 2), max_features=100)
    try:
        tfidf_matrix = vectorizer.fit_transform(corpus)
    except Exception:
        return words[:top_n]
    
    feature_names = vectorizer.get_feature_names_out()
    scores = tfidf_matrix[0].toarray()[0]
    
    keyword_scores = sorted(
        zip(feature_names, scores),
        key=lambda x: x[1],
        reverse=True
    )
    
    return [
        {"keyword": kw, "importance_score": round(float(score), 4)}
        for kw, score in keyword_scores[:top_n]
        if score > 0
    ]


def compute_ats_score(resume_text: str, job_description: str) -> dict:
    """
    Simulate ATS (Applicant Tracking System) scoring.
    ATS systems primarily do keyword matching — this shows how a real ATS would score the resume.
    """
    resume_lower = resume_text.lower()
    jd_lower = job_description.lower()
    
    # Extract top keywords from JD
    jd_keywords = extract_keywords_tfidf(job_description, top_n=20)
    
    found_keywords = []
    missing_keywords = []
    
    for kw_data in jd_keywords:
        keyword = kw_data["keyword"]
        pattern = r'\b' + re.escape(keyword) + r'\b'
        
        if re.search(pattern, resume_lower):
            count = len(re.findall(pattern, resume_lower))
            found_keywords.append({
                "keyword": keyword,
                "importance": kw_data["importance_score"],
                "frequency_in_resume": count
            })
        else:
            missing_keywords.append({
                "keyword": keyword,
                "importance": kw_data["importance_score"]
            })
    
    # ATS score calculation
    if jd_keywords:
        total_importance = sum(k["importance_score"] for k in jd_keywords)
        found_importance = sum(k["importance"] for k in found_keywords)
        ats_score = (found_importance / total_importance * 100) if total_importance > 0 else 0
    else:
        ats_score = 0
    
    # Keyword density in resume
    total_words = len(resume_text.split())
    keyword_density = (len(found_keywords) / total_words * 100) if total_words > 0 else 0
    
    return {
        "ats_score": round(ats_score, 1),
        "keyword_density": round(keyword_density, 2),
        "found_keywords": found_keywords,
        "missing_keywords": missing_keywords[:10],
        "total_jd_keywords_checked": len(jd_keywords),
        "keywords_found": len(found_keywords),
        "ats_verdict": get_ats_verdict(ats_score)
    }


def get_ats_verdict(score: float) -> str:
    if score >= 70:
        return "ATS Friendly - High chance of passing automated screening"
    elif score >= 50:
        return "Moderate ATS Match - Some keywords missing"
    elif score >= 30:
        return "Low ATS Score - Add more job-specific keywords"
    else:
        return "Poor ATS Match - Resume needs significant keyword optimization"