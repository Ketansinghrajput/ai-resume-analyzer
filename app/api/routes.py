from fastapi import APIRouter, UploadFile, File, HTTPException
from .schemas import AnalyzeRequest, SkillExtractRequest, RankRequest
from ..services.skill_extractor import extract_skills, ALL_SKILLS
from ..services.gap_analyzer import analyze_gap
from ..services.resume_ranker import rank_resumes
from ..services.pdf_parser import extract_text_from_pdf
from ..services.embedding_service import compute_similarity

router = APIRouter(prefix="/api", tags=["Resume Analysis"])


@router.post("/analyze")
async def analyze_resume_vs_job(request: AnalyzeRequest):
    result = analyze_gap(request.resume_text, request.job_description)
    return {"success": True, "data": result}


@router.post("/analyze-pdf")
async def analyze_pdf_resume(
    file: UploadFile = File(...),
    job_description: str = "",
):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")
    if file.size > 5 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File too large. Max 5MB.")

    pdf_bytes = await file.read()
    try:
        resume_text = extract_text_from_pdf(pdf_bytes)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))

    if not job_description:
        skills = extract_skills(resume_text)
        return {"success": True, "data": {"extracted_text_length": len(resume_text), "skills": skills}}

    result = analyze_gap(resume_text, job_description)
    return {"success": True, "data": result}


@router.post("/extract-skills")
async def extract_skills_endpoint(request: SkillExtractRequest):
    result = extract_skills(request.text)
    return {"success": True, "data": result}


@router.post("/rank-resumes")
async def rank_resumes_endpoint(request: RankRequest):
    if not all("text" in r for r in request.resumes):
        raise HTTPException(status_code=400, detail="Each resume must have a 'text' field")
    rankings = rank_resumes(request.resumes, request.job_description)
    return {"success": True, "data": {"rankings": rankings, "total_candidates": len(rankings)}}


@router.post("/similarity")
async def compute_text_similarity(text1: str, text2: str):
    score = compute_similarity(text1, text2)
    return {"similarity": round(score, 4), "interpretation": interpret_score(score)}


@router.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "model": "all-MiniLM-L6-v2",
        "embedding_dimensions": 384,
        "skills_in_database": len(ALL_SKILLS),
    }


def interpret_score(score: float) -> str:
    if score > 0.8:
        return "Very similar"
    elif score > 0.6:
        return "Related"
    elif score > 0.4:
        return "Somewhat related"
    else:
        return "Not related"