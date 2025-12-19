#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from database import get_db
from models import DocumentSource, PlagiarismCheck, PlagiarismMatch
from services.plagiarism_service import PlagiarismService
import uuid

def test_assignment_text():
    """실제 과제 텍스트로 표절 검사 테스트"""
    
    # 실제 과제 텍스트
    assignment_text = '''이 대통령은 "미국은 물론 자국 이익을 극대화하려고 하겠지만 그게 한국에 파멸적인 결과를 초래할 정도여서는 안 된다"고 했다.

이 대통령은 "대화가 계속되고 있으며 생각에 일부 차이가 있지만, (타결) 지연이 꼭 실패를 의미하지는 않는다"면서 "한국은 미국의 동맹이자 우방이기 때문에 우리는 모두가 받아들일 수 있는 합리적인 결과에 도달할 수 있을 것이라고 믿으며 그렇게 해야만 한다"고 밝혔다.

이 대통령 발언은 타결이 임박했다고 밝힌 도널드 트럼프 미국 대통령의 발언과는 온도차가 느껴진다. 트럼프 대통령은 지난 24일(현지 시각) 아시아 순방길에 오르면서 한미 관세 협상과 관련해 "타결(being finalized)에 매우 가깝다"며 "그들이 (타결할) 준비가 된다면, 나는 준비됐다"고 했었다.'''
    
    db = next(get_db())
    service = PlagiarismService(db)
    
    # 1. 데이터베이스 문서들 확인
    print("=== 데이터베이스 상태 확인 ===")
    sources = db.query(DocumentSource).filter(DocumentSource.is_active == True).all()
    print(f"활성 문서 수: {len(sources)}개")
    
    # 각 문서의 내용 미리보기
    for i, source in enumerate(sources[:3], 1):
        print(f"\n{i}. {source.title}")
        print(f"   URL: {source.url}")
        print(f"   내용 길이: {len(source.content)}자")
        print(f"   내용 미리보기: {source.content[:150]}...")
        
        # 키워드 분석
        source_words = set(source.content.lower().split())
        assignment_words = set(assignment_text.lower().split())
        common = source_words.intersection(assignment_words)
        print(f"   공통 단어 수: {len(common)}개")
        if common:
            print(f"   공통 단어: {list(common)[:10]}")
    
    print("\n=== 과제 텍스트 분석 ===")
    print(f"과제 텍스트 길이: {len(assignment_text)}자")
    assignment_words = assignment_text.lower().split()
    print(f"총 단어 수: {len(assignment_words)}개")
    print(f"고유 단어 수: {len(set(assignment_words))}개")
    print(f"주요 단어들: {assignment_words[:10]}")
    
    # 2. 표절 검사 실행
    print("\n=== 표절 검사 실행 ===")
    check_id = str(uuid.uuid4())
    
    try:
        service.process_plagiarism_check(check_id, assignment_text)
        
        # 결과 확인
        check = service.get_check_result(check_id)
        if check:
            print(f"✅ 검사 완료!")
            print(f"   상태: {check.status}")
            print(f"   유사도: {check.similarity_score}%")
            print(f"   처리 시간: {check.processing_time:.2f}초")
            
            matches = db.query(PlagiarismMatch).filter(PlagiarismMatch.check_id == check_id).all()
            print(f"   발견된 매치: {len(matches)}개")
            
            for j, match in enumerate(matches, 1):
                print(f"\n   매치 {j}:")
                print(f"     소스: {match.source_title}")
                print(f"     URL: {match.source_url}")
                print(f"     유사도: {match.similarity_score:.1f}%")
                print(f"     매치 텍스트: {match.matched_text}")
                
        else:
            print("❌ 검사 결과를 찾을 수 없습니다.")
            
    except Exception as e:
        print(f"❌ 검사 중 오류: {e}")
        import traceback
        traceback.print_exc()
    
    # 3. 수동 유사도 계산 (디버깅용)
    print("\n=== 수동 유사도 계산 ===")
    assignment_words_set = set(assignment_text.lower().split())
    
    for i, source in enumerate(sources[:5], 1):
        source_words_set = set(source.content.lower().split())
        common_words = assignment_words_set.intersection(source_words_set)
        
        if len(common_words) > 0:
            similarity = len(common_words) / len(assignment_words_set) * 100
            print(f"{i}. {source.title[:40]}...")
            print(f"   공통 단어: {len(common_words)}개")
            print(f"   유사도: {similarity:.1f}%")
            print(f"   주요 공통 단어: {list(common_words)[:5]}")
        else:
            print(f"{i}. {source.title[:40]}... - 공통 단어 없음")

if __name__ == "__main__":
    test_assignment_text()