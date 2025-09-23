from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List, Optional
import time
from datetime import datetime

from models import PlagiarismCheck, PlagiarismMatch, DocumentSource
from services.text_processor import TextProcessor
from services.similarity_calculator import SimilarityCalculator

class PlagiarismService:
    def __init__(self, db: Session):
        self.db = db
        self.text_processor = TextProcessor()
        self.similarity_calculator = SimilarityCalculator()
    
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
            # 텍스트 전처리
            processed_text = self.text_processor.preprocess_text(text)
            n_grams = self.text_processor.generate_ngrams(processed_text, n=5)
            
            # 유사도 계산을 위한 벡터화
            text_vector = self.similarity_calculator.vectorize_text(processed_text)
            
            # 데이터베이스에서 소스 문서들과 비교
            matches = self._find_matches(text, processed_text, text_vector, n_grams)
            
            # 전체 유사도 점수 계산
            overall_similarity = self._calculate_overall_similarity(matches)
            
            # 결과 저장
            self._save_results(check_id, matches, overall_similarity, time.time() - start_time)
            
        except Exception as e:
            # 에러 상태로 업데이트
            self._update_check_status(check_id, "error")
            print(f"Error processing plagiarism check {check_id}: {str(e)}")
    
    def _find_matches(self, original_text: str, processed_text: str, text_vector, n_grams) -> List[dict]:
        """유사한 텍스트 매치 찾기"""
        matches = []
        
        # 샘플 소스 문서들 (실제로는 데이터베이스에서 조회)
        sample_sources = [
            {
                "title": "Nature Journal 2023 - AI in Academic Research",
                "content": "Artificial intelligence has revolutionized academic research methodologies...",
                "url": "https://nature.com/articles/ai-research-2023"
            },
            {
                "title": "IEEE Computer Society - Machine Learning Applications",
                "content": "Machine learning applications in various domains have shown significant improvements...",
                "url": "https://ieee.org/ml-applications"
            },
            {
                "title": "Academic Writing Guidelines",
                "content": "Proper academic writing requires careful attention to citation and originality...",
                "url": "https://academic-guidelines.edu"
            }
        ]
        
        for source in sample_sources:
            # 실제 구현에서는 더 정교한 유사도 계산
            similarity_score = self.similarity_calculator.calculate_similarity(
                processed_text, 
                source["content"]
            )
            
            if similarity_score > 0.3:  # 30% 이상 유사한 경우
                # 매치되는 텍스트 구간 찾기
                matched_segments = self._find_matching_segments(
                    original_text, 
                    source["content"], 
                    similarity_score
                )
                
                for segment in matched_segments:
                    matches.append({
                        "matched_text": segment["text"],
                        "source_title": source["title"],
                        "source_url": source["url"],
                        "similarity_score": similarity_score * 100,
                        "start_index": segment["start"],
                        "end_index": segment["end"]
                    })
        
        return matches
    
    def _find_matching_segments(self, original_text: str, source_content: str, similarity_score: float) -> List[dict]:
        """매치되는 텍스트 구간 찾기"""
        # 간단한 구현 - 실제로는 더 정교한 알고리즘 필요
        segments = []
        words = original_text.split()
        
        # 예시: 첫 번째와 중간 부분에서 유사한 구간 생성
        if len(words) > 10:
            segments.append({
                "text": " ".join(words[5:15]),
                "start": len(" ".join(words[:5])) + 1 if len(words) > 5 else 0,
                "end": len(" ".join(words[:15]))
            })
            
            if len(words) > 20:
                segments.append({
                    "text": " ".join(words[15:25]),
                    "start": len(" ".join(words[:15])) + 1,
                    "end": len(" ".join(words[:25]))
                })
        
        return segments
    
    def _calculate_overall_similarity(self, matches: List[dict]) -> float:
        """전체 유사도 점수 계산"""
        if not matches:
            return 0.0
        
        # 가중 평균으로 전체 유사도 계산
        total_score = sum(match["similarity_score"] for match in matches)
        return min(total_score / len(matches), 100.0)
    
    def _save_results(self, check_id: str, matches: List[dict], similarity_score: float, processing_time: float):
        """결과를 데이터베이스에 저장"""
        # 검사 결과 업데이트
        check = self.db.query(PlagiarismCheck).filter(PlagiarismCheck.id == check_id).first()
        if check:
            check.similarity_score = similarity_score
            check.status = "completed"
            check.processing_time = processing_time
            check.updated_at = datetime.utcnow()
            
            # 매치 결과 저장
            for match_data in matches:
                match = PlagiarismMatch(
                    check_id=check_id,
                    matched_text=match_data["matched_text"],
                    source_text=match_data["matched_text"],  # 실제로는 원본 소스 텍스트
                    source_title=match_data["source_title"],
                    source_url=match_data["source_url"],
                    similarity_score=match_data["similarity_score"],
                    start_index=match_data["start_index"],
                    end_index=match_data["end_index"]
                )
                self.db.add(match)
            
            self.db.commit()
    
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
            # 관련 매치들도 함께 삭제
            self.db.query(PlagiarismMatch).filter(PlagiarismMatch.check_id == check_id).delete()
            self.db.delete(check)
            self.db.commit()
            return True
        return False