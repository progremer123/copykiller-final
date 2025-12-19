#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from database import get_db
from models import DocumentSource

def show_wiki_sources():
    """나무위키와 위키백과 소스 확인"""
    
    db = next(get_db())
    
    # 위키 관련 문서만 조회
    sources = db.query(DocumentSource).filter(
        DocumentSource.is_active == True
    ).all()
    
    wiki_sources = [s for s in sources if 'wiki' in s.url.lower()]
    
    print(f"🔍 위키 관련 문서 {len(wiki_sources)}개 발견:")
    print("=" * 80)
    
    for i, source in enumerate(wiki_sources, 1):
        print(f"\n📄 문서 {i}:")
        print(f"   제목: {source.title}")
        print(f"   URL: {source.url}")
        print(f"   소스 타입: {source.source_type}")
        print(f"   생성일: {source.created_at}")
        print(f"   내용 길이: {len(source.content)}자")
        
        # 내용 미리보기 (처음 300자)
        preview = source.content[:300].replace('\n', ' ').replace('\r', ' ')
        print(f"   내용 미리보기: {preview}...")
        print("-" * 80)
    
    # 전체 데이터베이스 상태
    total_sources = len(sources)
    print(f"\n📊 전체 데이터베이스 현황:")
    print(f"   - 총 활성 문서: {total_sources}개")
    print(f"   - 위키 문서: {len(wiki_sources)}개")
    print(f"   - 기타 문서: {total_sources - len(wiki_sources)}개")

if __name__ == "__main__":
    show_wiki_sources()