#!/usr/bin/env python3
"""
직접 표절 검사 테스트 스크립트
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from services.plagiarism_service import PlagiarismService
from models import Base, DocumentSource
import uuid

# 데이터베이스 연결
DATABASE_URL = "sqlite:///./plagiarism.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def test_plagiarism_check():
    """표절 검사 직접 테스트"""
    
    # 테이블 생성
    Base.metadata.create_all(bind=engine)
    
    # 데이터베이스 세션
    db = SessionLocal()
    
    try:
        # 테스트 텍스트
        test_text = "인공지능은 현대 사회에서 중요한 역할을 하고 있습니다. 머신러닝 기술의 발전으로 혁신이 일어나고 있습니다."
        
        print("🔍 직접 표절 검사 테스트 시작")
        print(f"📄 테스트 텍스트: {test_text}")
        
        # 문서 수 확인
        doc_count = db.query(DocumentSource).filter(DocumentSource.is_active == True).count()
        print(f"📚 데이터베이스 문서 수: {doc_count}개")
        
        if doc_count == 0:
            print("❌ 데이터베이스에 문서가 없습니다!")
            return
        
        # 서비스 생성 및 검사 실행
        service = PlagiarismService(db)
        check_id = str(uuid.uuid4())
        
        # 검사 생성
        check = service.create_check(check_id, test_text)
        print(f"✅ 검사 생성 완료: {check_id}")
        
        # 검사 실행
        service.process_plagiarism_check(check_id, test_text)
        
        # 결과 조회
        result = service.get_check_result(check_id)
        if result:
            print(f"📊 최종 결과:")
            print(f"   - 유사도: {result.similarity_score:.1f}%")
            print(f"   - 상태: {result.status}")
            print(f"   - 매치 수: {len(result.matches)}")
            
            for i, match in enumerate(result.matches):
                print(f"   - 매치 {i+1}: '{match.source_title}' (유사도: {match.similarity_score:.1f}%)")
        else:
            print("❌ 결과를 찾을 수 없습니다!")
            
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    test_plagiarism_check()