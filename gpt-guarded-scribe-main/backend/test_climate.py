#!/usr/bin/env python3
"""웹 인터페이스 테스트용 API 호출"""

import requests
import json

def test_climate_text():
    print("🌍 기후 변화 텍스트 표절 검사 테스트")
    
    url = "http://localhost:8001/api/v1/check/text"
    
    # 웹에서 보이는 텍스트와 동일한 내용
    payload = {
        "text": "기후 변화는 21세기 인류가 직면한 가장 심각한 도전 중 하나입니다. 지구 온난화로 인한 해수면 상승, 극단적 기상 현상의 증가, 생태계 파괴 등은 전 세계적인 대응을 필요로 합니다."
    }
    
    try:
        print(f"📡 요청 URL: {url}")
        print(f"📝 검사할 텍스트: {payload['text'][:50]}...")
        
        response = requests.post(url, json=payload, timeout=30)
        
        print(f"📊 HTTP 상태: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("\n✅ 성공적인 응답:")
            print(json.dumps(result, indent=2, ensure_ascii=False))
            
            # 핵심 정보 요약
            similarity = result.get('similarity_score', 0)
            matches_count = len(result.get('matches', []))
            
            print(f"\n🎯 핵심 결과:")
            print(f"   🔍 유사도: {similarity}%")
            print(f"   📚 매치 수: {matches_count}")
            
            if matches_count > 0:
                print(f"   📄 주요 매치:")
                for i, match in enumerate(result.get('matches', [])[:3], 1):
                    print(f"      {i}. '{match.get('source_title', 'Unknown')}' - {match.get('similarity_score', 0)}%")
            
        else:
            print(f"❌ 오류 응답:")
            print(f"   상태: {response.status_code}")
            print(f"   내용: {response.text}")
            
    except Exception as e:
        print(f"❌ 예외 발생: {e}")

if __name__ == "__main__":
    test_climate_text()