#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json

def test_plagiarism_api():
    """표절 검사 API 테스트"""
    
    print("🔍 표절 검사 API 테스트")
    print("=" * 50)
    
    # 1. API Health 체크
    print("\n📡 1. API Health 체크")
    try:
        response = requests.get("http://localhost:8005/api/health")
        if response.status_code == 200:
            print(f"   ✅ API Health 성공: {response.json()}")
        else:
            print(f"   ❌ API Health 실패: {response.status_code}")
    except Exception as e:
        print(f"   ❌ API Health 에러: {e}")
    
    # 2. 표절 검사 테스트
    print("\n📝 2. 표절 검사 테스트")
    try:
        test_text = "인공지능은 컴퓨터 시스템이 인간의 지적 능력을 모방하는 기술입니다. 머신러닝과 딥러닝을 통해 데이터로부터 패턴을 학습하고 예측을 수행할 수 있습니다."
        payload = {"text": test_text}
        
        response = requests.post(
            "http://localhost:8005/api/check/text",
            headers={"Content-Type": "application/json"},
            data=json.dumps(payload)
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ 표절 검사 성공!")
            print(f"   📊 유사도: {result.get('similarity', 'N/A')}%")
            print(f"   🔍 발견된 일치: {len(result.get('matches', []))}개")
            print(f"   📁 검사 ID: {result.get('check_id', 'N/A')}")
        else:
            print(f"   ❌ 표절 검사 실패: {response.status_code}")
            print(f"   응답: {response.text}")
    except Exception as e:
        print(f"   ❌ 표절 검사 에러: {e}")
    
    # 3. 프론트엔드 프록시를 통한 테스트
    print("\n🌐 3. 프론트엔드 프록시 테스트")
    try:
        response = requests.get("http://localhost:8080/api/health")
        if response.status_code == 200:
            print(f"   ✅ 프록시를 통한 API 연결 성공: {response.json()}")
        else:
            print(f"   ❌ 프록시 연결 실패: {response.status_code}")
    except Exception as e:
        print(f"   ❌ 프록시 연결 에러: {e}")
    
    print("\n" + "=" * 50)
    print("🎯 테스트 완료!")
    print("✅ 백엔드: http://localhost:8005")
    print("✅ 프론트엔드: http://localhost:8080")
    print("✅ API 문서: http://localhost:8005/docs")

if __name__ == "__main__":
    test_plagiarism_api()