#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
from bs4 import BeautifulSoup
import time

def demonstrate_crawling():
    """나무위키와 위키백과 크롤링 과정 실제 시연"""
    
    print("🌐 나무위키와 위키백과 크롤링 과정 시연")
    print("=" * 60)
    
    # 크롤링할 URL들
    urls = {
        "위키백과": "https://ko.wikipedia.org/wiki/%EC%9D%B8%EA%B3%B5%EC%A7%80%EB%8A%A5",
        "나무위키": "https://namu.wiki/w/%EC%9D%B8%EA%B3%B5%EC%A7%80%EB%8A%A5"
    }
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    for site_name, url in urls.items():
        print(f"\n📄 {site_name} 크롤링 중...")
        print(f"URL: {url}")
        
        try:
            # 1단계: HTTP 요청
            print("1️⃣ HTTP 요청 중...")
            response = requests.get(url, headers=headers, timeout=10)
            print(f"   응답 코드: {response.status_code}")
            print(f"   응답 크기: {len(response.text):,} 문자")
            
            # 2단계: HTML 파싱
            print("2️⃣ HTML 파싱 중...")
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 3단계: 제목 추출
            print("3️⃣ 제목 추출...")
            title_element = soup.find('title')
            if title_element:
                title = title_element.get_text().strip()
                print(f"   제목: {title[:60]}...")
            
            # 4단계: 본문 추출
            print("4️⃣ 본문 추출...")
            
            # 불필요한 요소 제거
            for element in soup(['script', 'style', 'nav', 'footer', 'header', 'aside']):
                element.decompose()
            
            # 본문 추출 시도
            content = ""
            if site_name == "위키백과":
                # 위키백과 특화 추출
                content_div = soup.find('div', {'class': 'mw-parser-output'})
                if content_div:
                    paragraphs = content_div.find_all('p')
                    content = ' '.join([p.get_text() for p in paragraphs[:5]])  # 첫 5개 문단
            
            elif site_name == "나무위키":
                # 나무위키 특화 추출
                paragraphs = soup.find_all('p')
                if paragraphs:
                    content = ' '.join([p.get_text() for p in paragraphs[:3]])  # 첫 3개 문단
            
            if not content:
                # 폴백: 모든 p 태그
                paragraphs = soup.find_all('p')
                content = ' '.join([p.get_text() for p in paragraphs[:3]])
            
            # 5단계: 텍스트 정제
            print("5️⃣ 텍스트 정제...")
            import re
            content = re.sub(r'\s+', ' ', content)  # 공백 정리
            content = content.strip()[:500]  # 길이 제한
            
            print(f"   추출된 내용 ({len(content)}자): {content}...")
            
            # 6단계: 키워드 분석
            print("6️⃣ 키워드 분석...")
            words = content.split()
            korean_words = [word for word in words if any('\uAC00' <= char <= '\uD7A3' for char in word)]
            print(f"   한글 키워드 샘플: {korean_words[:10]}")
            
        except Exception as e:
            print(f"❌ {site_name} 크롤링 실패: {e}")
        
        print("-" * 60)
        time.sleep(1)  # 서버 부하 방지
    
    print("\n✅ 크롤링 과정 완료!")

if __name__ == "__main__":
    demonstrate_crawling()