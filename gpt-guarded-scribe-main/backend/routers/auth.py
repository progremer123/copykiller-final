#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from database import get_db
from services.auth_service import AuthService
from pydantic import BaseModel, EmailStr
from typing import Optional, List
import re

router = APIRouter()
security = HTTPBearer()

# Pydantic 모델들
class UserRegister(BaseModel):
    username: str
    email: EmailStr
    password: str
    full_name: Optional[str] = None

class UserLogin(BaseModel):
    username_or_email: str
    password: str

class UserProfile(BaseModel):
    id: int
    username: str
    email: str
    full_name: Optional[str]
    is_premium: bool
    created_at: str
    last_login: Optional[str]

class QuestionSave(BaseModel):
    question_text: str
    question_type: str = "plagiarism_check"  # plagiarism_check, premium_analysis, general
    original_text: Optional[str] = None
    similarity_score: Optional[float] = None
    match_count: Optional[int] = 0
    processing_time: Optional[float] = None

# 의존성: 현재 사용자 가져오기
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    """현재 로그인한 사용자 가져오기"""
    auth_service = AuthService(db)
    user = auth_service.get_current_user(credentials.credentials)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="유효하지 않은 토큰입니다",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user

# 선택적 인증: 로그인하지 않아도 접근 가능
async def get_current_user_optional(request: Request, db: Session = Depends(get_db)):
    """선택적 현재 사용자 (토큰이 없어도 됨)"""
    auth_header = request.headers.get("Authorization")
    
    if not auth_header or not auth_header.startswith("Bearer "):
        return None
    
    try:
        token = auth_header.split(" ")[1]
        auth_service = AuthService(db)
        return auth_service.get_current_user(token)
    except:
        return None

@router.post("/register", summary="회원가입")
async def register(user_data: UserRegister, request: Request, db: Session = Depends(get_db)):
    """새 사용자 등록"""
    auth_service = AuthService(db)
    
    try:
        result = auth_service.register_user(
            username=user_data.username,
            email=user_data.email,
            password=user_data.password,
            full_name=user_data.full_name
        )
        
        # 세션 생성
        ip_address = request.client.host if request.client else None
        user_agent = request.headers.get("user-agent", "")
        session_id = auth_service.create_user_session(
            user_id=result["user"]["id"],
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        result["session_id"] = session_id
        return result
        
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"회원가입 처리 중 오류가 발생했습니다: {str(e)}"
        )

@router.post("/login", summary="로그인")
async def login(login_data: UserLogin, request: Request, db: Session = Depends(get_db)):
    """사용자 로그인"""
    auth_service = AuthService(db)
    
    try:
        result = auth_service.login(
            username_or_email=login_data.username_or_email,
            password=login_data.password
        )
        
        # 세션 생성
        ip_address = request.client.host if request.client else None
        user_agent = request.headers.get("user-agent", "")
        session_id = auth_service.create_user_session(
            user_id=result["user"]["id"],
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        result["session_id"] = session_id
        return result
        
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"로그인 처리 중 오류가 발생했습니다: {str(e)}"
        )

@router.get("/me", summary="내 프로필 조회")
async def get_profile(current_user = Depends(get_current_user)):
    """현재 로그인한 사용자의 프로필 정보"""
    return {
        "id": current_user.id,
        "username": current_user.username,
        "email": current_user.email,
        "full_name": current_user.full_name,
        "is_premium": current_user.is_premium,
        "created_at": current_user.created_at.isoformat(),
        "last_login": current_user.last_login.isoformat() if current_user.last_login else None
    }

@router.get("/questions", summary="내 질문 기록")
async def get_my_questions(
    limit: int = 50,
    offset: int = 0,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """로그인한 사용자의 질문 기록 조회"""
    auth_service = AuthService(db)
    return auth_service.get_user_questions(current_user.id, limit, offset)

@router.post("/questions", summary="질문 저장")
async def save_question(
    question_data: QuestionSave,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """사용자 질문을 기록에 저장"""
    auth_service = AuthService(db)
    
    question_dict = {
        "question_text": question_data.question_text,
        "question_type": question_data.question_type,
        "original_text": question_data.original_text,
        "similarity_score": question_data.similarity_score,
        "match_count": question_data.match_count,
        "processing_time": question_data.processing_time
    }
    
    return auth_service.save_user_question(current_user.id, question_dict)

@router.delete("/questions/{question_id}", summary="질문 삭제")
async def delete_question(
    question_id: int,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """사용자의 특정 질문 기록 삭제"""
    from models import UserQuestion
    
    question = db.query(UserQuestion).filter(
        UserQuestion.id == question_id,
        UserQuestion.user_id == current_user.id
    ).first()
    
    if not question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="질문을 찾을 수 없습니다"
        )
    
    db.delete(question)
    db.commit()
    
    return {"message": "질문이 삭제되었습니다"}

@router.post("/logout", summary="로그아웃")
async def logout():
    """로그아웃 (클라이언트에서 토큰 제거)"""
    return {"message": "로그아웃 되었습니다"}

@router.get("/check-username/{username}", summary="사용자명 중복 확인")
async def check_username(username: str, db: Session = Depends(get_db)):
    """사용자명 중복 확인"""
    from models import User
    
    if len(username) < 3:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="사용자명은 3자 이상이어야 합니다"
        )
    
    existing_user = db.query(User).filter(User.username == username).first()
    
    return {
        "available": existing_user is None,
        "message": "사용 가능한 사용자명입니다" if existing_user is None else "이미 사용중인 사용자명입니다"
    }

@router.get("/check-email/{email}", summary="이메일 중복 확인")
async def check_email(email: str, db: Session = Depends(get_db)):
    """이메일 중복 확인"""
    from models import User
    
    # 간단한 이메일 형식 확인
    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_regex, email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="유효하지 않은 이메일 형식입니다"
        )
    
    existing_user = db.query(User).filter(User.email == email).first()
    
    return {
        "available": existing_user is None,
        "message": "사용 가능한 이메일입니다" if existing_user is None else "이미 사용중인 이메일입니다"
    }