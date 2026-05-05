from .skill_extractor import extract_skills
from .embedding_service import compute_similarity, find_most_relevant_skills
from .keyword_analyzer import compute_ats_score
from .skill_extractor import extract_skills, extract_entities

def analyze_gap(resume_text: str, job_description: str) -> dict:
    resume_skills = extract_skills(resume_text)
    job_skills = extract_skills(job_description)

    resume_skill_set = set(resume_skills["all_skills"])
    job_skill_set = set(job_skills["all_skills"])

    matching_skills = resume_skill_set & job_skill_set
    missing_skills = job_skill_set - resume_skill_set
    extra_skills = resume_skill_set - job_skill_set

    overall_similarity = compute_similarity(resume_text, job_description)

    missing_skill_priority = find_most_relevant_skills(list(missing_skills), job_description)

    if len(job_skill_set) > 0:
        skill_match_percent = len(matching_skills) / len(job_skill_set) * 100
    else:
        skill_match_percent = 0

    recommendations = generate_recommendations(missing_skill_priority, overall_similarity, skill_match_percent)

    return {
        "overall_match": {
            "semantic_similarity": round(overall_similarity, 4),
            "skill_match_percentage": round(skill_match_percent, 1),
            "verdict": get_verdict(overall_similarity, skill_match_percent),
        },
        "matching_skills": sorted(list(matching_skills)),
        "missing_skills": missing_skill_priority,
        "extra_skills": sorted(list(extra_skills)),
        "resume_analysis": resume_skills,
        "ats_analysis": compute_ats_score(resume_text, job_description),
"resume_entities": extract_entities(resume_text),
        "job_analysis": job_skills,
        "recommendations": recommendations,
    }

def get_verdict(similarity: float, skill_match: float) -> str:
    combined = (similarity * 50) + (skill_match * 0.5)
    if combined > 70:
        return "Strong Match - You are well-qualified for this role"
    elif combined > 50:
        return "Good Match - A few skill gaps to address"
    elif combined > 30:
        return "Partial Match - Significant upskilling needed"
    else:
        return "Weak Match - This role requires substantially different skills"


def generate_recommendations(missing_skills: list, similarity: float, match_pct: float) -> list:
    recs = []
    if match_pct >= 80:
        recs.append("Your skills are a strong match. Focus on showcasing project experience.")
    elif match_pct >= 50:
        recs.append("Good foundation. Focus on the top 3 missing skills to strengthen your profile.")
    else:
        recs.append("Consider gaining hands-on experience with the core missing skills before applying.")

    for i, skill_info in enumerate(missing_skills[:3]):
        skill = skill_info["skill"]
        recs.append(f"Priority {i+1}: Learn '{skill}' - build a small project or take a focused course.")

    if similarity < 0.4:
        recs.append("Your resume language does not align well with this job. Tailor your resume using keywords from the job description.")

    return recs