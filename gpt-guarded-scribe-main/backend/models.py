from sqlalchemy import Column, Integer, String, Text, Float, DateTime, JSON, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import bcrypt

Base = declarative_base()

class PlagiarismCheck(Base):
    __tablename__ = "plagiarism_checks"
    
    id = Column(String, primary_key=True)
    original_text = Column(Text, nullable=False)
    similarity_score = Column(Float, default=0.0)
    status = Column(String, default="checking")  # checking, completed, error
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    file_name = Column(String, nullable=True)
    file_type = Column(String, nullable=True)
    processing_time = Column(Float, nullable=True)
    
    # Relationships
    matches = relationship("PlagiarismMatch", back_populates="check")

class PlagiarismMatch(Base):
    __tablename__ = "plagiarism_matches"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    check_id = Column(String, ForeignKey("plagiarism_checks.id"), nullable=False)
    matched_text = Column(Text, nullable=False)
    source_text = Column(Text, nullable=False)
    source_title = Column(String, nullable=False)
    source_url = Column(String, nullable=True)
    similarity_score = Column(Float, nullable=False)
    start_index = Column(Integer, nullable=False)
    end_index = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    check = relationship("PlagiarismCheck", back_populates="matches")

class DocumentSource(Base):
    __tablename__ = "document_sources"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    url = Column(String, nullable=True)
    source_type = Column(String, nullable=False)  # academic, web, book, etc.
    vector_embedding = Column(JSON, nullable=True)  # Store vector embeddings as JSON
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(100), nullable=True)
    is_premium = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)
    
    # Relationships
    questions = relationship("UserQuestion", back_populates="user")
    
    def set_password(self, password: str):
        """비밀번호 해시화"""
        salt = bcrypt.gensalt()
        self.password_hash = bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
    def check_password(self, password: str) -> bool:
        """비밀번호 확인"""
        return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))

class UserQuestion(Base):
    __tablename__ = "user_questions"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    question_text = Column(Text, nullable=False)
    question_type = Column(String(50), nullable=False)  # plagiarism_check, premium_analysis, general
    original_text = Column(Text, nullable=True)  # 원본 텍스트 (표절검사의 경우)
    similarity_score = Column(Float, nullable=True)
    match_count = Column(Integer, default=0)
    processing_time = Column(Float, nullable=True)
    status = Column(String(20), default="completed")  # pending, completed, failed
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="questions")

class UserSession(Base):
    __tablename__ = "user_sessions"
    
    id = Column(String, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    ip_address = Column(String, nullable=True)
    user_agent = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_activity = Column(DateTime, default=datetime.utcnow)
    check_count = Column(Integer, default=0)
    
    # Relationships
    user = relationship("User")