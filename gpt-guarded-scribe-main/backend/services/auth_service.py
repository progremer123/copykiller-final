#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from datetime import datetime, timedelta
from typing import Optional, Dict
import jwt
import secrets
from sqlalchemy.orm import Session
from models import User, UserSession
from fastapi import HTTPException, status
import re

class AuthService:
    """인증 서비스"""
    
    SECRET_KEY = "your-secret-key-here-change-in-production"
    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = 30 * 24 * 60  # 30일
    
    def __init__(self, db: Session):
        self.db = db
    
    def register_user(self, username: str, email: str, password: str, full_name: str = None) -> Dict:
        """사용자 등록"""
        
        # 입력값 검증
        if not self._validate_email(email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="유효하지 않은 이메일 형식입니다"
            )
        
        if not self._validate_password(password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="비밀번호는 8자 이상이어야 하며, 영문, 숫자를 포함해야 합니다"
            )
        
        if len(username) < 3:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="사용자명은 3자 이상이어야 합니다"
            )
        
        # 중복 확인
        existing_user = self.db.query(User).filter(
            (User.username == username) | (User.email == email)
        ).first()
        
        if existing_user:
            if existing_user.username == username:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="이미 사용중인 사용자명입니다"
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="이미 사용중인 이메일입니다"
                )
        
        # 새 사용자 생성
        new_user = User(
            username=username,
            email=email,
            full_name=full_name
        )
        new_user.set_password(password)
        
        self.db.add(new_user)
        self.db.commit()
        self.db.refresh(new_user)
        
        return {
            "message": "회원가입이 완료되었습니다",
            "user": {
                "id": new_user.id,
                "username": new_user.username,
                "email": new_user.email,
                "full_name": new_user.full_name,
                "is_premium": new_user.is_premium
            }
        }
    
    def login(self, username_or_email: str, password: str) -> Dict:
        """로그인"""
        
        # 사용자 찾기 (username 또는 email로)
        user = self.db.query(User).filter(
            (User.username == username_or_email) | (User.email == username_or_email)
        ).first()
        
        if not user or not user.check_password(password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="잘못된 사용자명/이메일 또는 비밀번호입니다"
            )
        
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="비활성화된 계정입니다"
            )
        
        # 마지막 로그인 시간 업데이트
        user.last_login = datetime.utcnow()
        self.db.commit()
        
        # JWT 토큰 생성
        token = self._create_access_token({"sub": str(user.id)})
        
        return {
            "access_token": token,
            "token_type": "bearer",
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "full_name": user.full_name,
                "is_premium": user.is_premium
            }
        }
    
    def get_current_user(self, token: str) -> Optional[User]:
        """현재 사용자 가져오기"""
        try:
            payload = jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            user_id: str = payload.get("sub")
            if user_id is None:
                return None
        except jwt.PyJWTError:
            return None
        
        user = self.db.query(User).filter(User.id == int(user_id)).first()
        return user
    
    def create_user_session(self, user_id: Optional[int], ip_address: str = None, user_agent: str = None) -> str:
        """사용자 세션 생성"""
        session_id = secrets.token_urlsafe(32)
        
        session = UserSession(
            id=session_id,
            user_id=user_id,
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        self.db.add(session)
        self.db.commit()
        
        return session_id
    
    def get_user_questions(self, user_id: int, limit: int = 50, offset: int = 0) -> Dict:
        """사용자 질문 기록 조회"""
        from models import UserQuestion
        
        # 총 개수 조회
        total_count = self.db.query(UserQuestion).filter(UserQuestion.user_id == user_id).count()
        
        # 질문 목록 조회
        questions = (
            self.db.query(UserQuestion)
            .filter(UserQuestion.user_id == user_id)
            .order_by(UserQuestion.created_at.desc())
            .offset(offset)
            .limit(limit)
            .all()
        )
        
        question_list = []
        for q in questions:
            question_list.append({
                "id": q.id,
                "question_text": q.question_text,
                "question_type": q.question_type,
                "similarity_score": q.similarity_score,
                "match_count": q.match_count,
                "processing_time": q.processing_time,
                "status": q.status,
                "created_at": q.created_at.isoformat()
            })
        
        return {
            "total_count": total_count,
            "questions": question_list,
            "has_more": (offset + limit) < total_count
        }
    
    def save_user_question(self, user_id: int, question_data: Dict) -> Dict:
        """사용자 질문 저장"""
        from models import UserQuestion
        
        question = UserQuestion(
            user_id=user_id,
            question_text=question_data.get("question_text", ""),
            question_type=question_data.get("question_type", "general"),
            original_text=question_data.get("original_text"),
            similarity_score=question_data.get("similarity_score"),
            match_count=question_data.get("match_count", 0),
            processing_time=question_data.get("processing_time"),
            status=question_data.get("status", "completed")
        )
        
        self.db.add(question)
        self.db.commit()
        self.db.refresh(question)
        
        return {
            "id": question.id,
            "message": "질문이 저장되었습니다",
            "created_at": question.created_at.isoformat()
        }
    
    def _create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None):
        """JWT 액세스 토큰 생성"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=self.ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)
        return encoded_jwt
    
    def _validate_email(self, email: str) -> bool:
        """이메일 형식 검증"""
        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(email_regex, email) is not None
    
    def _validate_password(self, password: str) -> bool:
        """비밀번호 강도 검증"""
        if len(password) < 8:
            return False
        
        # 영문자 포함 확인
        if not re.search(r'[a-zA-Z]', password):
            return False
        
        # 숫자 포함 확인
        if not re.search(r'[0-9]', password):
            return False
        
        return True

# 사용 예시
if __name__ == "__main__":
    print("🔐 인증 서비스 모듈")
    print("기능:")
    print("- 회원가입 (이메일/비밀번호 검증)")
    print("- 로그인 (JWT 토큰)")
    print("- 사용자 세션 관리")
    print("- 질문 기록 저장/조회")