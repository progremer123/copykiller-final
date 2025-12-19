#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""모든 기능 통합 테스트"""

import sys
import os

# 파이썬 UTF-8 인코딩 설정
sys.stdout.reconfigure(encoding='utf-8') if hasattr(sys.stdout, 'reconfigure') else None

import requests
import json
import time

BASE_URL = "http://127.0.0.1:8006"

def test_plagiarism_check():
    """표절 검사 테스트"""
    print("\n" + "="*50)
    print("✅ 1. 기본 표절 검사")
    print("="*50)
    
    test_text = "인공지능은 현대 사회에서 매우 중요한 역할을 합니다. 특히 의료, 교육 분야에서 활발하게 사용되고 있습니다."
    
    response = requests.post(
        f"{BASE_URL}/api/check/text",
        json={"text": test_text}
    )
    
    if response.status_code == 200:
        result = response.json()
        check_id = result.get("id") or result.get("check_id")  # id 필드가 정답
        print(f"✅ 표절 검사 성공!")
        print(f"   - 검사 ID: {check_id}")
        print(f"   - 유사도: {result.get('similarity_score', 0):.1f}%")
        print(f"   - 매치 수: {len(result.get('matches', []))}")
        return check_id
    else:
        print(f"❌ 표절 검사 실패: {response.status_code}")
        return None

def test_sentence_improvement(check_id):
    """문장 개선 테스트"""
    print("\n" + "="*50)
    print("✅ 2. 문장 개선 제안")
    print("="*50)
    
    response = requests.post(
        f"{BASE_URL}/api/improve/check/{check_id}",
        json={}
    )
    
    if response.status_code == 200:
        result = response.json()
        suggestions = result.get("improvement_data", {}).get("suggestions", [])
        print(f"✅ 문장 개선 성공!")
        print(f"   - 제안 수: {len(suggestions)}")
        if suggestions:
            print(f"   - 첫 번째 제안:")
            print(f"     원본: {suggestions[0].get('original', '')}")
            print(f"     개선: {suggestions[0].get('improved', '')}")
    else:
        print(f"❌ 문장 개선 실패: {response.status_code}")

def test_plagiarism_avoidance():
    """표절 회피 테스트"""
    print("\n" + "="*50)
    print("✅ 3. AI 표절 회피 (check_id 방식)")
    print("="*50)
    
    # 먼저 표절 검사 수행
    test_text = "디지털 트랜스포메이션은 기업의 생존과 성장을 위한 필수 요소가 되었습니다."
    check_response = requests.post(
        f"{BASE_URL}/api/check/text",
        json={"text": test_text}
    )
    
    if check_response.status_code != 200:
        print(f"❌ 표절 검사 실패: {check_response.status_code}")
        return
    
    check_id = check_response.json().get("id")
    if not check_id:
        print("❌ check_id를 받지 못했습니다")
        return
    
    # check_id로 표절 회피 요청
    response = requests.post(
        f"{BASE_URL}/api/avoid-plagiarism/{check_id}",
        json={}
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ 표절 회피 성공!")
        print(f"   - 원본: {result.get('original_text', '')[:50]}...")
        print(f"   - 수정본: {result.get('rewritten_text', '')[:50]}...")
        print(f"   - 유사도 감소: {result.get('similarity_reduction', 0):.1f}%")
        print(f"   - 수정 부분: {len(result.get('modifications', []))}개")
    else:
        print(f"❌ 표절 회피 실패: {response.status_code}")
        print(f"   응답: {response.text}")

def test_advanced_analysis():
    """고급 분석 테스트"""
    print("\n" + "="*50)
    print("✅ 4. 고급 분석 (프리미엄)")
    print("="*50)
    
    test_text = "인공지능은 현대 사회에서 매우 중요한 역할을 합니다."
    
    response = requests.post(
        f"{BASE_URL}/api/premium/advanced-analysis",
        json={"text": test_text}
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ 고급 분석 성공!")
        print(f"   - 분석 항목: {len(result.get('features', []))}개")
    else:
        print(f"❌ 고급 분석 실패: {response.status_code}")

def test_context_analysis():
    """맥락 분석 테스트"""
    print("\n" + "="*50)
    print("✅ 5. 맥락 분석 (프리미엄)")
    print("="*50)
    
    test_text = "인공지능은 현대 사회에서 매우 중요한 역할을 합니다."
    
    response = requests.post(
        f"{BASE_URL}/api/premium/context-analysis",
        json={
            "text": test_text,
            "matches": []
        }
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ 맥락 분석 성공!")
        print(f"   - 분석 완료")
    else:
        print(f"❌ 맥락 분석 실패: {response.status_code}")

def test_improvement_suggestions():
    """개선 제안 테스트"""
    print("\n" + "="*50)
    print("✅ 6. 개선 제안 (프리미엄)")
    print("="*50)
    
    test_text = "인공지능은 현대 사회에서 매우 중요한 역할을 합니다."
    
    response = requests.post(
        f"{BASE_URL}/api/premium/improvement-suggestions",
        json={
            "text": test_text,
            "matches": []
        }
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ 개선 제안 성공!")
        print(f"   - 제안 수: {len(result.get('suggestions', []))}개")
    else:
        print(f"❌ 개선 제안 실패: {response.status_code}")

def main():
    print("\n")
    print("🚀" * 25)
    print("CopyKiller 모든 기능 통합 테스트")
    print("🚀" * 25)
    
    # 1. 표절 검사
    check_id = test_plagiarism_check()
    
    if check_id:
        # 2. 문장 개선
        time.sleep(1)
        test_sentence_improvement(check_id)
    
    # 3. 표절 회피
    time.sleep(1)
    test_plagiarism_avoidance()
    
    # 4. 고급 분석
    time.sleep(1)
    test_advanced_analysis()
    
    # 5. 맥락 분석
    time.sleep(1)
    test_context_analysis()
    
    # 6. 개선 제안
    time.sleep(1)
    test_improvement_suggestions()
    
    print("\n" + "="*50)
    print("✅ 모든 테스트 완료!")
    print("="*50 + "\n")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n❌ 테스트 중 오류 발생: {e}")
