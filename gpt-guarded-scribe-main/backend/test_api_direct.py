#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json

def test_api():
    """API 엔드포인트 테스트"""
    
    # 실제 과제 텍스트
    assignment_text = '''이 대통령은 "미국은 물론 자국 이익을 극대화하려고 하겠지만 그게 한국에 파멸적인 결과를 초래할 정도여서는 안 된다"고 했다.

이 대통령은 "대화가 계속되고 있으며 생각에 일부 차이가 있지만, (타결) 지연이 꼭 실패를 의미하지는 않는다"면서 "한국은 미국의 동맹이자 우방이기 때문에 우리는 모두가 받아들일 수 있는 합리적인 결과에 도달할 수 있을 것이라고 믿으며 그렇게 해야만 한다"고 밝혔다.

이 대통령 발언은 타결이 임박했다고 밝힌 도널드 트럼프 미국 대통령의 발언과는 온도차가 느껴진다. 트럼프 대통령은 지난 24일(현지 시각) 아시아 순방길에 오르면서 한미 관세 협상과 관련해 "타결(being finalized)에 매우 가깝다"며 "그들이 (타결할) 준비가 된다면, 나는 준비됐다"고 했었다.'''
    
    # API 요청
    url = "http://localhost:8002/api/v1/check/text"  # 포트 8002로 변경
    headers = {
        "Content-Type": "application/json"
    }
    data = {
        "text": assignment_text
    }
    
    print("🔍 API 표절 검사 테스트...")
    print(f"📡 요청 URL: {url}")
    print(f"📄 텍스트 길이: {len(assignment_text)}자")
    
    try:
        response = requests.post(url, headers=headers, json=data, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            print(f"\n✅ API 응답 성공!")
            print(f"📊 결과:")
            print(f"   - 검사 ID: {result.get('check_id', 'N/A')}")
            print(f"   - 상태: {result.get('status', 'N/A')}")
            print(f"   - 메시지: {result.get('message', 'N/A')}")
            
            # 결과 조회
            check_id = result.get("check_id")
            if check_id:
                print(f"\n🔍 결과 조회 중...")
                
                import time
                time.sleep(5)  # 검사 완료 대기
                
                result_url = f"http://localhost:8002/api/v1/results/{check_id}"
                result_response = requests.get(result_url)
                
                if result_response.status_code == 200:
                    final_result = result_response.json()
                    print(f"✅ 최종 결과:")
                    print(f"   - 유사도: {final_result.get('similarity_score', 0)}%")
                    print(f"   - 상태: {final_result.get('status', 'N/A')}")
                    print(f"   - 처리시간: {final_result.get('processing_time', 0):.2f}초")
                    
                    matches = final_result.get('matches', [])
                    print(f"   - 매치 수: {len(matches)}개")
                    
                    for i, match in enumerate(matches[:3], 1):
                        print(f"\n   매치 {i}:")
                        print(f"     소스: {match.get('source_title', 'N/A')}")
                        print(f"     유사도: {match.get('similarity_score', 0)}%")
                        print(f"     텍스트: {match.get('matched_text', 'N/A')[:50]}...")
                        
                else:
                    print(f"❌ 결과 조회 실패: {result_response.status_code}")
                    print(f"응답: {result_response.text}")
        
        else:
            print(f"❌ API 요청 실패: {response.status_code}")
            print(f"응답: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ 서버에 연결할 수 없습니다. 서버가 실행 중인지 확인하세요.")
    except Exception as e:
        print(f"❌ 오류: {e}")

if __name__ == "__main__":
    test_api()