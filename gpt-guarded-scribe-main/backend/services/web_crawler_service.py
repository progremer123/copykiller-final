#!/usr/bin/env python3
"""웹 크롤링 서비스"""

import requests
from bs4 import BeautifulSoup
import sqlite3
from datetime import datetime
import re
import time
from urllib.parse import urljoin, urlparse
from typing import List, Dict

class WebCrawlerService:
    def __init__(self, db_path="plagiarism.db"):
        self.db_path = db_path
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
    
    def crawl_search_results(self, query: str, num_results: int = 5) -> List[Dict]:
        """Google 검색 결과를 크롤링 (시뮬레이션)"""
        print(f"🔍 '{query}' 검색 중...")
        
        # 실제 환경에서는 Google Search API나 다른 검색 엔진 API 사용
        # 여기서는 시뮬레이션용으로 일반적인 웹사이트들을 크롤링
        
        # 다양한 한국어 콘텐츠 사이트들
        sample_urls = [
            "https://ko.wikipedia.org/wiki/%EC%9D%B8%EA%B3%B5%EC%A7%80%EB%8A%A5",
            "https://namu.wiki/w/%EC%9D%B8%EA%B3%B5%EC%A7%80%EB%8A%A5",
            "https://ko.wikipedia.org/wiki/%EA%B8%B0%EA%B3%84%ED%95%99%EC%8A%B5",
            "https://ko.wikipedia.org/wiki/%EA%B8%B0%ED%9B%84_%EB%B3%80%ED%99%94",
            "https://ko.wikipedia.org/wiki/%EA%B5%90%EC%9C%A1",
            # 추가 한국어 콘텐츠 사이트들
            "https://terms.naver.com/entry.naver?docId=3478014&cid=58439&categoryId=58439",  # 네이버 지식백과
            "https://100.daum.net/encyclopedia/view/14XXE0031576",  # 다음백과 (예시)
            "https://ko.wikipedia.org/wiki/%EC%A0%95%EC%B9%98",
            "https://ko.wikipedia.org/wiki/%EA%B2%BD%EC%A0%9C",
            "https://ko.wikipedia.org/wiki/%EC%82%AC%ED%9A%8C",
        ]
        
        results = []
        for i, url in enumerate(sample_urls[:num_results]):
            try:
                content = self.crawl_article(url)
                if content and len(content.get('content', '')) > 100:
                    results.append(content)
                    print(f"✅ 크롤링 완료 {i+1}/{num_results}: {content['title'][:50]}...")
                else:
                    print(f"❌ 크롤링 실패: {url}")
                    
                # 요청 간 지연
                time.sleep(1)
                
            except Exception as e:
                print(f"❌ 오류: {url} - {e}")
                
        return results
    
    def crawl_article(self, url: str) -> Dict:
        """개별 웹페이지 크롤링"""
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 제목 추출
            title = self._extract_title(soup) or self._extract_title_from_url(url)
            
            # 본문 추출
            content = self._extract_content(soup)
            
            if content and len(content) > 100:
                return {
                    'title': title,
                    'content': self._clean_text(content),
                    'url': url,
                    'source_type': 'crawled'
                }
                
        except Exception as e:
            print(f"크롤링 오류 {url}: {e}")
            
        return None
    
    def _extract_title(self, soup: BeautifulSoup) -> str:
        """제목 추출"""
        # 여러 가능한 제목 선택자 시도
        selectors = [
            'title',
            'h1',
            '.title',
            '#title',
            '[class*="title"]'
        ]
        
        for selector in selectors:
            element = soup.select_one(selector)
            if element and element.get_text().strip():
                return element.get_text().strip()[:200]
                
        return "제목 없음"
    
    def _extract_content(self, soup: BeautifulSoup) -> str:
        """본문 추출"""
        # 불필요한 요소 제거
        for element in soup(['script', 'style', 'nav', 'footer', 'header', 'aside']):
            element.decompose()
        
        # 본문 후보들
        content_selectors = [
            '.content',
            '.article',
            '.post',
            '#content',
            'main',
            '.main-content',
            'article',
            '.entry-content'
        ]
        
        # 선택자로 본문 찾기
        for selector in content_selectors:
            elements = soup.select(selector)
            if elements:
                content = ' '.join([el.get_text() for el in elements])
                if len(content) > 200:
                    return content
        
        # 모든 p 태그 내용
        paragraphs = soup.find_all('p')
        if paragraphs:
            content = ' '.join([p.get_text() for p in paragraphs])
            if len(content) > 200:
                return content
        
        # 전체 텍스트
        return soup.get_text()
    
    def _extract_title_from_url(self, url: str) -> str:
        """URL에서 제목 추출"""
        parsed = urlparse(url)
        domain = parsed.netloc
        path = parsed.path
        
        return f"{domain}{path}"[:100]
    
    def _clean_text(self, text: str) -> str:
        """텍스트 정리"""
        # 불필요한 공백 제거
        text = re.sub(r'\s+', ' ', text)
        # 특수 문자 정리
        text = re.sub(r'[^\w\s가-힣.,!?]', '', text)
        # 길이 제한 (데이터베이스 저장 용량 고려)
        return text.strip()[:5000]
    
    def save_to_database(self, articles: List[Dict]) -> int:
        """크롤링된 데이터를 데이터베이스에 저장"""
        if not articles:
            return 0
            
        try:
            conn = sqlite3.connect(self.db_path)
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
                    print(f"⚠️  이미 존재: {article['title'][:50]}...")
                    continue
                
                # 저장
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
                print(f"💾 저장됨: {article['title'][:50]}...")
            
            conn.commit()
            conn.close()
            
            return saved_count
            
        except Exception as e:
            print(f"❌ 데이터베이스 저장 오류: {e}")
            return 0
    
    def crawl_and_save(self, query: str, num_results: int = 5) -> Dict:
        """검색하고 크롤링해서 데이터베이스에 저장"""
        print(f"🚀 웹 크롤링 시작: '{query}'")
        
        # 검색 결과 크롤링
        articles = self.crawl_search_results(query, num_results)
        
        # 데이터베이스 저장
        saved_count = self.save_to_database(articles)
        
        # 결과 반환
        result = {
            'query': query,
            'total_crawled': len(articles),
            'saved_count': saved_count,
            'articles': [
                {
                    'title': article['title'][:100],
                    'content_length': len(article['content']),
                    'url': article['url']
                }
                for article in articles
            ]
        }
        
        print(f"✅ 크롤링 완료: {len(articles)}개 수집, {saved_count}개 저장")
        return result

if __name__ == "__main__":
    # 테스트
    crawler = WebCrawlerService()
    
    # 여러 주제로 크롤링
    queries = ["인공지능", "기후변화", "교육", "건강"]
    
    for query in queries:
        result = crawler.crawl_and_save(query, 3)
        print(f"\n📊 결과: {result}")
        print("-" * 50)