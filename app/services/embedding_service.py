from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

model = SentenceTransformer("all-MiniLM-L6-v2")


def get_embedding(text: str) -> np.ndarray:
    if not text or not text.strip():
        raise ValueError("Cannot embed empty text")
    return model.encode(text, normalize_embeddings=True)


def compute_similarity(text1: str, text2: str) -> float:
    emb1 = get_embedding(text1).reshape(1, -1)
    emb2 = get_embedding(text2).reshape(1, -1)
    return float(cosine_similarity(emb1, emb2)[0][0])


def compute_section_similarities(resume_sections: dict, job_description: str) -> dict:
    job_embedding = get_embedding(job_description).reshape(1, -1)
    results = {}
    for section_name, section_text in resume_sections.items():
        if section_text.strip():
            section_embedding = get_embedding(section_text).reshape(1, -1)
            sim = cosine_similarity(section_embedding, job_embedding)[0][0]
            results[section_name] = round(float(sim), 4)
    return results


def find_most_relevant_skills(skills: list, job_description: str, top_n: int = 10) -> list:
    if not skills:
        return []
    job_embedding = get_embedding(job_description).reshape(1, -1)
    skill_embeddings = model.encode(skills, normalize_embeddings=True)
    similarities = cosine_similarity(skill_embeddings, job_embedding).flatten()
    ranked = sorted(zip(skills, similarities), key=lambda x: x[1], reverse=True)
    return [{"skill": skill, "relevance_score": round(float(score), 4)} for skill, score in ranked[:top_n]]