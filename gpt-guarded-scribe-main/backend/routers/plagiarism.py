from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, UploadFile, File
from sqlalchemy.orm import Session
from typing import List, Optional
import uuid
from datetime import datetime

from database import get_db
from services.plagiarism_service import PlagiarismService
from services.text_processor import TextProcessor
from schemas import PlagiarismCheckCreate, PlagiarismCheckResponse, PlagiarismMatchResponse

router = APIRouter()

@router.post("/check/text", response_model=PlagiarismCheckResponse)
async def check_text_plagiarism(
    background_tasks: BackgroundTasks,
    text: str,
    db: Session = Depends(get_db)
):
    """텍스트 표절 검사"""
    if not text or len(text.strip()) < 10:
        raise HTTPException(status_code=400, detail="텍스트가 너무 짧습니다 (최소 10자)")
    
    # 새로운 검사 생성
    check_id = str(uuid.uuid4())
    service = PlagiarismService(db)
    
    # 검사 레코드 생성
    check = service.create_check(check_id, text)
    
    # 백그라운드에서 표절 검사 실행
    background_tasks.add_task(service.process_plagiarism_check, check_id, text)
    
    return PlagiarismCheckResponse(
        id=check.id,
        original_text=check.original_text,
        similarity_score=check.similarity_score,
        status=check.status,
        created_at=check.created_at,
        matches=[]
    )

@router.post("/check/file", response_model=PlagiarismCheckResponse)
async def check_file_plagiarism(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """파일 표절 검사"""
    # 파일 타입 검증
    allowed_types = ["text/plain", "application/pdf", "application/msword", 
                    "application/vnd.openxmlformats-officedocument.wordprocessingml.document"]
    
    if file.content_type not in allowed_types:
        raise HTTPException(status_code=400, detail="지원하지 않는 파일 타입입니다")
    
    # 파일 크기 검증 (10MB)
    content = await file.read()
    if len(content) > 10 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="파일 크기가 너무 큽니다 (최대 10MB)")
    
    # 텍스트 추출
    processor = TextProcessor()
    text = processor.extract_text_from_file(content, file.content_type)
    
    if not text or len(text.strip()) < 10:
        raise HTTPException(status_code=400, detail="파일에서 텍스트를 추출할 수 없습니다")
    
    # 새로운 검사 생성
    check_id = str(uuid.uuid4())
    service = PlagiarismService(db)
    
    # 검사 레코드 생성
    check = service.create_check(
        check_id, 
        text, 
        file_name=file.filename,
        file_type=file.content_type
    )
    
    # 백그라운드에서 표절 검사 실행
    background_tasks.add_task(service.process_plagiarism_check, check_id, text)
    
    return PlagiarismCheckResponse(
        id=check.id,
        original_text=check.original_text[:500] + "..." if len(check.original_text) > 500 else check.original_text,
        similarity_score=check.similarity_score,
        status=check.status,
        created_at=check.created_at,
        matches=[]
    )

@router.get("/check/{check_id}", response_model=PlagiarismCheckResponse)
async def get_plagiarism_result(check_id: str, db: Session = Depends(get_db)):
    """표절 검사 결과 조회"""
    service = PlagiarismService(db)
    check = service.get_check_result(check_id)
    
    if not check:
        raise HTTPException(status_code=404, detail="검사 결과를 찾을 수 없습니다")
    
    matches = [
        PlagiarismMatchResponse(
            matched_text=match.matched_text,
            source_title=match.source_title,
            source_url=match.source_url,
            similarity_score=match.similarity_score,
            start_index=match.start_index,
            end_index=match.end_index
        )
        for match in check.matches
    ]
    
    return PlagiarismCheckResponse(
        id=check.id,
        original_text=check.original_text,
        similarity_score=check.similarity_score,
        status=check.status,
        created_at=check.created_at,
        processing_time=check.processing_time,
        matches=matches
    )

@router.get("/history", response_model=List[PlagiarismCheckResponse])
async def get_check_history(
    limit: int = 10,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    """검사 이력 조회"""
    service = PlagiarismService(db)
    checks = service.get_check_history(limit, offset)
    
    return [
        PlagiarismCheckResponse(
            id=check.id,
            original_text=check.original_text[:200] + "..." if len(check.original_text) > 200 else check.original_text,
            similarity_score=check.similarity_score,
            status=check.status,
            created_at=check.created_at,
            processing_time=check.processing_time,
            matches=[]
        )
        for check in checks
    ]

@router.delete("/check/{check_id}")
async def delete_check(check_id: str, db: Session = Depends(get_db)):
    """검사 결과 삭제"""
    service = PlagiarismService(db)
    success = service.delete_check(check_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="검사 결과를 찾을 수 없습니다")
    
    return {"message": "검사 결과가 삭제되었습니다"}