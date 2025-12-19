#!/usr/bin/env python3
"""크롤링 API 테스트"""

import requests
import json

def test_crawling_api():
    print("🌐 웹 크롤링 API 테스트\n")
    
    base_url = "http://localhost:8001/api/v1"
    
    # 1. 현재 데이터베이스 상태 확인
    print("1️⃣ 현재 데이터베이스 상태:")
    try:
        response = requests.get(f"{base_url}/database/stats")
        if response.status_code == 200:
            stats = response.json()
            print(f"   📚 총 문서 수: {stats['total_documents']}개")
            for source_type in stats['source_types']:
                print(f"   - {source_type['type']}: {source_type['count']}개")
        else:
            print(f"   ❌ 오류: {response.status_code}")
    except Exception as e:
        print(f"   ❌ 요청 오류: {e}")
    
    print("\n" + "="*50 + "\n")
    
    # 2. 새로운 주제로 크롤링
    print("2️⃣ 새로운 주제 크롤링:")
    crawl_queries = ["우주 탐사", "로봇 기술"]
    
    for query in crawl_queries:
        try:
            print(f"\n🔍 '{query}' 크롤링 요청...")
            response = requests.post(
                f"{base_url}/crawl",
                params={"query": query, "num_results": 2}
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"   ✅ 성공: {result['saved_count']}/{result['total_crawled']}개 저장")
                for article in result['articles']:
                    print(f"      📄 {article['title'][:50]}... ({article['content_length']}자)")
            else:
                print(f"   ❌ 오류: {response.status_code}")
                print(f"   응답: {response.text}")
                
        except Exception as e:
            print(f"   ❌ 요청 오류: {e}")
    
    print("\n" + "="*50 + "\n")
    
    # 3. 업데이트된 데이터베이스 상태 확인
    print("3️⃣ 업데이트된 데이터베이스 상태:")
    try:
        response = requests.get(f"{base_url}/database/stats")
        if response.status_code == 200:
            stats = response.json()
            print(f"   📚 총 문서 수: {stats['total_documents']}개")
            for source_type in stats['source_types']:
                print(f"   - {source_type['type']}: {source_type['count']}개")
        else:
            print(f"   ❌ 오류: {response.status_code}")
    except Exception as e:
        print(f"   ❌ 요청 오류: {e}")

if __name__ == "__main__":
    test_crawling_api()