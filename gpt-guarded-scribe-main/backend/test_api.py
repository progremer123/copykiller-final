#!/usr/bin/env python3
"""API 연결 테스트 스크립트"""

import requests
import json

def test_api():
    print("🌐 API 연결 테스트 시작...")
    
    url = "http://localhost:8001/api/v1/check/text"
    
    payload = {
        "text": "인공지능은 현대 사회에서 중요한 역할을 하고 있습니다. 머신러닝 기술의 발전으로 혁신이 일어나고 있습니다."
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    try:
        print(f"📡 요청 보내는 중: {url}")
        print(f"📝 텍스트: {payload['text'][:50]}...")
        
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        
        print(f"📊 응답 상태: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ API 호출 성공!")
            print(f"📄 결과 ID: {result.get('check_id')}")
            print(f"🔍 유사도: {result.get('similarity', 0):.1f}%")
            print(f"📚 매치 수: {len(result.get('matches', []))}")
        else:
            print(f"❌ API 호출 실패: {response.status_code}")
            print(f"오류 내용: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ 서버에 연결할 수 없습니다. 서버가 실행 중인지 확인하세요.")
    except requests.exceptions.Timeout:
        print("❌ 요청 시간 초과")
    except Exception as e:
        print(f"❌ 오류 발생: {e}")

if __name__ == "__main__":
    test_api()