import os
from typing import List

class Settings:
    # 데이터베이스 설정 (개발용 SQLite)
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", 
        "sqlite:///./plagiarism.db"
    )
    
    # Redis 설정 (캐싱용)
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379")
    
    # API 설정
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "GPT 표절 검사기 API"
    VERSION: str = "1.0.0"
    
    # CORS 설정
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:3001",
        "http://localhost:5173",
        "http://localhost:8080",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:8080",
    ]
    
    # 보안 설정
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # 파일 업로드 설정
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_FILE_TYPES: List[str] = [
        "text/plain",
        "application/pdf",
        "application/msword",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    ]
    
    # 텍스트 처리 설정
    MIN_TEXT_LENGTH: int = 10
    MAX_TEXT_LENGTH: int = 100000  # 100KB
    
    # 유사도 임계값
    SIMILARITY_THRESHOLD: float = 0.3
    HIGH_SIMILARITY_THRESHOLD: float = 0.7
    
    # 백그라운드 작업 설정 (개발용 메모리 브로커)
    CELERY_BROKER_URL: str = os.getenv("CELERY_BROKER_URL", "memory://")
    CELERY_RESULT_BACKEND: str = os.getenv("CELERY_RESULT_BACKEND", "cache+memory://")
    
    # 로깅 설정
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    
    # OpenAI API (의미적 유사도 계산용)
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    
    # 기타 설정
    TIMEZONE: str = "Asia/Seoul"

settings = Settings()