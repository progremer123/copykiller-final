#!/usr/bin/env python3
"""
데이터베이스 초기 데이터 준비 스크립트
나무위키, 위키백과에서 주요 주제들의 데이터를 미리 수집합니다.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import get_db, engine
from models import Base
from services.web_crawler_service import WebCrawlerService
import time

# 데이터베이스 테이블 생성
Base.metadata.create_all(bind=engine)

def prepare_initial_data():
    """초기 데이터 준비"""
    print("🚀 CopyKiller 초기 데이터 준비 시작...")
    
    db = next(get_db())
    crawler = WebCrawlerService()
    
    # 주요 주제 키워드들
    topics = [
        # 기술 관련
        "인공지능", "머신러닝", "딥러닝", "자연어처리", "컴퓨터비전",
        "빅데이터", "클라우드", "사물인터넷", "블록체인", "사이버보안",
        
        # 학술 관련  
        "연구방법론", "통계학", "데이터분석", "논문작성", "학술윤리",
        "문헌고찰", "실험설계", "가설검정", "표본조사", "질적연구",
        
        # 일반 지식
        "경제학", "심리학", "사회학", "철학", "역사학",
        "물리학", "화학", "생물학", "수학", "지리학",
        
        # 현대 이슈
        "지속가능발전", "기후변화", "디지털전환", "원격근무", "온라인교육",
        "전자상거래", "핀테크", "스마트시티", "바이오기술", "신재생에너지"
    ]
    
    total_saved = 0
    
    for i, topic in enumerate(topics, 1):
        try:
            print(f"\n📚 [{i}/{len(topics)}] '{topic}' 데이터 수집 중...")
            
            result = crawler.crawl_and_save(topic, 2)  # 주제당 2개 문서
            saved_count = result.get('saved_count', 0)
            total_saved += saved_count
            
            print(f"✅ '{topic}' 완료: {saved_count}개 저장")
            
            # 서버 부하 방지를 위한 대기 (1.5초)
            time.sleep(1.5)
            
        except Exception as e:
            print(f"❌ '{topic}' 오류: {e}")
            continue
    
    print(f"\n🎉 초기 데이터 준비 완료!")
    print(f"📊 총 {total_saved}개 문서 수집됨")
    print(f"💡 이제 CopyKiller가 풍부한 데이터로 정확한 표절 검사를 제공합니다!")

if __name__ == "__main__":
    prepare_initial_data()