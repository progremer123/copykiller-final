from celery_app import celery_app
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, text
from datetime import datetime, timedelta
import logging

from config import settings
from models import PlagiarismCheck, PlagiarismMatch

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 데이터베이스 연결
engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@celery_app.task
def cleanup_old_results():
    """오래된 검사 결과 정리"""
    db = SessionLocal()
    
    try:
        # 30일 이전의 검사 결과 삭제
        cutoff_date = datetime.utcnow() - timedelta(days=30)
        
        # 먼저 관련 매치들 삭제
        old_matches = db.query(PlagiarismMatch).join(PlagiarismCheck).filter(
            PlagiarismCheck.created_at < cutoff_date
        )
        match_count = old_matches.count()
        old_matches.delete(synchronize_session=False)
        
        # 그 다음 검사 결과 삭제
        old_checks = db.query(PlagiarismCheck).filter(
            PlagiarismCheck.created_at < cutoff_date
        )
        check_count = old_checks.count()
        old_checks.delete(synchronize_session=False)
        
        db.commit()
        
        logger.info(f"Cleaned up {check_count} old checks and {match_count} matches")
        
        return {
            'status': 'completed',
            'deleted_checks': check_count,
            'deleted_matches': match_count
        }
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error during cleanup: {str(e)}")
        raise e
        
    finally:
        db.close()

@celery_app.task
def update_daily_statistics():
    """일일 통계 업데이트"""
    db = SessionLocal()
    
    try:
        # 통계 업데이트 SQL 실행
        db.execute(text("SELECT update_daily_statistics()"))
        db.commit()
        
        logger.info("Daily statistics updated successfully")
        
        return {'status': 'completed', 'updated_date': datetime.utcnow().date()}
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating statistics: {str(e)}")
        raise e
        
    finally:
        db.close()

@celery_app.task
def optimize_database():
    """데이터베이스 최적화"""
    db = SessionLocal()
    
    try:
        # VACUUM과 ANALYZE 실행
        tables = ['plagiarism_checks', 'plagiarism_matches', 'document_sources', 'ngrams']
        
        for table in tables:
            db.execute(text(f"VACUUM ANALYZE {table}"))
            logger.info(f"Optimized table: {table}")
        
        db.commit()
        
        return {'status': 'completed', 'optimized_tables': tables}
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error during database optimization: {str(e)}")
        raise e
        
    finally:
        db.close()

@celery_app.task
def backup_statistics():
    """통계 데이터 백업"""
    db = SessionLocal()
    
    try:
        # 통계 데이터 조회
        stats = db.execute(text("""
            SELECT 
                COUNT(*) as total_checks,
                COUNT(*) FILTER (WHERE status = 'completed') as completed_checks,
                AVG(similarity_score) FILTER (WHERE status = 'completed') as avg_similarity,
                AVG(processing_time) FILTER (WHERE status = 'completed') as avg_processing_time
            FROM plagiarism_checks 
            WHERE created_at >= CURRENT_DATE - INTERVAL '1 day'
        """)).fetchone()
        
        backup_data = {
            'date': datetime.utcnow().date().isoformat(),
            'total_checks': stats[0] if stats else 0,
            'completed_checks': stats[1] if stats else 0,
            'avg_similarity': float(stats[2]) if stats and stats[2] else 0.0,
            'avg_processing_time': float(stats[3]) if stats and stats[3] else 0.0
        }
        
        logger.info(f"Statistics backup created: {backup_data}")
        
        return backup_data
        
    except Exception as e:
        logger.error(f"Error during statistics backup: {str(e)}")
        raise e
        
    finally:
        db.close()

@celery_app.task
def health_check():
    """시스템 헬스 체크"""
    db = SessionLocal()
    
    try:
        # 데이터베이스 연결 테스트
        db.execute(text("SELECT 1"))
        
        # 최근 검사 활동 확인
        recent_checks = db.query(PlagiarismCheck).filter(
            PlagiarismCheck.created_at >= datetime.utcnow() - timedelta(hours=1)
        ).count()
        
        # 에러 비율 확인
        error_checks = db.query(PlagiarismCheck).filter(
            PlagiarismCheck.status == 'error',
            PlagiarismCheck.created_at >= datetime.utcnow() - timedelta(hours=24)
        ).count()
        
        total_checks = db.query(PlagiarismCheck).filter(
            PlagiarismCheck.created_at >= datetime.utcnow() - timedelta(hours=24)
        ).count()
        
        error_rate = (error_checks / total_checks * 100) if total_checks > 0 else 0
        
        health_status = {
            'database_connection': 'healthy',
            'recent_activity': recent_checks,
            'error_rate_24h': round(error_rate, 2),
            'status': 'healthy' if error_rate < 5 else 'degraded',
            'timestamp': datetime.utcnow().isoformat()
        }
        
        logger.info(f"Health check completed: {health_status}")
        
        return health_status
        
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return {
            'database_connection': 'unhealthy',
            'error': str(e),
            'status': 'unhealthy',
            'timestamp': datetime.utcnow().isoformat()
        }
        
    finally:
        db.close()