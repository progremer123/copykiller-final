#!/usr/bin/env python3
"""다양한 텍스트 표절 검사 테스트"""

import requests
import json

def test_various_texts():
    print("🔍 다양한 텍스트 표절 검사 테스트\n")
    
    url = "http://localhost:8001/api/v1/check/text"
    
    test_cases = [
        {
            "name": "교육 관련 텍스트",
            "text": "교육은 미래 사회 발전의 핵심입니다. 창의적 사고 능력을 기르는 것이 중요합니다."
        },
        {
            "name": "건강 관련 텍스트",
            "text": "건강한 생활을 위해서는 규칙적인 운동과 균형 잡힌 식단이 필요합니다."
        },
        {
            "name": "여행 관련 텍스트",
            "text": "여행을 통해 새로운 문화를 체험하고 시야를 넓힐 수 있습니다."
        },
        {
            "name": "완전 새로운 내용",
            "text": "우주선이 화성에 착륙했습니다. 외계 생명체를 찾는 탐사가 시작되었습니다."
        }
    ]
    
    for i, case in enumerate(test_cases, 1):
        print(f"📝 테스트 {i}: {case['name']}")
        print(f"   입력: {case['text']}")
        
        try:
            response = requests.post(url, json={"text": case["text"]}, timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                similarity = result.get('similarity_score', 0)
                matches_count = len(result.get('matches', []))
                
                print(f"   🎯 유사도: {similarity}%")
                print(f"   📚 매치 수: {matches_count}개")
                
                if matches_count > 0:
                    top_match = result.get('matches', [])[0]
                    print(f"   📄 최고 매치: '{top_match.get('source_title', 'Unknown')}' ({top_match.get('similarity_score', 0)}%)")
                
            else:
                print(f"   ❌ 오류: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ 예외: {e}")
        
        print()

if __name__ == "__main__":
    test_various_texts()