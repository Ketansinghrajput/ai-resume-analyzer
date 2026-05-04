import json
import re
from pathlib import Path
import spacy

nlp = spacy.load("en_core_web_sm")

SKILLS_PATH = Path(__file__).parent.parent / "data" / "tech_skills.json"
with open(SKILLS_PATH, "r") as f:
    SKILL_DATABASE = json.load(f)

ALL_SKILLS = set()
SKILL_CATEGORIES = {}
for category, skills in SKILL_DATABASE.items():
    for skill in skills:
        ALL_SKILLS.add(skill.lower())
        SKILL_CATEGORIES[skill.lower()] = category


def extract_skills(text: str) -> dict:
    if not text or not text.strip():
        return {"skills_by_category": {}, "all_skills": [], "skill_count": 0, "skill_frequency": {}, "experience": {"mentions": [], "min_years": 0, "max_years": 0}}

    text_lower = text.lower()
    found_skills = {}

    for skill in ALL_SKILLS:
        pattern = r'\b' + re.escape(skill) + r'\b'
        if re.search(pattern, text_lower):
            category = SKILL_CATEGORIES[skill]
            if category not in found_skills:
                found_skills[category] = []
            if skill not in found_skills[category]:
                found_skills[category].append(skill)

    skill_frequency = {}
    for category, skills in found_skills.items():
        for skill in skills:
            pattern = r'\b' + re.escape(skill) + r'\b'
            count = len(re.findall(pattern, text_lower))
            skill_frequency[skill] = count

    experience = extract_experience(text)

    return {
        "skills_by_category": found_skills,
        "all_skills": [s for skills in found_skills.values() for s in skills],
        "skill_count": sum(len(s) for s in found_skills.values()),
        "skill_frequency": skill_frequency,
        "experience": experience,
    }


def extract_experience(text: str) -> dict:
    patterns = [
        r'(\d+)\+?\s*(?:years?|yrs?)\s*(?:of)?\s*experience',
        r'experience\s*(?:of)?\s*(\d+)\+?\s*(?:years?|yrs?)',
        r'(\d+)\+?\s*(?:years?|yrs?)\s*(?:in|with|of)',
    ]
    mentions = []
    for pattern in patterns:
        matches = re.finditer(pattern, text.lower())
        for match in matches:
            years = int(match.group(1))
            mentions.append({"years": years, "context": match.group(0)})

    return {
        "mentions": mentions,
        "min_years": min((m["years"] for m in mentions), default=0),
        "max_years": max((m["years"] for m in mentions), default=0),
    }