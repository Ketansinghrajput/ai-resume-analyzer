from .embedding_service import compute_similarity
from .skill_extractor import extract_skills


def rank_resumes(resumes: list, job_description: str) -> list:
    job_skills = extract_skills(job_description)
    job_skill_set = set(job_skills["all_skills"])
    job_experience = job_skills["experience"]

    ranked = []
    for resume in resumes:
        text = resume["text"]
        resume_skills = extract_skills(text)
        resume_skill_set = set(resume_skills["all_skills"])

        semantic_score = compute_similarity(text, job_description)

        matching = resume_skill_set & job_skill_set
        skill_score = len(matching) / max(len(job_skill_set), 1)

        exp_score = compute_experience_score(resume_skills["experience"], job_experience)

        final_score = (semantic_score * 0.50) + (skill_score * 0.35) + (exp_score * 0.15)

        ranked.append({
            "candidate": resume.get("name", "Unknown"),
            "final_score": round(final_score * 100, 1),
            "breakdown": {
                "semantic_match": round(semantic_score * 100, 1),
                "skill_match": round(skill_score * 100, 1),
                "experience_match": round(exp_score * 100, 1),
            },
            "matching_skills": sorted(list(matching)),
            "missing_skills": sorted(list(job_skill_set - resume_skill_set)),
        })

    ranked.sort(key=lambda x: x["final_score"], reverse=True)
    for i, r in enumerate(ranked):
        r["rank"] = i + 1

    return ranked


def compute_experience_score(resume_exp: dict, job_exp: dict) -> float:
    resume_years = resume_exp.get("max_years", 0)
    required_years = job_exp.get("min_years", 0)

    if required_years == 0:
        return 1.0
    if resume_years >= required_years:
        return 1.0
    elif resume_years >= required_years * 0.5:
        return 0.7
    elif resume_years > 0:
        return 0.4
    else:
        return 0.2