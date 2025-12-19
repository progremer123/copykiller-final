#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""AI 표절 회피 테스트"""

import sys
sys.stdout.reconfigure(encoding='utf-8') if hasattr(sys.stdout, 'reconfigure') else None

import requests
import json

BASE_URL = "http://127.0.0.1:8006"

def test_ai_avoidance():
    # 표절 검사 먼저 수행
    test_text = '인공지능은 현대 사회에서 매우 중요한 역할을 합니다. 특히 의료, 교육, 금융 등 다양한 분야에서 활용되고 있습니다.'

    print('1️⃣ 표절 검사 수행 중...')
    check_response = requests.post(f'{BASE_URL}/api/check/text', json={'text': test_text})
    check_data = check_response.json()
    check_id = check_data.get('id')
    print(f'✅ 검사 완료 - ID: {check_id}')
    print(f'   유사도: {check_data.get("similarity_score")}%')

    print('\n2️⃣ AI 표절 회피 실행 중...')
    avoid_response = requests.post(f'{BASE_URL}/api/avoid-plagiarism/{check_id}', json={})
    
    if avoid_response.status_code != 200:
        print(f'❌ 오류: {avoid_response.status_code}')
        print(avoid_response.text)
        return
    
    avoid_data = avoid_response.json()

    print(f'\n📊 결과:')
    print(f'  - 유사도 감소: {avoid_data.get("similarity_reduction", 0):.1f}%')
    print(f'  - 수정 부분: {len(avoid_data.get("modifications", []))}개')
    print(f'  - 신뢰도: {avoid_data.get("confidence_score", 0):.1f}%')
    
    print(f'\n📝 원본:')
    print(f'  {avoid_data.get("original_text", "")}')
    print(f'\n✨ 수정본:')
    print(f'  {avoid_data.get("rewritten_text", "")}')
    
    if avoid_data.get("modifications"):
        print(f'\n🔧 수정 상세:')
        for i, mod in enumerate(avoid_data.get("modifications", [])[:3], 1):
            print(f'  {i}. "{mod.get("original", "")}" → "{mod.get("rewritten", "")}"')

if __name__ == "__main__":
    test_ai_avoidance()
