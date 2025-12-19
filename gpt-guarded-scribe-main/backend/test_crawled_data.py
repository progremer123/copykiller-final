#!/usr/bin/env python3
"""크롤링 후 표절 검사 테스트"""

import requests
import json

def test_with_crawled_data():
    print("🔍 크롤링 데이터를 활용한 표절 검사 테스트\n")
    
    url = "http://localhost:8001/api/v1/check/text"
    
    # 크롤링된 데이터와 매칭될 가능성이 있는 다양한 텍스트들
    test_cases = [
        {
            "name": "기계학습 관련 (위키백과 매치 예상)",
            "text": "기계 학습은 컴퓨터가 데이터를 통해 학습하는 방법입니다. 알고리즘을 사용하여 패턴을 찾고 예측을 수행합니다."
        },
        {
            "name": "인공지능 관련 (나무위키 매치 예상)",
            "text": "인공지능은 인간의 지능을 모방하는 컴퓨터 시스템입니다. 다양한 분야에서 활용되고 있습니다."
        },
        {
            "name": "기후변화 관련 (위키백과 매치 예상)",
            "text": "기후변화는 지구의 기후 시스템에 장기적인 변화를 의미합니다. 온실가스 배출이 주요 원인입니다."
        },
        {
            "name": "완전 다른 주제 (매치 없을 예상)",
            "text": "축구는 전 세계에서 가장 인기 있는 스포츠입니다. 두 팀이 공을 차서 골을 넣는 경기입니다."
        },
        {
            "name": "일반적인 설명 (부분 매치 예상)",
            "text": "기술의 발전은 사회에 큰 영향을 미치고 있습니다. 새로운 방법과 시스템이 계속 등장하고 있습니다."
        }
    ]
    
    for i, case in enumerate(test_cases, 1):
        print(f"📝 테스트 {i}: {case['name']}")
        print(f"   입력: {case['text']}")
        
        try:
            response = requests.post(url, json={"text": case["text"]}, timeout=15)
            
            if response.status_code == 200:
                result = response.json()
                similarity = result.get('similarity_score', 0)
                matches_count = len(result.get('matches', []))
                
                print(f"   🎯 유사도: {similarity}%")
                print(f"   📚 매치 수: {matches_count}개")
                
                if matches_count > 0:
                    # 상위 3개 매치 표시
                    matches = result.get('matches', [])
                    for j, match in enumerate(matches[:3], 1):
                        source_title = match.get('source_title', 'Unknown')
                        match_score = match.get('similarity_score', 0)
                        matched_text = match.get('matched_text', '')[:50]
                        print(f"     {j}. '{source_title[:30]}...' ({match_score:.1f}%) - '{matched_text}...'")
                else:
                    print("     매치 없음")
                
            else:
                print(f"   ❌ API 오류: {response.status_code}")
                print(f"   응답: {response.text}")
                
        except Exception as e:
            print(f"   ❌ 요청 오류: {e}")
        
        print()

if __name__ == "__main__":
    test_with_crawled_data()