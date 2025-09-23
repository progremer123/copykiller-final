from celery import current_task
from celery_app import celery_app
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from typing import List, Dict
import time

from config import settings
from services.plagiarism_service import PlagiarismService
from models import PlagiarismCheck

# 데이터베이스 연결
engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@celery_app.task(bind=True, max_retries=3)
def process_plagiarism_check(self, check_id: str, text: str):
    """백그라운드에서 표절 검사 처리"""
    try:
        # 진행률 업데이트
        current_task.update_state(
            state='PROGRESS',
            meta={'current': 10, 'total': 100, 'status': '텍스트 전처리 중...'}
        )
        
        db = SessionLocal()
        service = PlagiarismService(db)
        
        # 표절 검사 실행
        service.process_plagiarism_check(check_id, text)
        
        # 완료 상태 업데이트
        current_task.update_state(
            state='SUCCESS',
            meta={'current': 100, 'total': 100, 'status': '검사 완료'}
        )
        
        db.close()
        return {'status': 'completed', 'check_id': check_id}
        
    except Exception as exc:
        # 재시도 로직
        if self.request.retries < self.max_retries:
            raise self.retry(countdown=60, exc=exc)
        
        # 최대 재시도 후 실패 처리
        db = SessionLocal()
        check = db.query(PlagiarismCheck).filter(PlagiarismCheck.id == check_id).first()
        if check:
            check.status = 'error'
            db.commit()
        db.close()
        
        current_task.update_state(
            state='FAILURE',
            meta={'error': str(exc)}
        )
        raise exc

@celery_app.task
def batch_process_documents(document_ids: List[int]):
    """여러 문서를 일괄 처리"""
    db = SessionLocal()
    
    try:
        results = []
        for doc_id in document_ids:
            # 각 문서 처리
            result = f"Document {doc_id} processed"
            results.append(result)
            time.sleep(1)  # 시뮬레이션
        
        return {'status': 'completed', 'results': results}
        
    finally:
        db.close()

@celery_app.task
def update_similarity_scores():
    """유사도 점수 재계산"""
    db = SessionLocal()
    
    try:
        # 완료된 모든 검사의 유사도 점수 재계산
        checks = db.query(PlagiarismCheck).filter(
            PlagiarismCheck.status == 'completed'
        ).all()
        
        updated_count = 0
        for check in checks:
            # 유사도 점수 재계산 로직
            # (실제로는 더 복잡한 계산)
            updated_count += 1
        
        return {'status': 'completed', 'updated_count': updated_count}
        
    finally:
        db.close()

@celery_app.task
def generate_report(check_id: str, report_type: str = 'detailed'):
    """상세 리포트 생성"""
    db = SessionLocal()
    
    try:
        service = PlagiarismService(db)
        check = service.get_check_result(check_id)
        
        if not check:
            raise ValueError(f"Check {check_id} not found")
        
        # 리포트 생성 로직
        report_data = {
            'check_id': check_id,
            'similarity_score': check.similarity_score,
            'match_count': len(check.matches),
            'report_type': report_type,
            'generated_at': time.time()
        }
        
        return report_data
        
    finally:
        db.close()