#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from database import get_db
from models import DocumentSource, PlagiarismCheck, PlagiarismMatch
from services.plagiarism_service import PlagiarismService
import uuid

def test_real_assignment():
    """실제 과제 텍스트로 표절 검사 테스트"""
    
    db = next(get_db())
    service = PlagiarismService(db)
    
    # 1. 현재 데이터베이스 상태 확인
    print("=== 데이터베이스 현재 상태 ===")
    sources = db.query(DocumentSource).filter(DocumentSource.is_active == True).all()
    print(f"활성 문서 수: {len(sources)}개")
    
    for i, source in enumerate(sources[:5], 1):
        print(f"{i}. {source.title[:50]}... ({len(source.content)}자)")
        print(f"   내용 미리보기: {source.content[:100]}...")
        print()
    
    # 2. 실제 과제와 유사한 텍스트 테스트
    test_texts = [
        # 일반적인 과제 텍스트
        "인공지능은 현대 사회에서 매우 중요한 기술이다. 머신러닝과 딥러닝 기술의 발전으로 인해 많은 분야에서 혁신이 일어나고 있다. 특히 자연어 처리, 컴퓨터 비전, 로보틱스 등의 분야에서 큰 발전을 보이고 있다.",
        
        # 기후변화 관련 텍스트
        "기후변화는 지구의 기온 상승으로 인해 발생하는 환경 문제이다. 온실가스의 증가가 주요 원인이며, 이로 인해 해수면 상승, 극한 기후 현상 등이 발생하고 있다. 전 세계적으로 탄소 중립을 위한 노력이 필요하다.",
        
        # 완전히 다른 주제
        "요리는 인간의 기본적인 생활 기술 중 하나이다. 다양한 재료를 조합하여 맛있는 음식을 만드는 과정은 창의성을 발휘할 수 있는 좋은 방법이다. 건강한 식단을 유지하기 위해서는 균형 잡힌 영양소 섭취가 중요하다."
    ]
    
    # 3. 각 텍스트로 테스트
    for i, text in enumerate(test_texts, 1):
        print(f"\n=== 테스트 {i}: {text[:30]}... ===")
        
        check_id = str(uuid.uuid4())
        
        # 직접 표절 검사 실행
        try:
            service.process_plagiarism_check(check_id, text)
            
            # 결과 확인
            check = service.get_check_result(check_id)
            if check:
                print(f"✅ 검사 완료: {check.similarity_score:.1f}%")
                
                matches = db.query(PlagiarismMatch).filter(PlagiarismMatch.check_id == check_id).all()
                print(f"📊 발견된 매치: {len(matches)}개")
                
                for j, match in enumerate(matches, 1):
                    print(f"  {j}. {match.source_title[:40]}... - {match.similarity_score:.1f}%")
                    print(f"     매치 텍스트: {match.matched_text[:60]}...")
                
            else:
                print("❌ 검사 결과를 찾을 수 없습니다.")
                
        except Exception as e:
            print(f"❌ 검사 중 오류: {e}")
            import traceback
            traceback.print_exc()
    
    # 4. 데이터베이스 문서 내용 샘플 확인
    print("\n=== 데이터베이스 문서 내용 샘플 ===")
    if sources:
        sample_source = sources[0]
        print(f"샘플 문서: {sample_source.title}")
        print(f"URL: {sample_source.url}")
        print(f"내용 (첫 200자): {sample_source.content[:200]}...")
        
        # 샘플 문서의 키워드 분석
        words = sample_source.content.lower().split()
        unique_words = set(words)
        print(f"총 단어 수: {len(words)}, 고유 단어 수: {len(unique_words)}")
        
        # 빈도가 높은 단어들
        from collections import Counter
        word_count = Counter(words)
        common_words = word_count.most_common(10)
        print("빈도 높은 단어들:", [word for word, count in common_words if len(word) >= 2])

if __name__ == "__main__":
    test_real_assignment()