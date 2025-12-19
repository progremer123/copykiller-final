#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from services.web_crawler_service import WebCrawlerService
from database import get_db

def add_political_content():
    """정치/시사 관련 콘텐츠 추가"""
    
    crawler = WebCrawlerService()
    
    # 정치/시사 관련 키워드들
    political_keywords = [
        "대통령", "미국", "한미관계", "외교", "통상", 
        "정치", "정부", "협상", "트럼프", "한국정치",
        "국제관계", "무역협상", "동맹", "외교정책", "국정"
    ]
    
    print("🏛️ 정치/시사 관련 콘텐츠 크롤링 시작...")
    
    total_saved = 0
    for keyword in political_keywords:
        try:
            print(f"\n🔍 '{keyword}' 검색 중...")
            result = crawler.crawl_and_save(keyword, 3)  # 키워드당 3개 문서
            saved_count = result.get('saved_count', 0)
            total_saved += saved_count
            print(f"✅ '{keyword}': {saved_count}개 저장")
            
        except Exception as e:
            print(f"❌ '{keyword}' 크롤링 오류: {e}")
    
    print(f"\n🎉 총 {total_saved}개의 정치/시사 문서를 추가했습니다!")
    
    # 데이터베이스 상태 확인
    db = next(get_db())
    from models import DocumentSource
    
    total_docs = db.query(DocumentSource).filter(DocumentSource.is_active == True).count()
    print(f"📚 현재 총 활성 문서 수: {total_docs}개")

if __name__ == "__main__":
    add_political_content()