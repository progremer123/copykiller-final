#!/usr/bin/env python3
"""
테스트용 데이터베이스 설정 스크립트
표절 검사를 위한 샘플 문서들을 데이터베이스에 추가합니다.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config import settings
from models import Base, DocumentSource
import datetime

def setup_test_data():
    """테스트용 문서 소스들을 데이터베이스에 추가"""
    
    # 데이터베이스 연결
    engine = create_engine(
        settings.DATABASE_URL,
        connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {},
        echo=True
    )
    
    # 테이블 생성
    Base.metadata.create_all(bind=engine)
    
    # 세션 생성
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        # 기존 테스트 데이터 삭제
        db.query(DocumentSource).filter(DocumentSource.source_type == "test").delete()
        db.commit()
        
        # 테스트 문서들 추가
        test_documents = [
            {
                "title": "인공지능의 발전과 미래",
                "content": """인공지능은 현대 사회에서 중요한 역할을 하고 있습니다. 
                머신러닝 기술의 발전으로 많은 분야에서 혁신이 일어나고 있으며, 
                특히 자연어 처리와 컴퓨터 비전 분야에서 놀라운 성과를 보이고 있습니다. 
                딥러닝 알고리즘의 발전으로 이미지 인식, 음성 인식, 번역 등의 
                성능이 크게 향상되었습니다.""",
                "url": "https://example.com/ai-development",
                "source_type": "test"
            },
            {
                "title": "기계학습의 원리",
                "content": """기계학습은 데이터를 통해 학습하는 알고리즘입니다. 
                지도학습, 비지도학습, 강화학습 등 다양한 방법이 있으며, 
                각각의 특징과 활용 분야가 다릅니다. 신경망과 딥러닝은 
                기계학습의 한 분야로서 복잡한 패턴을 학습할 수 있습니다.""",
                "url": "https://example.com/machine-learning",
                "source_type": "test"
            },
            {
                "title": "데이터 과학과 분석",
                "content": """데이터 과학은 데이터에서 인사이트를 추출하는 학문입니다. 
                통계학, 수학, 컴퓨터 과학이 결합된 분야로서 
                빅데이터 시대에 매우 중요한 역할을 합니다. 
                데이터 마이닝, 시각화, 예측 모델링 등이 주요 기술입니다.""",
                "url": "https://example.com/data-science",
                "source_type": "test"
            },
            {
                "title": "프로그래밍 언어의 종류",
                "content": """프로그래밍 언어는 컴퓨터와 소통하기 위한 도구입니다. 
                Python은 간단하고 읽기 쉬운 문법으로 인해 초보자들에게 인기가 많습니다. 
                JavaScript는 웹 개발에서 필수적인 언어이며, 
                Java는 기업용 애플리케이션 개발에 널리 사용됩니다.""",
                "url": "https://example.com/programming-languages",
                "source_type": "test"
            },
            {
                "title": "웹 개발의 기초",
                "content": """웹 개발은 프론트엔드와 백엔드로 나뉩니다. 
                프론트엔드는 사용자가 직접 보고 상호작용하는 부분이며, 
                HTML, CSS, JavaScript를 주로 사용합니다. 
                백엔드는 서버 로직과 데이터베이스 관리를 담당합니다.""",
                "url": "https://example.com/web-development",
                "source_type": "test"
            }
        ]
        
        # 문서들을 데이터베이스에 추가
        for doc_data in test_documents:
            document = DocumentSource(**doc_data)
            db.add(document)
        
        db.commit()
        
        count = db.query(DocumentSource).filter(DocumentSource.source_type == "test").count()
        print(f"✅ {count}개의 테스트 문서가 데이터베이스에 추가되었습니다.")
        
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    setup_test_data()