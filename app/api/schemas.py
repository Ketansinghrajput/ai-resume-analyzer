from pydantic import BaseModel, Field


class AnalyzeRequest(BaseModel):
    resume_text: str = Field(..., min_length=50, description="Full resume text")
    job_description: str = Field(..., min_length=30, description="Job description text")


class SkillExtractRequest(BaseModel):
    text: str = Field(..., min_length=10)


class RankRequest(BaseModel):
    resumes: list = Field(..., min_length=1, max_length=50)
    job_description: str = Field(..., min_length=30)


class HealthResponse(BaseModel):
    status: str
    model_loaded: bool
    skills_database_size: int