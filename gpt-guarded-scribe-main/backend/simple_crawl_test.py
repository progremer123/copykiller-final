#!/usr/bin/env python3
"""간단한 웹 크롤링 테스트"""

import requests
from bs4 import BeautifulSoup
import sqlite3
from datetime import datetime

def simple_crawl_test():
    print("🌐 간단한 웹 크롤링 테스트")
    
    # 크롤링할 샘플 사이트들 (한국어 콘텐츠)
    urls = [
        "https://namu.wiki/w/%EC%9D%B8%EA%B3%B5%EC%A7%80%EB%8A%A5",
        "https://ko.wikipedia.org/wiki/%EA%B8%B0%EA%B3%84%ED%95%99%EC%8A%B5",
        "https://ko.wikipedia.org/wiki/%EA%B8%B0%ED%9B%84_%EB%B3%80%ED%99%94"
    ]
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    articles = []
    
    for i, url in enumerate(urls, 1):
        try:
            print(f"📄 크롤링 {i}/{len(urls)}: {url}")
            
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # 제목 추출
                title_elem = soup.find('title')
                title = title_elem.text if title_elem else f"제목없음_{i}"
                
                # 본문 추출 (p 태그들)
                paragraphs = soup.find_all('p')
                content_parts = []
                
                for p in paragraphs[:10]:  # 처음 10개 문단만
                    text = p.get_text().strip()
                    if len(text) > 20:  # 20자 이상만
                        content_parts.append(text)
                
                content = " ".join(content_parts)[:2000]  # 2000자로 제한
                
                if len(content) > 100:
                    articles.append({
                        'title': title[:200],
                        'content': content,
                        'url': url,
                        'source_type': 'crawled'
                    })
                    print(f"✅ 성공: {title[:50]}... ({len(content)}자)")
                else:
                    print(f"❌ 내용 부족: {len(content)}자")
            else:
                print(f"❌ HTTP 오류: {response.status_code}")
                
        except Exception as e:
            print(f"❌ 예외 발생: {e}")
    
    # 데이터베이스에 저장
    if articles:
        try:
            conn = sqlite3.connect("plagiarism.db")
            cursor = conn.cursor()
            
            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
            saved_count = 0
            
            for article in articles:
                # 중복 체크
                cursor.execute(
                    "SELECT id FROM document_sources WHERE url = ? AND is_active = 1",
                    (article['url'],)
                )
                
                if cursor.fetchone():
                    print(f"⚠️  이미 존재: {article['title'][:30]}...")
                    continue
                
                cursor.execute("""
                    INSERT INTO document_sources 
                    (title, content, url, source_type, created_at, updated_at, is_active)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    article['title'],
                    article['content'],
                    article['url'],
                    article['source_type'],
                    current_time,
                    current_time,
                    1
                ))
                saved_count += 1
                print(f"💾 저장: {article['title'][:30]}...")
            
            conn.commit()
            conn.close()
            
            print(f"\n🎉 완료: {len(articles)}개 크롤링, {saved_count}개 저장")
            
        except Exception as e:
            print(f"❌ DB 저장 오류: {e}")
    else:
        print("❌ 크롤링된 콘텐츠가 없습니다")

if __name__ == "__main__":
    simple_crawl_test()