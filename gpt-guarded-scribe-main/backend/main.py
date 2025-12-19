from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import uvicorn
from contextlib import asynccontextmanager

from database import get_db, create_tables
from config import settings

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    create_tables()
    yield
    # Shutdown

app = FastAPI(
    title="GPT 표절 검사기 API",
    description="AI 기반 표절 검사 시스템",
    version="1.0.0",
    lifespan=lifespan
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 라우터 등록
from routers import plagiarism
from routers import advanced_features
from routers import auth

# 라우터 추가
app.include_router(plagiarism.router, prefix="/api", tags=["plagiarism"])
app.include_router(advanced_features.router, prefix="/api/premium", tags=["premium"])
app.include_router(auth.router, prefix="/api/auth", tags=["authentication"])

@app.get("/")
async def root():
    return {"message": "GPT 표절 검사기 API", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    print("[*] FastAPI 서버 시작 중...")
    uvicorn.run(app, host="127.0.0.1", port=8006)