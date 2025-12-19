#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json

def test_simple_plagiarism():
    """간단한 표절 검사 테스트"""
    
    print("🔍 간단한 표절 검사 테스트")
    print("=" * 40)
    
    # 아주 짧고 간단한 텍스트로 테스트
    test_text = "안녕하세요. 테스트입니다. 간단한 문장입니다."
    
    payload = {"text": test_text}
    
    print(f"📝 테스트 텍스트: {test_text}")
    print(f"📏 텍스트 길이: {len(test_text)}자")
    
    try:
        print("\n🚀 API 호출 중...")
        response = requests.post(
            "http://localhost:8005/api/check/text",
            headers={"Content-Type": "application/json"},
            data=json.dumps(payload),
            timeout=30  # 30초 타임아웃
        )
        
        print(f"📡 응답 상태 코드: {response.status_code}")
        print(f"📋 응답 헤더: {dict(response.headers)}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"\n✅ 성공!")
            print(f"응답 내용: {result}")
        else:
            print(f"\n❌ 실패!")
            print(f"응답 텍스트: {response.text}")
            
    except requests.exceptions.Timeout:
        print("⏰ 요청 시간 초과 (30초)")
    except requests.exceptions.ConnectionError:
        print("🔌 연결 실패")
    except Exception as e:
        print(f"❌ 예외 발생: {e}")

if __name__ == "__main__":
    test_simple_plagiarism()