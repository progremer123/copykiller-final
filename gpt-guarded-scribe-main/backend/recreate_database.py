#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
데이터베이스 재생성 스크립트
기존 데이터베이스를 삭제하고 새로운 스키마로 다시 생성합니다.
"""

import os
import sqlite3
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config import settings
from models import Base, User, UserSession, UserQuestion, PlagiarismCheck

def recreate_database():
    """데이터베이스를 완전히 재생성"""
    
    # 1. 기존 데이터베이스 파일 삭제 (이미 삭제됨)
    db_file = "plagiarism.db"
    if os.path.exists(db_file):
        os.remove(db_file)
        print(f"🗑️ 기존 데이터베이스 파일 '{db_file}' 삭제됨")
    
    # 2. 새로운 엔진 생성
    engine = create_engine(settings.DATABASE_URL, echo=True)
    
    # 3. 모든 테이블 생성
    print("📊 새로운 데이터베이스 스키마 생성 중...")
    Base.metadata.create_all(bind=engine)
    
    # 4. 테이블 생성 확인
    with sqlite3.connect(db_file) as conn:
        cursor = conn.cursor()
        
        # 생성된 테이블 목록 확인
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        print("\n✅ 생성된 테이블:")
        for table in tables:
            table_name = table[0]
            print(f"  - {table_name}")
            
            # 각 테이블의 컬럼 정보 확인
            cursor.execute(f"PRAGMA table_info({table_name});")
            columns = cursor.fetchall()
            
            for col in columns:
                col_id, col_name, col_type, not_null, default_val, pk = col
                pk_marker = " (PRIMARY KEY)" if pk else ""
                null_marker = " NOT NULL" if not_null else ""
                print(f"    └─ {col_name}: {col_type}{null_marker}{pk_marker}")
            print()
    
    # 5. 기본 데이터 삽입
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        # 테스트용 사용자 생성 (선택사항)
        print("👤 테스트 데이터 생성 중...")
        
        test_user = User(
            username="testuser",
            email="test@example.com",
            full_name="테스트 사용자"
        )
        test_user.set_password("testpassword123")
        
        db.add(test_user)
        db.commit()
        db.refresh(test_user)
        
        print(f"✅ 테스트 사용자 생성됨: {test_user.username} (ID: {test_user.id})")
        
    except Exception as e:
        print(f"⚠️ 테스트 데이터 생성 중 오류 (무시 가능): {e}")
        db.rollback()
    finally:
        db.close()
    
    print("\n🎉 데이터베이스 재생성 완료!")
    print("📍 이제 서버를 다시 시작할 수 있습니다: python main.py")

if __name__ == "__main__":
    recreate_database()