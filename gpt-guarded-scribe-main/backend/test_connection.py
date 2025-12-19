#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json

def test_frontend_backend_connection():
    """프론트엔드-백엔드 연결 테스트"""
    
    print("🌐 프론트엔드-백엔드 연결 테스트")
    print("=" * 50)
    
    # 1. 백엔드 직접 연결 테스트
    print("\n🔙 1. 백엔드 직접 연결 (포트 8005)")
    try:
        response = requests.get("http://localhost:8005/")
        if response.status_code == 200:
            print(f"   ✅ 백엔드 연결 성공: {response.json()}")
        else:
            print(f"   ❌ 백엔드 연결 실패: {response.status_code}")
    except Exception as e:
        print(f"   ❌ 백엔드 연결 에러: {e}")
    
    # 2. 프론트엔드를 통한 API 프록시 테스트
    print("\n🔄 2. 프론트엔드 프록시를 통한 API 연결 (포트 5173)")
    try:
        response = requests.get("http://localhost:5173/api/")
        if response.status_code == 200:
            print(f"   ✅ 프록시를 통한 연결 성공: {response.json()}")
        else:
            print(f"   ❌ 프록시를 통한 연결 실패: {response.status_code}")
            print(f"   응답 내용: {response.text}")
    except Exception as e:
        print(f"   ❌ 프록시 연결 에러: {e}")
    
    # 3. 표절 검사 API 테스트
    print("\n📝 3. 표절 검사 API 테스트")
    try:
        test_text = "인공지능은 미래의 핵심 기술입니다."
        payload = {"text": test_text}
        
        response = requests.post(
            "http://localhost:5173/api/check/text",
            headers={"Content-Type": "application/json"},
            data=json.dumps(payload)
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ 표절 검사 성공!")
            print(f"   📊 유사도: {result.get('similarity', 'N/A')}%")
            print(f"   🔍 발견된 일치: {len(result.get('matches', []))}개")
        else:
            print(f"   ❌ 표절 검사 실패: {response.status_code}")
            print(f"   응답: {response.text}")
    except Exception as e:
        print(f"   ❌ 표절 검사 에러: {e}")
    
    print("\n" + "=" * 50)
    print("🎯 연결 상태 요약:")
    print("• 백엔드: http://localhost:8005")
    print("• 프론트엔드: http://localhost:5173")
    print("• 프록시: /api → http://localhost:8005")

if __name__ == "__main__":
    test_frontend_backend_connection()