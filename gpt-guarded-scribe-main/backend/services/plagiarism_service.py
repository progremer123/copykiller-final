from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List, Optional
import time
from datetime import datetime

# DocumentSource 모델을 import 해야 합니다.
from models import PlagiarismCheck, PlagiarismMatch, DocumentSource
from services.text_processor import TextProcessor
from services.similarity_calculator import SimilarityCalculator
from services.web_crawler_service import WebCrawlerService
from services.ai_analysis_service import AIAnalysisService, PlagiarismContextAnalyzer
from services.realtime_improvement_service import RealTimeImprovementService

class PlagiarismService:
    def __init__(self, db: Session):
        self.db = db
        self.text_processor = TextProcessor()
        self.similarity_calculator = SimilarityCalculator()
        self.web_crawler = WebCrawlerService()
        self.ai_analysis = AIAnalysisService()
        self.context_analyzer = PlagiarismContextAnalyzer()
        self.improvement_service = RealTimeImprovementService()

    def create_check(self, check_id: str, text: str, file_name: str = None, file_type: str = None) -> PlagiarismCheck:
        """새로운 표절 검사 생성"""
        check = PlagiarismCheck(
            id=check_id,
            original_text=text,
            file_name=file_name,
            file_type=file_type,
            status="checking"
        )
        self.db.add(check)
        self.db.commit()
        return check

    def process_plagiarism_check(self, check_id: str, text: str):
        """표절 검사 처리 (백그라운드 작업)"""
        start_time = time.time()
        
        try:
            print(f"[*] 표절 검사 시작: {check_id}")
            print(f"[*] 입력 텍스트: {text[:50]}...")
            
            # 검사 객체가 없으면 생성
            existing_check = self.db.query(PlagiarismCheck).filter(PlagiarismCheck.id == check_id).first()
            if not existing_check:
                print(f"[NEW] 새 검사 객체 생성: {check_id}")
                check = PlagiarismCheck(
                    id=check_id,
                    original_text=text,
                    status="checking"
                )
                self.db.add(check)
                self.db.commit()
            
            # 데이터베이스 연결 확인
            source_count = self.db.query(DocumentSource).filter(DocumentSource.is_active == True).count()
            print(f"[DB] 활성 문서 수: {source_count}개")
            
            # 웹 크롤링으로 추가 데이터 수집 (비동기 처리로 개선)
            if source_count < 50:  # 문서가 적으면 백그라운드에서 크롤링
                self._schedule_background_crawling(text)
            
            if source_count == 0:
                print("[!] 데이터베이스에 비교할 문서가 없습니다! 기본 데이터 생성...")
                # 기본 데이터 몇 개 생성
                self._create_sample_data()
                # source_count 다시 확인
                source_count = self.db.query(DocumentSource).filter(DocumentSource.is_active == True).count()
                print(f"[DB] 기본 데이터 생성 후: {source_count}개")
            
            processed_text = self.text_processor.preprocess_text(text)
            n_grams = self.text_processor.generate_ngrams(processed_text, n=5)
            
            print(f"[*] 텍스트 전처리 완료, 데이터베이스 검색 중...")
            
            matches = self._find_matches(text, processed_text, n_grams)
            
            overall_similarity = self._calculate_overall_similarity(matches)
            
            print(f"[OK] 검사 완료: 유사도 {overall_similarity:.1f}%, 매치 {len(matches)}개")
            
            self._save_results(check_id, matches, overall_similarity, time.time() - start_time)
            
        except Exception as e:
            print(f"[ERROR] 표절 검사 오류 {check_id}: {str(e)}")
            import traceback
            traceback.print_exc()
            self._update_check_status(check_id, "error")
    
    def _crawl_additional_data(self, text: str):
        """텍스트 내용 기반으로 추가 웹 크롤링"""
        print("[*] 웹 크롤링을 통한 추가 데이터 수집...")
        
        # 텍스트에서 키워드 추출 (간단한 방법)
        words = text.split()
        keywords = []
        
        # 한글 키워드만 추출 (길이 2자 이상)
        for word in words:
            clean_word = word.strip('.,!?()[]{}":;')
            if len(clean_word) >= 2 and any('\u3131' <= char <= '\u318E' or '\uAC00' <= char <= '\uD7A3' for char in clean_word):
                keywords.append(clean_word)
        
        # 상위 3개 키워드로 크롤링
        top_keywords = keywords[:3] if keywords else ["일반", "정보", "내용"]
        
        for keyword in top_keywords:
            try:
                print(f"[*] 키워드 '{keyword}'로 크롤링 중...")
                result = self.web_crawler.crawl_and_save(keyword, 2)  # 키워드당 2개 문서
                print(f"[OK] '{keyword}' 크롤링 결과: {result['saved_count']}개 저장")
            except Exception as e:
                print(f"[ERROR] '{keyword}' 크롤링 오류: {e}")

    def _find_matches(self, original_text: str, processed_text: str, n_grams) -> List[dict]:
        """스마트 유사도 검사 - 간단한 키워드 기반 매칭"""
        matches = []
        all_sources = self.db.query(DocumentSource).filter(DocumentSource.is_active == True).all()
        
        print(f"[DB] 검색 대상 문서 수: {len(all_sources)}개")
        
        # 텍스트 정규화: 여러 공백, 줄바꿈을 단일 공백으로 변환
        normalized_original = ' '.join(original_text.split())
        normalized_original_lower = normalized_original.lower()
        
        # 입력 텍스트에서 주요 단어 추출 (2자 이상, 숫자 제외)
        original_words = [w.lower() for w in normalized_original.split() 
                         if len(w) >= 2 and not w.isdigit()]
        original_word_set = set(original_words)
        
        print(f"[*] 추출된 단어 수: {len(original_word_set)}개 (예: {list(original_word_set)[:5]}...)")
        
        for source in all_sources:
            print(f"[*] '{source.title}' 검사 중...")
            
            # 소스 텍스트 정규화
            normalized_source = ' '.join(source.content.split()).lower()
            source_words = set(w.lower() for w in normalized_source.split() 
                              if len(w) >= 2 and not w.isdigit())
            
            # 공통 단어 찾기
            common_words = original_word_set.intersection(source_words)
            
            print(f"   공통 단어: {len(common_words)}개")
            
            if len(common_words) > 0:
                # 유사도 계산 (Jaccard 유사도)
                union_size = len(original_word_set.union(source_words))
                similarity = (len(common_words) / union_size * 100) if union_size > 0 else 0
                
                # 추가 유사도 계산: 공통 단어 비율
                common_ratio = len(common_words) / len(original_word_set) * 100 if original_word_set else 0
                
                print(f"   계산된 유사도: {similarity:.1f}% (비율: {common_ratio:.1f}%)")
                
                # 최소 유사도 2% 이상이거나 공통 단어 2개 이상이면 매치로 인정
                if similarity >= 2 or len(common_words) >= 2:
                    # 공통 단어로 매치 생성
                    matched_text = " ".join(sorted(list(common_words))[:15])  # 상위 15개 단어
                    
                    # 원본 텍스트에서 공통 단어의 위치 찾기
                    text_lower = original_text.lower()
                    first_match_pos = 0
                    for word in common_words:
                        pos = text_lower.find(word.lower())
                        if pos >= 0:
                            first_match_pos = pos
                            break
                    
                    # 최종 유사도: Jaccard 유사도 + 공통 단어 보너스
                    final_similarity = min(similarity + (len(common_words) * 2), 95)
                    
                    matches.append({
                        "matched_text": matched_text,
                        "source_title": source.title,
                        "source_url": source.url,
                        "similarity_score": final_similarity,
                        "start_index": first_match_pos,
                        "end_index": first_match_pos + len(matched_text),
                        "match_type": "keyword"
                    })
                    print(f"[OK] 매치 발견: {final_similarity:.1f}% - 공통단어: {len(common_words)}개")
                else:
                    print(f"   유사도 낮음 (임계값 미달)")
            else:
                print(f"   공통 단어 없음")
        
        print(f"[RESULT] 총 {len(matches)}개의 매치 발견")
        return matches

    def _find_matching_segments(self, original_text: str, source_content: str, similarity_score: float) -> List[dict]:
        """매치되는 텍스트 구간 찾기 - 간소화된 버전"""
        return [{
            "text": original_text[:50] + "..." if len(original_text) > 50 else original_text,
            "start": 0,
            "end": min(50, len(original_text))
        }]


    def _calculate_overall_similarity(self, matches: List[dict]) -> float:
        """전체 유사도 점수 계산 - 개선된 알고리즘"""
        if not matches:
            return 0.0
        
        # 단순하게: 매치들의 유사도 점수 평균
        avg_similarity = sum(match.get("similarity_score", 0) for match in matches) / len(matches)
        
        # 매치 개수가 많을수록 신뢰도 높음 (가중치)
        match_count_bonus = min(len(matches) * 2, 15)  # 최대 +15%
        
        # 최종 유사도
        overall_similarity = avg_similarity + match_count_bonus
        
        # 범위 제한
        overall_similarity = max(0.0, min(overall_similarity, 95.0))
        
        print(f"[CALC] 유사도: {avg_similarity:.1f}% (평균) + {match_count_bonus:.1f}% (보너스) = {overall_similarity:.1f}%")
        
        return overall_similarity

    def _save_results(self, check_id: str, matches: List[dict], similarity_score: float, processing_time: float):
        """결과를 데이터베이스에 저장"""
        print(f"[SAVE] 결과 저장 중: check_id={check_id}, 유사도={similarity_score}%, 매치={len(matches)}개")
        
        check = self.db.query(PlagiarismCheck).filter(PlagiarismCheck.id == check_id).first()
        if check:
            print(f"[OK] 검사 객체 발견: {check.id}")
            check.similarity_score = similarity_score
            check.status = "completed"
            check.processing_time = processing_time
            check.updated_at = datetime.utcnow()
            
            for i, match_data in enumerate(matches, 1):
                print(f"[*] 매치 {i} 저장 중: {match_data['source_title'][:30]}...")
                match = PlagiarismMatch(
                    check_id=check_id,
                    matched_text=match_data["matched_text"],
                    source_text=match_data["matched_text"],
                    source_title=match_data["source_title"],
                    source_url=match_data["source_url"],
                    similarity_score=match_data["similarity_score"],
                    start_index=match_data["start_index"],
                    end_index=match_data["end_index"]
                )
                self.db.add(match)
            
            self.db.commit()
            print(f"[OK] 저장 완료!")
        else:
            print(f"[ERROR] 검사 객체를 찾을 수 없음: {check_id}")
            # 새로운 검사 객체 생성
            check = PlagiarismCheck(
                id=check_id,
                original_text="",  # 원본 텍스트가 없을 경우
                similarity_score=similarity_score,
                status="completed",
                processing_time=processing_time,
                updated_at=datetime.utcnow()
            )
            self.db.add(check)
            
            for match_data in matches:
                match = PlagiarismMatch(
                    check_id=check_id,
                    matched_text=match_data["matched_text"],
                    source_text=match_data["matched_text"],
                    source_title=match_data["source_title"],
                    source_url=match_data["source_url"],
                    similarity_score=match_data["similarity_score"],
                    start_index=match_data["start_index"],
                    end_index=match_data["end_index"]
                )
                self.db.add(match)
            
            self.db.commit()
            print(f"[OK] 새 객체 생성 후 저장 완료!")

    def _update_check_status(self, check_id: str, status: str):
        """검사 상태 업데이트"""
        check = self.db.query(PlagiarismCheck).filter(PlagiarismCheck.id == check_id).first()
        if check:
            check.status = status
            check.updated_at = datetime.utcnow()
            self.db.commit()

    def get_check_result(self, check_id: str) -> Optional[PlagiarismCheck]:
        """검사 결과 조회"""
        return self.db.query(PlagiarismCheck).filter(PlagiarismCheck.id == check_id).first()

    def get_check_history(self, limit: int = 10, offset: int = 0) -> List[PlagiarismCheck]:
        """검사 이력 조회"""
        return (
            self.db.query(PlagiarismCheck)
            .order_by(desc(PlagiarismCheck.created_at))
            .offset(offset)
            .limit(limit)
            .all()
        )

    def delete_check(self, check_id: str) -> bool:
        """검사 결과 삭제"""
        check = self.db.query(PlagiarismCheck).filter(PlagiarismCheck.id == check_id).first()
        if check:
            self.db.query(PlagiarismMatch).filter(PlagiarismMatch.check_id == check_id).delete()
            self.db.delete(check)
            self.db.commit()
            return True
        return False

    def _create_sample_data(self):
        """기본 샘플 데이터 생성"""
        sample_documents = [
            {
                "title": "인공지능 개요",
                "content": "인공지능은 현대 기술의 핵심입니다. 머신러닝과 딥러닝을 통해 컴퓨터가 학습하고 판단할 수 있게 됩니다. 자연어 처리, 이미지 인식, 음성 인식 등 다양한 분야에 활용되고 있습니다.",
                "source_type": "academic",
                "url": "sample_ai_overview"
            },
            {
                "title": "머신러닝 기초",
                "content": "머신러닝은 인공지능의 한 분야로, 데이터로부터 패턴을 학습하는 기술입니다. 지도학습, 비지도학습, 강화학습으로 분류할 수 있으며, 각각 다른 접근 방법을 사용합니다.",
                "source_type": "academic",
                "url": "sample_ml_basics"
            },
            {
                "title": "자연어 처리 기술",
                "content": "자연어 처리는 컴퓨터가 인간의 언어를 이해하고 처리하는 기술입니다. 형태소 분석, 구문 분석, 의미 분석 등의 단계를 거쳐 텍스트 데이터를 처리합니다.",
                "source_type": "academic",
                "url": "sample_nlp"
            },
            {
                "title": "딥러닝 응용",
                "content": "딥러닝은 심층 신경망을 사용하는 머신러닝 기법입니다. 이미지 분류, 객체 검출, 언어 모델 등 다양한 분야에서 뛰어난 성능을 보여주고 있습니다.",
                "source_type": "academic",
                "url": "sample_deep_learning"
            }
        ]
        
        for doc_data in sample_documents:
            # 이미 존재하는지 확인
            existing = self.db.query(DocumentSource).filter(DocumentSource.url == doc_data["url"]).first()
            if not existing:
                doc = DocumentSource(
                    title=doc_data["title"],
                    content=doc_data["content"],
                    source_type=doc_data["source_type"],
                    url=doc_data["url"],
                    is_active=True
                )
                self.db.add(doc)
        
        self.db.commit()
        print("[OK] 기본 샘플 데이터 생성 완료")

    def _schedule_background_crawling(self, text: str):
        """스마트 백그라운드 웹 크롤링 스케줄링"""
        import threading
        from datetime import datetime, timedelta
        
        # 최근 1시간 내에 크롤링했는지 확인 (중복 방지)
        cache_key = f"crawl_cache_{hash(text[:100])}"  # 텍스트 앞부분으로 캐시 키 생성
        
        def background_crawl():
            try:
                print("[*] 스마트 백그라운드 크롤링 시작...")
                
                # 현재 데이터베이스 상태 확인
                current_count = self.db.query(DocumentSource).filter(DocumentSource.is_active == True).count()
                print(f"[*] 현재 데이터베이스: {current_count}개 문서")
                
                if current_count < 100:  # 100개 미만일 때만 크롤링
                    self._crawl_additional_data_optimized(text)
                    
                    # 크롤링 후 상태 확인
                    new_count = self.db.query(DocumentSource).filter(DocumentSource.is_active == True).count()
                    added = new_count - current_count
                    print(f"[OK] 백그라운드 크롤링 완료: {added}개 추가됨 (총 {new_count}개)")
                else:
                    print("[*] 충분한 데이터가 있어 크롤링 생략")
                    
            except Exception as e:
                print(f"[ERROR] 백그라운드 크롤링 오류: {e}")
        
        # 별도 스레드에서 실행 (메인 응답에 영향 없음)
        thread = threading.Thread(target=background_crawl, daemon=True)
        thread.start()
        print("[*] 스마트 백그라운드 크롤링 스케줄됨 (응답 지연 없음)")

    def _crawl_additional_data_optimized(self, text: str):
        """최적화된 웹 크롤링 (백그라운드용)"""
        # 텍스트에서 키워드 추출 (개선된 방법)
        import re
        from collections import Counter
        
        # 한글 명사만 추출 (2-5글자)
        korean_words = re.findall(r'[가-힣]{2,5}', text)
        
        # 불용어 제거 (확장된 목록)
        stop_words = {
            '이것', '그것', '저것', '하나', '때문', '이런', '그런', '저런', '있는', '없는', '같은', '다른',
            '것을', '것이', '것은', '이를', '이는', '그를', '그는', '저를', '저는', '할수', '있게', '되는',
            '하는', '되고', '있다', '있고', '없고', '같이', '처럼', '정도', '부분', '경우', '때와', '경우',
            '사람', '여자', '남자', '아이', '학생', '선생', '이번', '다음', '저번', '지난', '올해', '작년'
        }
        korean_words = [word for word in korean_words if word not in stop_words and len(word) >= 2]
        
        # 빈도 기준으로 키워드 선택 (조건 완화)
        word_freq = Counter(korean_words)
        
        # 빈도가 높은 단어 우선, 없으면 길이가 긴 단어 선택
        frequent_words = [word for word, count in word_freq.most_common(5) if count >= 2]
        unique_words = [word for word, count in word_freq.most_common(10) if count == 1 and len(word) >= 3]
        
        # 최종 키워드 선택 (빈도 높은 단어 + 긴 단어)
        top_keywords = frequent_words[:2] + unique_words[:2]
        top_keywords = list(set(top_keywords))[:3]  # 중복 제거 및 3개 제한
        
        if not top_keywords:
            # 마지막 fallback: 텍스트에서 가장 긴 단어들 선택
            top_keywords = sorted(set(korean_words), key=len, reverse=True)[:3]
        
        if not top_keywords:
            top_keywords = ["정보", "기술", "사회"]  # 범용적인 기본 키워드
        
        print(f"🔍 선택된 키워드: {top_keywords}")
        print(f"📝 원본 텍스트 미리보기: {text[:50]}...")
        
        for keyword in top_keywords:
            try:
                print(f"[*] '{keyword}' 크롤링 중...")
                result = self.web_crawler.crawl_and_save(keyword, 3)  # 키워드당 3개 문서
                print(f"[OK] '{keyword}' 크롤링 완료: {result.get('saved_count', 0)}개 저장")
                
                # 각 키워드마다 1초 대기 (서버 부하 방지)
                import time
                time.sleep(1)
                
            except Exception as e:
                print(f"[ERROR] '{keyword}' 크롤링 오류: {e}")
                continue

    def get_database_stats(self) -> dict:
        """데이터베이스 통계 정보"""
        try:
            total_docs = self.db.query(DocumentSource).filter(DocumentSource.is_active == True).count()
            
            # 소스별 통계
            wikipedia_count = self.db.query(DocumentSource).filter(
                DocumentSource.is_active == True,
                DocumentSource.source_type == 'wikipedia'
            ).count()
            
            namuwiki_count = self.db.query(DocumentSource).filter(
                DocumentSource.is_active == True, 
                DocumentSource.source_type == 'namuwiki'
            ).count()
            
            academic_count = self.db.query(DocumentSource).filter(
                DocumentSource.is_active == True,
                DocumentSource.source_type == 'academic'
            ).count()
            
            return {
                "total_documents": total_docs,
                "sources": {
                    "wikipedia": wikipedia_count,
                    "namuwiki": namuwiki_count,
                    "academic": academic_count
                },
                "status": "healthy" if total_docs > 20 else "needs_more_data"
            }
        except Exception as e:
            return {
                "error": str(e),
                "status": "error"
            }

    def cleanup_old_data(self, days_old: int = 30):
        """오래된 데이터 정리"""
        from datetime import datetime, timedelta
        
        cutoff_date = datetime.now() - timedelta(days=days_old)
        
        # 오래된 검사 결과 삭제
        old_checks = self.db.query(PlagiarismCheck).filter(
            PlagiarismCheck.created_at < cutoff_date
        ).all()
        
        deleted_count = 0
        for check in old_checks:
            # 관련 매치 먼저 삭제
            self.db.query(PlagiarismMatch).filter(PlagiarismMatch.check_id == check.id).delete()
            self.db.delete(check)
            deleted_count += 1
        
        self.db.commit()
        print(f"[*] {deleted_count}개의 오래된 검사 결과 정리 완료")
        
        return deleted_count

    def _check_sentence_similarity(self, original_sentences: List[str], source_content: str, source) -> List[dict]:
        """문장 단위 유사도 검사"""
        matches = []
        source_sentences = [s.strip() for s in source_content.split('.') if s.strip()]
        original_full_text = '. '.join(original_sentences)  # 원본 전체 텍스트 복원
        
        for orig_sentence in original_sentences:
            if len(orig_sentence) < 10:  # 너무 짧은 문장 제외
                continue
                
            orig_words = set(orig_sentence.lower().split())
            
            for src_sentence in source_sentences:
                if len(src_sentence) < 10:
                    continue
                    
                src_words = set(src_sentence.lower().split())
                common_words = orig_words.intersection(src_words)
                
                # 공통 단어가 2개 이상이고, 원문의 30% 이상일 때 (더 관대한 조건)
                if len(common_words) >= 2 and len(common_words) / len(orig_words) >= 0.3:
                    # 더 보수적인 유사도 계산
                    word_ratio = len(common_words) / len(orig_words)
                    similarity = (word_ratio * 70) + (len(common_words) * 2)  # 최대 80점 정도
                    similarity = min(similarity, 80)  # 문장 매칭 최대 80%
                    
                    # 원본 전체 텍스트에서 이 문장의 위치 찾기
                    start_pos = original_full_text.lower().find(orig_sentence.lower())
                    if start_pos >= 0:
                        matches.append({
                            "matched_text": orig_sentence,
                            "source_title": source.title,
                            "source_url": source.url,
                            "similarity_score": similarity,
                            "start_index": start_pos,
                            "end_index": start_pos + len(orig_sentence),
                            "match_type": "sentence"
                        })
                        print(f"[*] 문장 매치: {similarity:.1f}% - {orig_sentence[:50]}...")
                        break
        
        return matches

    def _check_phrase_similarity(self, original_text: str, source_content: str, source) -> List[dict]:
        """구문 단위 유사도 검사 (3-7 단어)"""
        matches = []
        words = original_text.split()
        
        # 2-7단어 구문 생성 (더 많은 매치 찾기)
        for length in range(2, 8):
            for i in range(len(words) - length + 1):
                phrase = ' '.join(words[i:i+length])
                
                # 소스에서 유사한 구문 찾기
                if phrase.lower() in source_content.lower():
                    start_pos = original_text.lower().find(phrase.lower())
                    if start_pos >= 0:
                        # 더 보수적인 구문 점수 계산
                        base_score = 30 + (length * 5)  # 2단어=40점, 3단어=45점, 7단어=65점
                        phrase_score = min(base_score, 75)  # 최대 75%
                        # 원본 텍스트에서 정확한 위치 찾기
                        actual_start = original_text.find(phrase)
                        if actual_start == -1:
                            # 정확한 매치를 찾지 못한 경우 근사치 사용
                            actual_start = start_pos
                            actual_end = start_pos + len(phrase)
                        else:
                            actual_end = actual_start + len(phrase)
                        
                        matches.append({
                            "matched_text": phrase,
                            "source_title": source.title,
                            "source_url": source.url,
                            "similarity_score": phrase_score,
                            "start_index": actual_start,
                            "end_index": actual_end,
                            "match_type": "phrase"
                        })
                        print(f"[*] 구문 매치: {85 + (length * 2)}% - {phrase[:40]}...")
        
        return matches

    def _check_keyword_similarity(self, original_words: List[str], source_content: str, source) -> List[dict]:
        """키워드 기반 유사도 검사"""
        matches = []
        original_text = ' '.join(original_words)  # 원본 텍스트 복원
        
        # 의미있는 단어만 추출 (2글자 이상 한글, 3글자 이상 영문)
        meaningful_words = []
        for word in original_words:
            clean_word = word.strip('.,!?()[]{}":;')
            if len(clean_word) >= 2:
                # 한글 또는 영문 체크
                if any('\uAC00' <= char <= '\uD7A3' for char in clean_word) or \
                   (clean_word.isalpha() and len(clean_word) >= 3):
                    meaningful_words.append(clean_word)
        
        if not meaningful_words:
            return matches
        
        # 소스에서 키워드 매치 확인
        source_lower = source_content.lower()
        matched_keywords = []
        keyword_positions = []
        
        for word in meaningful_words:
            if word.lower() in source_lower:
                matched_keywords.append(word)
                # 원본 텍스트에서 이 키워드의 위치 찾기
                pos = original_text.lower().find(word.lower())
                if pos >= 0:
                    keyword_positions.append({
                        "word": word,
                        "start": pos,
                        "end": pos + len(word)
                    })
        
        # 매치된 키워드가 충분히 많으면 유사 판정
        match_ratio = len(matched_keywords) / len(meaningful_words)
        
        if match_ratio >= 0.3 and len(matched_keywords) >= 2:  # 30% 이상, 최소 2개
            # 키워드 매칭은 낮은 점수
            similarity = min(match_ratio * 40, 50)  # 최대 50%
            
            # 각 매치된 키워드에 대해 개별 매치 생성
            for kw_pos in keyword_positions[:5]:  # 최대 5개 키워드만
                matches.append({
                    "matched_text": kw_pos["word"],
                    "source_title": source.title,
                    "source_url": source.url,
                    "similarity_score": similarity,
                    "start_index": kw_pos["start"],
                    "end_index": kw_pos["end"],
                    "match_type": "keyword"
                })
            
            print(f"[*] 키워드 매치: {similarity:.1f}% - {len(matched_keywords)}개 키워드")
        seen = set()
        
        for match in sorted_matches:
            key = f"{match['source_title']}_{match['start_index']//20}"  # 20글자 단위로 그룹핑 (덜 엄격)
            if key not in seen:
                unique_matches.append(match)
                seen.add(key)
        
        # 상위 20개까지 반환 (더 많은 매치 표시)
        return unique_matches[:20]