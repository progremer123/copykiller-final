#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""AI 기반 고급 웹 크롤링 서비스"""

import requests
from bs4 import BeautifulSoup
import sqlite3
from datetime import datetime
import re
import time
import json
from urllib.parse import urljoin, urlparse, quote
from typing import List, Dict, Optional
import random
from dataclasses import dataclass

@dataclass
class CrawlTarget:
    """크롤링 대상 정보"""
    domain: str
    name: str
    search_url_pattern: str
    content_selectors: List[str]
    title_selectors: List[str]
    requires_js: bool = False

class AICrawlerService:
    """AI 기반 고급 웹 크롤링 서비스"""
    
    def __init__(self, db_path="plagiarism.db"):
        self.db_path = db_path
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'ko-KR,ko;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
        
        # 다양한 한국어 컨텐츠 소스 정의
        self.crawl_targets = {
            'wikipedia': CrawlTarget(
                domain='ko.wikipedia.org',
                name='위키백과',
                search_url_pattern='https://ko.wikipedia.org/w/api.php?action=opensearch&search={}&limit=10&format=json',
                content_selectors=['.mw-parser-output', '#mw-content-text', '.mw-content-ltr'],
                title_selectors=['h1.firstHeading', '.mw-page-title-main', 'h1']
            ),
            'namuwiki': CrawlTarget(
                domain='namu.wiki',
                name='나무위키',
                search_url_pattern='https://namu.wiki/Search?q={}',
                content_selectors=['.wiki-content', '.wiki-article', '#app'],
                title_selectors=['.wiki-title', 'h1', '.title']
            ),
            'naver_encyclopedia': CrawlTarget(
                domain='terms.naver.com',
                name='네이버 지식백과',
                search_url_pattern='https://search.naver.com/search.naver?where=nexearch&sm=top_hty&fbm=0&ie=utf8&query=site:terms.naver.com {}',
                content_selectors=['.se_component', '.api_cs_wrap', '.content_area'],
                title_selectors=['.headword', 'h2', '.title']
            ),
            'doopedia': CrawlTarget(
                domain='www.doopedia.co.kr',
                name='두산백과',
                search_url_pattern='https://www.doopedia.co.kr/search/encyber/result.do?query={}',
                content_selectors=['.viewcon', '.cont', '.content'],
                title_selectors=['.tit', 'h1', '.title']
            ),
            'kpedia': CrawlTarget(
                domain='kpedia.jp',
                name='한국어 위키',
                search_url_pattern='https://kpedia.jp/s/{}/1',
                content_selectors=['.content', '.article', '.main'],
                title_selectors=['.title', 'h1', 'h2']
            ),
            'korean_history': CrawlTarget(
                domain='contents.history.go.kr',
                name='한국사 콘텐츠',
                search_url_pattern='https://contents.history.go.kr/mobile/ka/search.do?keywords={}',
                content_selectors=['.cont_area', '.content', '.article'],
                title_selectors=['.tit', 'h1', '.title']
            ),
            'korean_culture': CrawlTarget(
                domain='encykorea.aks.ac.kr',
                name='한국민족문화대백과',
                search_url_pattern='https://encykorea.aks.ac.kr/search/SearchList.do?keyword={}',
                content_selectors=['.content', '.view_content', '.article_content'],
                title_selectors=['.view_title', 'h1', '.title']
            ),
            'science_all': CrawlTarget(
                domain='www.scienceall.com',
                name='사이언스올',
                search_url_pattern='https://www.scienceall.com/search/?q={}',
                content_selectors=['.content', '.article-content', '.entry-content'],
                title_selectors=['.entry-title', 'h1', '.title']
            )
        }
    
    def intelligent_search(self, query: str, num_results: int = 10) -> List[Dict]:
        """AI 기반 지능형 검색 및 크롤링"""
        print(f"🤖 AI 기반 지능형 검색 시작: '{query}'")
        
        all_articles = []
        
        # 1. 키워드 확장 및 다양화
        expanded_queries = self._expand_search_queries(query)
        print(f"📝 확장된 검색어: {expanded_queries}")
        
        # 2. 각 소스별로 크롤링
        for target_name, target in self.crawl_targets.items():
            print(f"\n🎯 {target.name} 크롤링 중...")
            
            for search_query in expanded_queries[:3]:  # 상위 3개 검색어만 사용
                try:
                    articles = self._crawl_from_source(target, search_query, max_articles=3)
                    all_articles.extend(articles)
                    print(f"✅ {target.name}: {len(articles)}개 수집")
                    
                    # 요청 간 지연 (차단 방지)
                    time.sleep(random.uniform(1, 3))
                    
                except Exception as e:
                    print(f"❌ {target.name} 오류: {e}")
                    continue
        
        # 3. 중복 제거 및 품질 필터링
        filtered_articles = self._filter_and_deduplicate(all_articles)
        
        # 4. 상위 결과만 반환
        return filtered_articles[:num_results]
    
    def _expand_search_queries(self, original_query: str) -> List[str]:
        """검색어 확장 및 다양화"""
        queries = [original_query]
        
        # 동의어 및 관련어 사전
        expansion_dict = {
            '인공지능': ['AI', '머신러닝', '기계학습', '딥러닝', '신경망', '알고리즘'],
            '기후변화': ['지구온난화', '탄소중립', '온실가스', '환경', '기후위기', '친환경'],
            '교육': ['학습', '학교', '교육과정', '교육제도', '교육정책', '학교교육'],
            '경제': ['경제학', '시장', '금융', '투자', '경제정책', '경제성장'],
            '건강': ['의학', '질병', '치료', '예방', '의료', '보건'],
            '기술': ['테크놀로지', '혁신', '과학기술', 'IT', '디지털', '첨단기술'],
            '사회': ['사회학', '공동체', '사회문제', '사회제도', '사회변화'],
            '정치': ['정부', '정책', '민주주의', '정치제도', '행정', '국정'],
            '문화': ['예술', '전통', '문화예술', '한국문화', '문화유산', '대중문화'],
            '역사': ['한국사', '세계사', '역사학', '전통', '문화재', '유적']
        }
        
        # 관련어 추가
        for keyword, related_terms in expansion_dict.items():
            if keyword in original_query:
                queries.extend(related_terms[:3])
        
        # 복합 검색어 생성
        if len(original_query.split()) == 1:
            compound_queries = [
                f"{original_query} 개념",
                f"{original_query} 정의",
                f"{original_query} 특징",
                f"{original_query} 현황",
                f"{original_query} 동향"
            ]
            queries.extend(compound_queries)
        
        return list(set(queries))[:10]  # 중복 제거 후 최대 10개
    
    def _crawl_from_source(self, target: CrawlTarget, query: str, max_articles: int = 5) -> List[Dict]:
        """특정 소스에서 크롤링"""
        articles = []
        
        try:
            # 검색 URL 생성
            search_url = target.search_url_pattern.format(quote(query))
            
            # 위키백과 API 특별 처리
            if target.domain == 'ko.wikipedia.org':
                return self._crawl_wikipedia_api(query, max_articles)
            
            # 일반 웹사이트 크롤링
            response = requests.get(search_url, headers=self.headers, timeout=15)
            if response.status_code != 200:
                return articles
                
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 검색 결과에서 링크 추출
            links = self._extract_search_result_links(soup, target)
            
            # 각 링크에서 콘텐츠 추출
            for link in links[:max_articles]:
                try:
                    article = self._extract_article_content(link, target)
                    if article:
                        articles.append(article)
                    time.sleep(random.uniform(0.5, 1.5))
                except Exception as e:
                    print(f"⚠️  링크 처리 실패 {link}: {e}")
                    continue
                    
        except Exception as e:
            print(f"❌ {target.name} 크롤링 오류: {e}")
            
        return articles
    
    def _crawl_wikipedia_api(self, query: str, max_articles: int = 5) -> List[Dict]:
        """위키백과 API를 통한 크롤링"""
        articles = []
        
        try:
            # OpenSearch API로 검색
            search_url = f"https://ko.wikipedia.org/w/api.php?action=opensearch&search={quote(query)}&limit={max_articles}&format=json"
            response = requests.get(search_url, headers=self.headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                titles = data[1] if len(data) > 1 else []
                urls = data[3] if len(data) > 3 else []
                
                for title, url in zip(titles, urls):
                    try:
                        # 각 페이지 내용 가져오기
                        content_response = requests.get(url, headers=self.headers, timeout=10)
                        if content_response.status_code == 200:
                            soup = BeautifulSoup(content_response.text, 'html.parser')
                            
                            # 본문 추출
                            content_element = soup.select_one('.mw-parser-output')
                            if content_element:
                                content = self._clean_text(content_element.get_text())
                                if len(content) > 200:
                                    articles.append({
                                        'title': title,
                                        'content': content,
                                        'url': url,
                                        'source_type': 'wikipedia',
                                        'source_name': '위키백과'
                                    })
                        
                        time.sleep(0.5)
                        
                    except Exception as e:
                        print(f"⚠️  위키백과 페이지 처리 실패 {title}: {e}")
                        continue
                        
        except Exception as e:
            print(f"❌ 위키백과 API 오류: {e}")
            
        return articles
    
    def _extract_search_result_links(self, soup: BeautifulSoup, target: CrawlTarget) -> List[str]:
        """검색 결과에서 링크 추출"""
        links = []
        
        # 일반적인 링크 선택자들
        link_selectors = ['a[href]', '.result a', '.search-result a', '.title a']
        
        for selector in link_selectors:
            elements = soup.select(selector)
            for element in elements:
                href = element.get('href', '')
                if href:
                    # 상대 링크를 절대 링크로 변환
                    if href.startswith('/'):
                        href = f"https://{target.domain}{href}"
                    elif href.startswith('http'):
                        # 동일 도메인인지 확인
                        if target.domain in href:
                            links.append(href)
                    
            if len(links) >= 10:
                break
                
        return list(set(links))[:10]
    
    def _extract_article_content(self, url: str, target: CrawlTarget) -> Optional[Dict]:
        """개별 기사 콘텐츠 추출"""
        try:
            response = requests.get(url, headers=self.headers, timeout=15)
            if response.status_code != 200:
                return None
                
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 제목 추출
            title = None
            for selector in target.title_selectors:
                element = soup.select_one(selector)
                if element:
                    title = element.get_text().strip()
                    break
            
            if not title:
                title = soup.title.get_text().strip() if soup.title else "제목 없음"
            
            # 본문 추출
            content = None
            for selector in target.content_selectors:
                element = soup.select_one(selector)
                if element:
                    content = self._clean_text(element.get_text())
                    if len(content) > 200:
                        break
            
            if not content or len(content) < 200:
                return None
            
            return {
                'title': title[:200],
                'content': content,
                'url': url,
                'source_type': 'crawled',
                'source_name': target.name
            }
            
        except Exception as e:
            print(f"❌ 콘텐츠 추출 실패 {url}: {e}")
            return None
    
    def _filter_and_deduplicate(self, articles: List[Dict]) -> List[Dict]:
        """중복 제거 및 품질 필터링"""
        # URL 기반 중복 제거
        seen_urls = set()
        unique_articles = []
        
        for article in articles:
            url = article.get('url', '')
            if url not in seen_urls:
                seen_urls.add(url)
                unique_articles.append(article)
        
        # 콘텐츠 길이 기준 필터링
        quality_articles = [
            article for article in unique_articles 
            if len(article.get('content', '')) >= 500
        ]
        
        # 제목 유사도 기반 중복 제거 (간단한 방식)
        final_articles = []
        seen_titles = set()
        
        for article in quality_articles:
            title = article.get('title', '').lower()
            title_key = ''.join(title.split()[:3])  # 첫 3단어로 유사도 판단
            
            if title_key not in seen_titles:
                seen_titles.add(title_key)
                final_articles.append(article)
        
        return final_articles
    
    def _clean_text(self, text: str) -> str:
        """텍스트 정리"""
        # 불필요한 공백 제거
        text = re.sub(r'\s+', ' ', text)
        # 특수 문자 정리 (한국어 보존)
        text = re.sub(r'[^\w\s가-힣ㄱ-ㅎㅏ-ㅣ.,!?():;-]', '', text)
        # 길이 제한
        return text.strip()[:8000]
    
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
                # 중복 체크 (URL과 제목 모두)
                cursor.execute("""
                    SELECT id FROM document_sources 
                    WHERE (url = ? OR title = ?) AND is_active = 1
                """, (article['url'], article['title']))
                
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
                    f"{article['source_type']}_{article.get('source_name', 'unknown')}",
                    current_time,
                    current_time,
                    1
                ))
                saved_count += 1
                print(f"💾 저장됨: [{article.get('source_name', 'Unknown')}] {article['title'][:50]}...")
            
            conn.commit()
            conn.close()
            
            return saved_count
            
        except Exception as e:
            print(f"❌ 데이터베이스 저장 오류: {e}")
            return 0
    
    def ai_enhanced_crawl(self, query: str, num_results: int = 15) -> Dict:
        """AI 강화 크롤링 메인 함수"""
        print(f"🚀 AI 강화 웹 크롤링 시작: '{query}'")
        print(f"🎯 대상 소스: {len(self.crawl_targets)}개 사이트")
        
        # 지능형 검색 및 크롤링
        articles = self.intelligent_search(query, num_results)
        
        # 데이터베이스 저장
        saved_count = self.save_to_database(articles)
        
        # 결과 정리
        result = {
            'query': query,
            'total_crawled': len(articles),
            'saved_count': saved_count,
            'sources_used': list(set([article.get('source_name', 'Unknown') for article in articles])),
            'articles': [
                {
                    'title': article['title'][:100],
                    'content_length': len(article['content']),
                    'url': article['url'],
                    'source': article.get('source_name', 'Unknown')
                }
                for article in articles
            ]
        }
        
        print(f"✅ AI 크롤링 완료:")
        print(f"   📊 총 수집: {len(articles)}개")
        print(f"   💾 저장: {saved_count}개")
        print(f"   🌐 사용 소스: {', '.join(result['sources_used'])}")
        
        return result

if __name__ == "__main__":
    # 테스트
    crawler = AICrawlerService()
    
    # 다양한 주제로 AI 크롤링 테스트
    test_queries = ["인공지능", "기후변화", "한국사", "경제학"]
    
    for query in test_queries:
        print(f"\n{'='*60}")
        result = crawler.ai_enhanced_crawl(query, 10)
        print(f"\n📈 결과 요약:")
        print(f"   검색어: {result['query']}")
        print(f"   수집: {result['total_crawled']}개")
        print(f"   저장: {result['saved_count']}개")
        print(f"   소스: {', '.join(result['sources_used'])}")
        print("="*60)