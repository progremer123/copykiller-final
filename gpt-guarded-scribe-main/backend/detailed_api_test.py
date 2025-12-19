#!/usr/bin/env python3
"""상세 API 테스트"""

import requests
import json

def detailed_api_test():
    print("🔍 상세 API 테스트...")
    
    url = "http://localhost:8001/api/v1/check/text"
    
    payload = {
        "text": "인공지능은 현대 사회에서 중요한 역할을 하고 있습니다. 머신러닝 기술의 발전으로 혁신이 일어나고 있습니다."
    }
    
    try:
        response = requests.post(url, json=payload, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ 완전한 응답:")
            print(json.dumps(result, indent=2, ensure_ascii=False))
            
            # 각 필드 상세 분석
            print(f"\n📊 상세 분석:")
            print(f"   - ID: {result.get('id')}")
            print(f"   - 유사도: {result.get('similarity_score')}%")
            print(f"   - 상태: {result.get('status')}")
            print(f"   - 매치 수: {len(result.get('matches', []))}")
            
            matches = result.get('matches', [])
            for i, match in enumerate(matches[:3], 1):  # 처음 3개만 표시
                print(f"   📄 매치 {i}:")
                print(f"      - 소스: {match.get('source_title', 'Unknown')}")
                print(f"      - 유사도: {match.get('similarity_score', 0)}%")
                print(f"      - 매치 텍스트: {match.get('matched_text', 'N/A')[:50]}...")
                
        else:
            print(f"❌ 오류: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"❌ 예외 발생: {e}")

if __name__ == "__main__":
    detailed_api_test()