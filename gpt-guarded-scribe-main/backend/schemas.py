from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class PlagiarismCheckCreate(BaseModel):
    text: str
    file_name: Optional[str] = None
    file_type: Optional[str] = None

class PlagiarismMatchResponse(BaseModel):
    matched_text: str
    source_title: str
    source_url: Optional[str] = None
    similarity_score: float
    start_index: int
    end_index: int

class PlagiarismCheckResponse(BaseModel):
    id: str
    original_text: str
    similarity_score: float
    status: str
    created_at: datetime
    processing_time: Optional[float] = None
    matches: List[PlagiarismMatchResponse] = []

    class Config:
        from_attributes = True

class HealthResponse(BaseModel):
    status: str
    timestamp: datetime
    version: str

class ErrorResponse(BaseModel):
    error: str
    message: str
    status_code: int