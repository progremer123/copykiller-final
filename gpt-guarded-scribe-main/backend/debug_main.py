#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import traceback

try:
    print("🔍 서버 시작 디버깅...")
    
    # 1단계: 모듈 import 확인
    print("1️⃣ 모듈 import 중...")
    from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
    from fastapi.middleware.cors import CORSMiddleware
    from sqlalchemy.orm import Session
    import uvicorn
    from contextlib import asynccontextmanager
    print("   ✅ FastAPI 모듈들 import 성공")
    
    from database import get_db, create_tables
    from config import settings
    print("   ✅ 내부 모듈들 import 성공")
    
    # 2단계: lifespan 함수 정의
    print("2️⃣ lifespan 함수 정의 중...")
    @asynccontextmanager
    async def lifespan(app: FastAPI):
        # Startup
        print("   📚 데이터베이스 테이블 생성 중...")
        create_tables()
        print("   ✅ 데이터베이스 준비 완료")
        yield
        # Shutdown
        print("   🔄 서버 종료 중...")
    
    # 3단계: FastAPI 앱 생성
    print("3️⃣ FastAPI 앱 생성 중...")
    app = FastAPI(
        title="GPT 표절 검사기 API",
        description="AI 기반 표절 검사 시스템",
        version="1.0.0",
        lifespan=lifespan
    )
    print("   ✅ FastAPI 앱 생성 성공")
    
    # 4단계: CORS 설정
    print("4️⃣ CORS 미들웨어 설정 중...")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    print("   ✅ CORS 설정 완료")
    
    # 5단계: 라우터 import 및 등록
    print("5️⃣ 라우터 등록 중...")
    from routers import plagiarism
    app.include_router(plagiarism.router, prefix="/api", tags=["plagiarism"])
    print("   ✅ 라우터 등록 성공")
    
    # 6단계: 기본 엔드포인트 추가
    @app.get("/")
    async def root():
        return {"message": "GPT 표절 검사기 API", "version": "1.0.0"}

    @app.get("/health")
    async def health_check():
        return {"status": "healthy"}
    
    print("6️⃣ 기본 엔드포인트 등록 완료")
    
    # 7단계: 서버 시작
    print("7️⃣ 서버 시작 중...")
    print("🚀 FastAPI 서버 시작!")
    print("📡 접속 주소: http://127.0.0.1:8005")
    print("🔗 문서: http://127.0.0.1:8005/docs")
    
    uvicorn.run(app, host="127.0.0.1", port=8006)
    
except Exception as e:
    print(f"❌ 오류 발생: {e}")
    print("📋 전체 에러 스택:")
    traceback.print_exc()
    sys.exit(1)