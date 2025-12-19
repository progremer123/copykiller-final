#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json

def test_basic_api():
    """기본 API 기능 테스트"""
    
    print("🔍 기본 표절검사 API 테스트")
    print("=" * 50)
    
    base_url = "http://localhost:8005"
    
    # 1. 서버 상태 확인
    print("\n📡 1. 서버 상태 확인")
    try:
        response = requests.get(f"{base_url}/")
        print(f"   상태 코드: {response.status_code}")
        if response.status_code == 200:
            print(f"   ✅ 서버 정상 작동: {response.json()}")
        else:
            print(f"   ❌ 서버 오류: {response.text}")
    except Exception as e:
        print(f"   ❌ 연결 실패: {e}")
    
    # 2. 헬스 체크
    print("\n🔍 2. 헬스 체크")
    try:
        response = requests.get(f"{base_url}/health")
        print(f"   상태 코드: {response.status_code}")
        if response.status_code == 200:
            print(f"   ✅ 헬스 체크 성공: {response.json()}")
        else:
            print(f"   ❌ 헬스 체크 실패: {response.text}")
    except Exception as e:
        print(f"   ❌ 에러: {e}")
    
    # 3. 기본 표절 검사
    print("\n📝 3. 기본 표절 검사")
    try:
        test_text = "인공지능은 컴퓨터 시스템이 인간의 지적 능력을 모방하는 기술입니다."
        payload = {"text": test_text}
        
        response = requests.post(
            f"{base_url}/api/check/text",
            headers={"Content-Type": "application/json"},
            data=json.dumps(payload)
        )
        print(f"   상태 코드: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ 표절 검사 성공!")
            print(f"   📊 유사도: {result.get('similarity', 'N/A')}%")
            print(f"   🔍 발견된 일치: {len(result.get('matches', []))}개")
        else:
            print(f"   ❌ 표절 검사 실패: {response.text}")
    except Exception as e:
        print(f"   ❌ 에러: {e}")
    
    print("\n" + "=" * 50)
    print("✅ 기본 API 테스트 완료!")

if __name__ == "__main__":
    test_basic_api()