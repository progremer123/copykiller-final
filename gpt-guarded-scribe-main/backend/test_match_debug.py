import requests
import json
import time

# API 테스트
text = "정 부패 사례는 2025년 6월에 발생한 YES24 컨설팅에 공격입니다. 사건 개요: 2025년 6월 9일 새벽, 해커의 랜섬웨어 공격으로 인해 YES24의 홈페이지, 앱, eBook 등 핵심 서비스가 전면 중단되는 사태가 발생했습니다."

print("=== API 테스트 시작 ===")
response = requests.post('http://localhost:8006/api/plagiarism/check/text', json={'text': text})
print(f"Status: {response.status_code}")

if response.status_code == 200:
    result = response.json()
    check_id = result.get('check_id')
    print(f"Check ID: {check_id}")
    
    # 결과 조회
    print("3초 대기 중...")
    time.sleep(3)
    
    result_response = requests.get(f'http://localhost:8006/api/plagiarism/check/{check_id}')
    if result_response.status_code == 200:
        final_result = result_response.json()
        print(f"Similarity: {final_result.get('similarity_score')}%")
        
        matches = final_result.get('matches', [])
        print(f"Matches count: {len(matches)}")
        
        for i, match in enumerate(matches[:5]):
            matched_text = match.get('matched_text', '')
            match_type = match.get('match_type', '')
            start_idx = match.get('start_index')
            end_idx = match.get('end_index')
            
            print(f"\n--- Match {i+1} ---")
            print(f"Text: {matched_text[:80]}...")
            print(f"Type: {match_type}")
            print(f"Indices: {start_idx}-{end_idx}")
            print(f"Length: {len(matched_text)}")
            
            # 원본 텍스트에서 해당 위치 확인
            if start_idx is not None and end_idx is not None:
                extracted = text[start_idx:end_idx]
                print(f"Extracted: {extracted[:80]}...")
                print(f"Match OK: {extracted.lower() == matched_text.lower()}")
    else:
        print(f"Result error: {result_response.text}")
else:
    print(f"Error: {response.text}")