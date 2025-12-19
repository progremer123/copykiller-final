#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json

def test_premium_features():
    """프리미엄 고급 분석 기능 테스트"""
    
    print("🌟 프리미엄 고급 분석 기능 테스트")
    print("=" * 60)
    
    base_url = "http://localhost:8006"
    
    # 테스트 텍스트
    test_text = """
    인공지능(AI)은 기계가 인간의 지능을 모방하도록 하는 기술입니다. 
    머신러닝과 딥러닝을 통해 컴퓨터가 스스로 학습하고 판단할 수 있게 됩니다.
    자연어 처리, 컴퓨터 비전, 음성 인식 등 다양한 분야에서 활용되고 있습니다.
    """
    
    # 가상의 매치 데이터
    matches = [
        {
            "text": "인공지능은 기계가 인간의 지능을 모방하는 기술",
            "source": "위키백과",
            "similarity": 85.5,
            "startIndex": 0,
            "endIndex": 25
        },
        {
            "text": "머신러닝과 딥러닝을 통한 학습",
            "source": "나무위키", 
            "similarity": 72.3,
            "startIndex": 50,
            "endIndex": 70
        }
    ]
    
    # 1. 프리미엄 기능 목록 조회
    print("\n🎯 1. 프리미엄 기능 목록 조회")
    try:
        response = requests.get(f"{base_url}/api/premium/premium-features")
        print(f"   상태 코드: {response.status_code}")
        
        if response.status_code == 200:
            features = response.json()
            print("   ✅ 프리미엄 기능 목록 조회 성공!")
            print(f"   📊 AI 분석: {features['premium_features']['ai_analysis']['name']}")
            print(f"   💡 스마트 제안: {features['premium_features']['smart_suggestions']['name']}")
            print(f"   🎯 맥락 분석: {features['premium_features']['context_analysis']['name']}")
        else:
            print(f"   ❌ 실패: {response.text}")
    except Exception as e:
        print(f"   ❌ 에러: {e}")
    
    # 2. AI 기반 고급 분석
    print("\n🤖 2. AI 기반 고급 분석 테스트")
    try:
        payload = {"text": test_text}
        response = requests.post(
            f"{base_url}/api/premium/advanced-analysis",
            headers={"Content-Type": "application/json"},
            data=json.dumps(payload)
        )
        print(f"   상태 코드: {response.status_code}")
        
        if response.status_code == 200:
            analysis = response.json()
            print("   ✅ AI 분석 성공!")
            if 'analysis' in analysis:
                print(f"   📝 문장 수: {analysis['analysis'].get('sentence_count', 'N/A')}")
                print(f"   📏 평균 문장 길이: {analysis['analysis'].get('avg_sentence_length', 'N/A')}")
                print(f"   🧠 복잡도: {analysis['analysis'].get('complexity_score', 'N/A')}")
                print(f"   📚 학술성 점수: {analysis['analysis'].get('academic_score', 'N/A')}")
                print(f"   🎭 문체: {analysis['analysis'].get('detected_style', 'N/A')}")
                print(f"   🎵 어조: {analysis['analysis'].get('tone', 'N/A')}")
        else:
            print(f"   ❌ 실패: {response.text}")
    except Exception as e:
        print(f"   ❌ 에러: {e}")
    
    # 3. 맥락 분석
    print("\n🎯 3. 표절 맥락 분석 테스트")
    try:
        payload = {"text": test_text, "matches": matches}
        response = requests.post(
            f"{base_url}/api/premium/context-analysis",
            headers={"Content-Type": "application/json"},
            data=json.dumps(payload)
        )
        print(f"   상태 코드: {response.status_code}")
        
        if response.status_code == 200:
            context = response.json()
            print("   ✅ 맥락 분석 성공!")
            if 'context_analysis' in context:
                analysis_data = context['context_analysis']
                print(f"   ⚠️ 위험도 점수: {analysis_data.get('risk_score', 'N/A')}/10")
                print(f"   📊 위험 수준: {analysis_data.get('risk_level', 'N/A')}")
                print(f"   🔍 표절 유형: {analysis_data.get('plagiarism_types', [])}")
                print(f"   ⚖️ 법적 평가: {analysis_data.get('legal_assessment', 'N/A')}")
        else:
            print(f"   ❌ 실패: {response.text}")
    except Exception as e:
        print(f"   ❌ 에러: {e}")
    
    # 4. 개선 제안
    print("\n💡 4. 실시간 개선 제안 테스트")
    try:
        payload = {"text": test_text, "matches": matches}
        response = requests.post(
            f"{base_url}/api/premium/improvement-suggestions",
            headers={"Content-Type": "application/json"},
            data=json.dumps(payload)
        )
        print(f"   상태 코드: {response.status_code}")
        
        if response.status_code == 200:
            suggestions = response.json()
            print("   ✅ 개선 제안 성공!")
            if 'suggestions' in suggestions:
                suggestion_data = suggestions['suggestions']
                
                # 동의어 제안
                if 'synonym_suggestions' in suggestion_data:
                    print(f"   🔄 동의어 제안: {len(suggestion_data['synonym_suggestions'])}개")
                    for i, syn in enumerate(suggestion_data['synonym_suggestions'][:2]):
                        print(f"      • {syn.get('original', 'N/A')} → {syn.get('alternatives', [])}")
                
                # 문장 재구성
                if 'restructuring_suggestions' in suggestion_data:
                    print(f"   📝 재구성 제안: {len(suggestion_data['restructuring_suggestions'])}개")
                    for i, rest in enumerate(suggestion_data['restructuring_suggestions'][:1]):
                        print(f"      • 원문: {rest.get('original', 'N/A')[:50]}...")
                        print(f"      • 개선: {rest.get('improved', 'N/A')[:50]}...")
                
                # 인용 가이드
                if 'citation_guide' in suggestion_data:
                    print(f"   📚 인용 가이드: {suggestion_data['citation_guide'][:100]}...")
        else:
            print(f"   ❌ 실패: {response.text}")
    except Exception as e:
        print(f"   ❌ 에러: {e}")
    
    print("\n" + "=" * 60)
    print("✅ 프리미엄 고급 분석 기능 테스트 완료!")
    print("\n🌟 차별화 포인트:")
    print("• 🤖 AI 기반 글쓰기 스타일 자동 분석")
    print("• 🎯 단순 유사도를 넘어선 맥락 기반 위험도 평가")
    print("• 💡 구체적이고 실용적인 개선 제안")
    print("• ⚡ 실시간 작성 도움 및 피드백")

if __name__ == "__main__":
    test_premium_features()