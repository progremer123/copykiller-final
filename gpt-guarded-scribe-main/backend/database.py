from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config import settings
from models import Base

# 데이터베이스 연결: SQLite와 기타(DB) 분기 처리
db_url = settings.DATABASE_URL

if db_url.startswith("sqlite"):
    # SQLite 전용 옵션
    engine = create_engine(
        db_url,
        connect_args={"check_same_thread": False},
        echo=settings.DEBUG,
    )
else:
    # Postgres/MySQL 등 일반 DB
    engine = create_engine(
        db_url,
        echo=settings.DEBUG,
        pool_pre_ping=True,
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def create_tables():
    """데이터베이스 테이블 생성"""
    Base.metadata.create_all(bind=engine)

def get_db():
    """데이터베이스 세션 의존성"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()