from celery import Celery
from config import settings

# Celery 애플리케이션 생성
celery_app = Celery(
    "plagiarism_checker",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=['tasks.plagiarism_tasks', 'tasks.maintenance_tasks']
)

# Celery 설정
celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone=settings.TIMEZONE,
    enable_utc=True,
    
    # 작업 라우팅
    task_routes={
        'tasks.plagiarism_tasks.process_plagiarism_check': {'queue': 'plagiarism'},
        'tasks.plagiarism_tasks.batch_process_documents': {'queue': 'batch'},
    },
    
    # 결과 만료 시간
    result_expires=3600,
    
    # 작업자 설정
    worker_prefetch_multiplier=1,
    task_acks_late=True,
    
    # 재시도 설정
    task_reject_on_worker_lost=True,
    
    # 모니터링
    worker_send_task_events=True,
    task_send_sent_event=True,
)

# 주기적 작업 스케줄
celery_app.conf.beat_schedule = {
    'cleanup-old-results': {
        'task': 'tasks.maintenance_tasks.cleanup_old_results',
        'schedule': 3600.0,  # 1시간마다
    },
    'update-statistics': {
        'task': 'tasks.maintenance_tasks.update_daily_statistics',
        'schedule': 86400.0,  # 24시간마다
    },
}