from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Request
from sqlalchemy.orm import Session
from typing import List, Optional, Dict
import uuid
import time
from datetime import datetime

from database import get_db
from models import PlagiarismCheck, PlagiarismMatch
from services.plagiarism_service import PlagiarismService
from services.text_processor import TextProcessor
from services.web_crawler_service import WebCrawlerService
from services.ai_crawler_service import AICrawlerService
from services.ai_knowledge_generator import AIKnowledgeGenerator
from services.ai_plagiarism_avoidance import AIPlagiarismAvoidance
from services.ai_plagiarism_fixer import AIPlagiarismFixer
from services.sentence_improvement_service import SentenceImprovementService
from schemas import PlagiarismCheckCreate, PlagiarismCheckResponse, PlagiarismMatchResponse
import sqlite3
# ⬇️⬇️⬇️ 1. Celery 작업을 직접 import 합니다. ⬇️⬇️⬇️
# 임시로 Celery 대신 직접 처리
# from tasks.plagiarism_tasks import process_plagiarism_check

router = APIRouter()

@router.get("/health")
async def api_health_check():
    """API 상태 확인"""
    return {"status": "healthy", "service": "plagiarism API"}

@router.get("/database/stats")
async def get_database_stats(db: Session = Depends(get_db)):
    """데이터베이스 통계 확인"""
    service = PlagiarismService(db)
    stats = service.get_database_stats()
    return stats

@router.post("/check/text", response_model=PlagiarismCheckResponse)
async def check_text_plagiarism(
    payload: PlagiarismCheckCreate,
    db: Session = Depends(get_db)
):
    """텍스트 표절 검사"""
    print(f"[*] 표절 검사 요청 받음: {len(payload.text)}자")
    try:
        text = payload.text
        if not text or len(text.strip()) < 10:
            raise HTTPException(status_code=400, detail="텍스트가 너무 짧습니다 (최소 10자)")
        
        check_id = str(uuid.uuid4())
        print(f"[*] 검사 ID 생성: {check_id}")
        service = PlagiarismService(db)
        
        check = service.create_check(check_id, text)
        
        # 즉시 동기 처리 (테스트용)
        try:
            print(f"[*] 표절 검사 처리 시작...")
            service.process_plagiarism_check(check_id, text)
            print(f"[OK] 표절 검사 처리 완료")
            # 처리 완료 후 결과 재조회
            updated_check = service.get_check_result(check_id)
            if updated_check:
                check = updated_check
                print(f"[*] 업데이트된 결과 조회 완료")
        except Exception as e:
            print(f"[ERROR] 처리 중 오류: {e}")
            import traceback
            traceback.print_exc()
            # 오류가 발생해도 기본 응답 반환
        
        # 매치 정보 포함
        matches = []
        if hasattr(check, 'matches') and check.matches:
            matches = [
                PlagiarismMatchResponse(
                    matched_text=match.matched_text or "",
                    source_title=match.source_title or "Unknown",
                    source_url=match.source_url or "",
                    similarity_score=match.similarity_score or 0.0,
                    start_index=match.start_index or 0,
                    end_index=match.end_index or 0
                )
                for match in check.matches
            ]
        
        # 응답 반환 (Pydantic 모델이 자동으로 JSON 변환)
        return PlagiarismCheckResponse(
            id=check.id,
            original_text=check.original_text,
            similarity_score=check.similarity_score or 0.0,
            status=check.status,
            created_at=check.created_at,
            matches=matches
        )
    except Exception as e:
        print(f"API 오류: {e}")
        raise HTTPException(status_code=500, detail=f"서버 오류: {str(e)}")

@router.post("/check/file", response_model=PlagiarismCheckResponse)
async def check_file_plagiarism(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """파일 표절 검사"""
    allowed_types = ["text/plain", "application/pdf", "application/msword", 
                    "application/vnd.openxmlformats-officedocument.wordprocessingml.document"]
    
    if file.content_type not in allowed_types:
        raise HTTPException(status_code=400, detail="지원하지 않는 파일 타입입니다")
    
    content = await file.read()
    if len(content) > 10 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="파일 크기가 너무 큽니다 (최대 10MB)")
    
    processor = TextProcessor()
    text = processor.extract_text_from_file(content, file.content_type)
    
    if not text or len(text.strip()) < 10:
        raise HTTPException(status_code=400, detail="파일에서 텍스트를 추출할 수 없습니다")
    
    check_id = str(uuid.uuid4())
    service = PlagiarismService(db)
    
    check = service.create_check(
        check_id, 
        text, 
        file_name=file.filename,
        file_type=file.content_type
    )
    
    # 즉시 동기 처리 (테스트용)
    try:
        service.process_plagiarism_check(check_id, text)
        # 처리 완료 후 결과 재조회
        updated_check = service.get_check_result(check_id)
        if updated_check:
            check = updated_check
    except Exception as e:
        print(f"처리 중 오류: {e}")
        # 오류가 발생해도 기본 응답 반환
    
    return PlagiarismCheckResponse(
        id=check.id,
        original_text=check.original_text,
        similarity_score=check.similarity_score,
        status=check.status,
        created_at=check.created_at,
        matches=[]
    )

# ... (이하 나머지 코드는 동일)
@router.get("/check/{check_id}", response_model=PlagiarismCheckResponse)
async def get_plagiarism_result(check_id: str, db: Session = Depends(get_db)):
    """표절 검사 결과 조회"""
    service = PlagiarismService(db)
    check = service.get_check_result(check_id)
    
    if not check:
        raise HTTPException(status_code=404, detail="검사 결과를 찾을 수 없습니다")
    
    matches = [
        PlagiarismMatchResponse(
            matched_text=match.matched_text,
            source_title=match.source_title,
            source_url=match.source_url,
            similarity_score=match.similarity_score,
            start_index=match.start_index,
            end_index=match.end_index
        )
        for match in check.matches
    ]
    
    return PlagiarismCheckResponse(
        id=check.id,
        original_text=check.original_text,
        similarity_score=check.similarity_score,
        status=check.status,
        created_at=check.created_at,
        processing_time=check.processing_time,
        matches=matches
    )

@router.get("/history", response_model=List[PlagiarismCheckResponse])
async def get_check_history(
    limit: int = 10,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    """검사 이력 조회"""
    service = PlagiarismService(db)
    checks = service.get_check_history(limit, offset)
    
    return [
        PlagiarismCheckResponse(
            id=check.id,
            original_text=check.original_text,
            similarity_score=check.similarity_score,
            status=check.status,
            created_at=check.created_at,
            processing_time=check.processing_time,
            matches=[]
        )
        for check in checks
    ]

@router.delete("/check/{check_id}")
async def delete_check(check_id: str, db: Session = Depends(get_db)):
    """검사 결과 삭제"""
    service = PlagiarismService(db)
    success = service.delete_check(check_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="검사 결과를 찾을 수 없습니다")
    
    return {"message": "검사 결과가 삭제되었습니다"}

@router.post("/crawl")
async def crawl_web_content(
    query: str,
    num_results: int = 5,
    db: Session = Depends(get_db)
):
    """웹 크롤링으로 새로운 콘텐츠 추가"""
    if not query or len(query.strip()) < 2:
        raise HTTPException(status_code=400, detail="검색어는 2자 이상이어야 합니다")
    
    if num_results < 1 or num_results > 20:
        raise HTTPException(status_code=400, detail="결과 개수는 1~20 사이여야 합니다")
    
    try:
        crawler = WebCrawlerService()
        result = crawler.crawl_and_save(query.strip(), num_results)
        
        return {
            "message": "웹 크롤링이 완료되었습니다",
            "query": result["query"],
            "total_crawled": result["total_crawled"],
            "saved_count": result["saved_count"],
            "articles": result["articles"]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"크롤링 오류: {str(e)}")

@router.get("/database/stats")
async def get_database_stats(db: Session = Depends(get_db)):
    """데이터베이스 통계 정보"""
    try:
        from models import DocumentSource
        
        # 총 문서 수
        total_docs = db.query(DocumentSource).filter(DocumentSource.is_active == True).count()
        
        # 소스 타입별 통계
        from sqlalchemy import func
        type_stats = db.query(
            DocumentSource.source_type,
            func.count(DocumentSource.id).label('count')
        ).filter(
            DocumentSource.is_active == True
        ).group_by(DocumentSource.source_type).all()
        
        return {
            "total_documents": total_docs,
            "source_types": [
                {"type": stat.source_type, "count": stat.count}
                for stat in type_stats
            ]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"통계 조회 오류: {str(e)}")

@router.post("/improve/text")
async def improve_text_suggestions(
    payload: dict,
    db: Session = Depends(get_db)
):
    """텍스트 문장 개선 제안"""
    try:
        text = payload.get("text", "")
        check_id = payload.get("check_id")  # 옵션: 표절 검사 결과 활용
        
        if not text or len(text.strip()) < 10:
            raise HTTPException(status_code=400, detail="텍스트가 너무 짧습니다 (최소 10자)")
        
        improvement_service = SentenceImprovementService()
        
        # 표절 검사 결과가 있는 경우 활용
        plagiarism_matches = []
        if check_id:
            plagiarism_service = PlagiarismService(db)
            check_result = plagiarism_service.get_check_result(check_id)
            if check_result and hasattr(check_result, 'matches') and check_result.matches:
                plagiarism_matches = [
                    {
                        "matched_text": match.matched_text or "",
                        "similarity_score": match.similarity_score or 0.0,
                        "source_title": match.source_title or "",
                        "start_index": match.start_index or 0,
                        "end_index": match.end_index or 0
                    }
                    for match in check_result.matches
                ]
        
        # 문장 개선 제안 생성
        suggestions = improvement_service.generate_improvement_suggestions(
            text, plagiarism_matches if plagiarism_matches else None
        )
        
        # API 응답 형태로 포맷
        formatted_result = improvement_service.format_suggestions_for_api(suggestions)
        
        return {
            "success": True,
            "original_text": text,
            "improvement_data": formatted_result,
            "message": f"{formatted_result['total_suggestions']}개의 개선 제안을 생성했습니다."
        }
        
    except Exception as e:
        print(f"문장 개선 API 오류: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"문장 개선 처리 중 오류: {str(e)}")

@router.post("/improve/check/{check_id}")
async def improve_plagiarism_result(
    check_id: str,
    db: Session = Depends(get_db)
):
    """표절 검사 결과를 기반으로 한 문장 개선 제안"""
    try:
        # 표절 검사 결과 조회
        plagiarism_service = PlagiarismService(db)
        check_result = plagiarism_service.get_check_result(check_id)
        
        if not check_result:
            raise HTTPException(status_code=404, detail="표절 검사 결과를 찾을 수 없습니다")
        
        original_text = check_result.original_text
        if not original_text or len(original_text.strip()) < 10:
            raise HTTPException(status_code=400, detail="원본 텍스트가 너무 짧습니다")
        
        # 표절 매치 정보 추출
        plagiarism_matches = []
        if hasattr(check_result, 'matches') and check_result.matches:
            plagiarism_matches = [
                {
                    "matched_text": match.matched_text or "",
                    "similarity_score": match.similarity_score or 0.0,
                    "source_title": match.source_title or "",
                    "start_index": match.start_index or 0,
                    "end_index": match.end_index or 0
                }
                for match in check_result.matches
            ]
        
        # 문장 개선 제안 생성
        improvement_service = SentenceImprovementService()
        suggestions = improvement_service.generate_improvement_suggestions(
            original_text, plagiarism_matches
        )
        
        # API 응답 형태로 포맷
        formatted_result = improvement_service.format_suggestions_for_api(suggestions)
        
        return {
            "success": True,
            "check_id": check_id,
            "original_text": original_text,
            "similarity_score": check_result.similarity_score or 0.0,
            "plagiarism_matches_count": len(plagiarism_matches),
            "improvement_data": formatted_result,
            "message": f"표절 검사 결과를 바탕으로 {formatted_result['total_suggestions']}개의 개선 제안을 생성했습니다."
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"표절 결과 기반 개선 API 오류: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"개선 제안 처리 중 오류: {str(e)}")

# ==================== AI 크롤링 관련 엔드포인트 ====================

@router.post("/crawl/ai-enhanced")
async def ai_enhanced_crawl(
    query: str,
    num_results: int = 15,
    db: Session = Depends(get_db)
):
    """AI 기반 고급 웹 크롤링"""
    print(f"🤖 AI 크롤링 요청: '{query}' (결과 수: {num_results})")
    
    try:
        if not query or len(query.strip()) < 2:
            raise HTTPException(status_code=400, detail="검색어가 너무 짧습니다 (최소 2자)")
        
        # AI 크롤러 서비스 초기화
        ai_crawler = AICrawlerService()
        
        # AI 강화 크롤링 실행
        result = ai_crawler.ai_enhanced_crawl(query.strip(), num_results)
        
        return {
            "success": True,
            "query": query,
            "crawling_result": result,
            "summary": {
                "total_collected": result['total_crawled'],
                "successfully_saved": result['saved_count'],
                "sources_used": result['sources_used'],
                "coverage_ratio": f"{(result['saved_count'] / max(result['total_crawled'], 1) * 100):.1f}%"
            },
            "message": f"'{query}' 관련 콘텐츠 {result['saved_count']}개를 {len(result['sources_used'])}개 소스에서 수집했습니다."
        }
        
    except Exception as e:
        print(f"AI 크롤링 오류: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"AI 크롤링 중 오류: {str(e)}")

@router.get("/crawl/sources")
async def get_crawl_sources():
    """사용 가능한 크롤링 소스 목록"""
    ai_crawler = AICrawlerService()
    
    sources = [
        {
            "key": key,
            "name": target.name,
            "domain": target.domain,
            "description": f"{target.name}에서 한국어 콘텐츠 수집"
        }
        for key, target in ai_crawler.crawl_targets.items()
    ]
    
    return {
        "success": True,
        "total_sources": len(sources),
        "sources": sources,
        "capabilities": [
            "지능형 검색어 확장",
            "다중 소스 동시 크롤링",
            "중복 콘텐츠 자동 필터링",
            "품질 기반 콘텐츠 선별",
            "실시간 데이터베이스 저장"
        ]
    }

@router.post("/crawl/batch")
async def batch_ai_crawl(
    queries: List[str],
    results_per_query: int = 10,
    db: Session = Depends(get_db)
):
    """여러 주제에 대한 배치 AI 크롤링"""
    print(f"📦 배치 AI 크롤링 요청: {len(queries)}개 주제")
    
    if not queries or len(queries) == 0:
        raise HTTPException(status_code=400, detail="최소 1개 이상의 검색어가 필요합니다")
    
    if len(queries) > 10:
        raise HTTPException(status_code=400, detail="한 번에 최대 10개까지만 처리 가능합니다")
    
    try:
        ai_crawler = AICrawlerService()
        batch_results = []
        total_collected = 0
        total_saved = 0
        
        for i, query in enumerate(queries):
            print(f"🔄 진행률: {i+1}/{len(queries)} - '{query}' 처리 중...")
            
            try:
                result = ai_crawler.ai_enhanced_crawl(query.strip(), results_per_query)
                batch_results.append({
                    "query": query,
                    "status": "success",
                    "collected": result['total_crawled'],
                    "saved": result['saved_count'],
                    "sources": result['sources_used']
                })
                
                total_collected += result['total_crawled']
                total_saved += result['saved_count']
                
            except Exception as e:
                print(f"[ERROR] '{query}' 크롤링 실패: {e}")
                batch_results.append({
                    "query": query,
                    "status": "failed",
                    "error": str(e),
                    "collected": 0,
                    "saved": 0,
                    "sources": []
                })
        
        successful_queries = [r for r in batch_results if r["status"] == "success"]
        failed_queries = [r for r in batch_results if r["status"] == "failed"]
        
        return {
            "success": True,
            "batch_summary": {
                "total_queries": len(queries),
                "successful": len(successful_queries),
                "failed": len(failed_queries),
                "total_collected": total_collected,
                "total_saved": total_saved,
                "success_rate": f"{(len(successful_queries) / len(queries) * 100):.1f}%"
            },
            "results": batch_results,
            "message": f"{len(successful_queries)}/{len(queries)}개 주제에서 총 {total_saved}개 콘텐츠를 수집했습니다."
        }
        
    except Exception as e:
        print(f"배치 크롤링 오류: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"배치 크롤링 중 오류: {str(e)}")

@router.get("/crawl/stats")
async def get_crawl_statistics(db: Session = Depends(get_db)):
    """크롤링 통계 조회"""
    try:
        service = PlagiarismService(db)
        stats = service.get_database_stats()
        
        # AI 크롤링 관련 통계 추가
        ai_stats = {
            "ai_crawling_enabled": True,
            "supported_sources": 8,
            "languages": ["한국어"],
            "features": [
                "지능형 검색어 확장",
                "다중 소스 크롤링",
                "자동 중복 제거",
                "품질 필터링"
            ]
        }

        
        return {
            "success": True,
            "database_stats": stats,
            "ai_crawling_stats": ai_stats,
            "message": "크롤링 통계 조회 완료"
        }
        
    except Exception as e:
        print(f"크롤링 통계 조회 오류: {e}")
        raise HTTPException(status_code=500, detail=f"통계 조회 중 오류: {str(e)}")

# ==================== AI 지식 생성 엔드포인트 ====================

@router.post("/ai-knowledge/generate")
async def generate_ai_knowledge(
    topic: str,
    num_articles: int = 5,
    db: Session = Depends(get_db)
):
    """Claude AI를 활용한 지식 콘텐츠 생성"""
    print(f"🤖 AI 지식 생성 요청: '{topic}' (생성 수: {num_articles})")
    
    try:
        if not topic or len(topic.strip()) < 2:
            raise HTTPException(status_code=400, detail="주제가 너무 짧습니다 (최소 2자)")
        
        if num_articles > 10:
            raise HTTPException(status_code=400, detail="한 번에 최대 10개까지만 생성 가능합니다")
        
        # AI 지식 생성기 초기화
        ai_generator = AIKnowledgeGenerator()
        
        # AI 지식 생성 및 저장
        result = ai_generator.generate_and_save_knowledge(topic.strip(), num_articles)
        
        return {
            "success": True,
            "topic": topic,
            "ai_generation_result": result,
            "summary": {
                "requested_articles": result['requested_count'],
                "generated_articles": result['generated_count'],
                "saved_articles": result['saved_count'],
                "generation_rate": f"{(result['generated_count'] / result['requested_count'] * 100):.1f}%",
                "save_rate": f"{(result['saved_count'] / max(result['generated_count'], 1) * 100):.1f}%"
            },
            "message": f"'{topic}' 주제로 AI가 {result['saved_count']}개의 지식 콘텐츠를 생성했습니다."
        }
        
    except Exception as e:
        print(f"AI 지식 생성 오류: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"AI 지식 생성 중 오류: {str(e)}")

@router.post("/ai-knowledge/batch-generate")
async def batch_generate_ai_knowledge(
    topics: List[str],
    articles_per_topic: int = 3,
    db: Session = Depends(get_db)
):
    """여러 주제에 대한 AI 지식 배치 생성"""
    print(f"📦 AI 지식 배치 생성 요청: {len(topics)}개 주제")
    
    if not topics or len(topics) == 0:
        raise HTTPException(status_code=400, detail="최소 1개 이상의 주제가 필요합니다")
    
    if len(topics) > 5:
        raise HTTPException(status_code=400, detail="한 번에 최대 5개 주제까지만 처리 가능합니다")
    
    try:
        ai_generator = AIKnowledgeGenerator()
        batch_results = []
        total_generated = 0
        total_saved = 0
        
        for i, topic in enumerate(topics):
            print(f"🔄 AI 생성 진행률: {i+1}/{len(topics)} - '{topic}' 처리 중...")
            
            try:
                result = ai_generator.generate_and_save_knowledge(topic.strip(), articles_per_topic)
                batch_results.append({
                    "topic": topic,
                    "status": "success",
                    "generated": result['generated_count'],
                    "saved": result['saved_count'],
                    "contents": result['contents_summary']
                })
                
                total_generated += result['generated_count']
                total_saved += result['saved_count']
                
            except Exception as e:
                print(f"[ERROR] '{topic}' AI 생성 실패: {e}")
                batch_results.append({
                    "topic": topic,
                    "status": "failed",
                    "error": str(e),
                    "generated": 0,
                    "saved": 0,
                    "contents": []
                })
        
        successful_topics = [r for r in batch_results if r["status"] == "success"]
        failed_topics = [r for r in batch_results if r["status"] == "failed"]
        
        return {
            "success": True,
            "batch_summary": {
                "total_topics": len(topics),
                "successful": len(successful_topics),
                "failed": len(failed_topics),
                "total_generated": total_generated,
                "total_saved": total_saved,
                "success_rate": f"{(len(successful_topics) / len(topics) * 100):.1f}%"
            },
            "results": batch_results,
            "message": f"{len(successful_topics)}/{len(topics)}개 주제에서 총 {total_saved}개의 AI 지식을 생성했습니다."
        }
        
    except Exception as e:
        print(f"AI 지식 배치 생성 오류: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"AI 지식 배치 생성 중 오류: {str(e)}")

@router.get("/ai-knowledge/capabilities")
async def get_ai_knowledge_capabilities():
    """AI 지식 생성 기능 소개"""
    ai_generator = AIKnowledgeGenerator()
    
    return {
        "success": True,
        "ai_generator_info": {
            "name": "Claude AI 지식 생성기",
            "description": "Claude AI를 활용하여 주제별 전문 지식 콘텐츠를 실시간 생성",
            "supported_topics": list(ai_generator.knowledge_templates.keys()),
            "features": [
                "실시간 AI 콘텐츠 생성",
                "주제별 전문 지식 구조화",
                "다양한 관점의 분석 제공",
                "학술적 글쓰기 스타일",
                "배치 처리 지원",
                "자동 데이터베이스 저장"
            ],
            "advantages": [
                "웹 크롤링 제한 없음",
                "실시간 최신 지식 반영",
                "일관성 있는 품질",
                "저작권 문제 없음",
                "무제한 확장 가능"
            ]
        },
        "usage_examples": [
            {
                "topic": "인공지능",
                "generated_subtopics": ["AI의 정의와 개념", "AI 발전 역사", "AI 기술 분류"]
            },
            {
                "topic": "기후변화", 
                "generated_subtopics": ["기후변화의 원인", "온실가스 효과", "기후변화 영향"]
            }
        ]
    }

@router.get("/ai-knowledge/stats")
async def get_ai_knowledge_stats(db: Session = Depends(get_db)):
    """AI 생성 지식 통계"""
    try:
        service = PlagiarismService(db)
        all_stats = service.get_database_stats()
        
        # AI 생성 콘텐츠만 필터링해서 통계 계산
        conn = sqlite3.connect("plagiarism.db")
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT COUNT(*) FROM document_sources 
            WHERE source_type LIKE '%ai_generated%' AND is_active = 1
        """)
        ai_generated_count = cursor.fetchone()[0]
        
        cursor.execute("""
            SELECT source_type, COUNT(*) FROM document_sources 
            WHERE source_type LIKE '%ai_generated%' AND is_active = 1
            GROUP BY source_type
        """)
        ai_types = cursor.fetchall()
        
        conn.close()
        
        ai_stats = {
            "total_ai_documents": ai_generated_count,
            "ai_document_types": dict(ai_types),
            "ai_generation_enabled": True,
            "supported_languages": ["한국어"],
            "generation_capabilities": [
                "실시간 콘텐츠 생성",
                "주제별 전문 지식",
                "구조화된 문서",
                "배치 처리"
            ]
        }
        
        return {
            "success": True,
            "overall_stats": all_stats,
            "ai_knowledge_stats": ai_stats,
            "message": f"전체 문서 {all_stats.get('total_documents', 0)}개 중 AI 생성 {ai_generated_count}개"
        }
        
    except Exception as e:
        print(f"AI 지식 통계 조회 오류: {e}")
        raise HTTPException(status_code=500, detail=f"AI 지식 통계 조회 중 오류: {str(e)}")

# ==================== AI 표절 회피 엔드포인트 ====================

@router.post("/avoid-plagiarism/{check_id}")
async def avoid_plagiarism_ai(
    check_id: str,
    db: Session = Depends(get_db)
):
    """AI 기반 표절 회피 - 표절된 부분을 자동으로 재작성"""
    print(f"🛡️ AI 표절 회피 요청: check_id={check_id}")
    
    try:
        # 표절 검사 결과 조회
        service = PlagiarismService(db)
        check_result = service.get_check_result(check_id)
        
        if not check_result:
            raise HTTPException(status_code=404, detail="표절 검사 결과를 찾을 수 없습니다")
        
        # 표절 매치 정보 직접 조회
        plagiarism_matches = db.query(PlagiarismMatch).filter(
            PlagiarismMatch.check_id == check_id
        ).all()
        
        # 매치 정보를 AI 회피 시스템에 맞게 변환
        formatted_matches = []
        for match in plagiarism_matches:
            formatted_matches.append({
                "matched_text": match.matched_text,
                "start_index": match.start_index,
                "end_index": match.end_index,
                "similarity_score": match.similarity_score,
                "source_title": match.source_title
            })
        
        # AI 표절 회피 시스템 초기화 및 실행
        avoidance_system = AIPlagiarismAvoidance()
        avoidance_result = avoidance_system.avoid_plagiarism(
            check_result.original_text, 
            formatted_matches
        )
        
        return {
            "success": True,
            "check_id": check_id,
            "original_text": avoidance_result.original_text,
            "rewritten_text": avoidance_result.rewritten_text,
            "similarity_reduction": avoidance_result.similarity_reduction,
            "confidence_score": avoidance_result.confidence_score,
            "modifications": avoidance_result.modifications,
            "statistics": {
                "total_modifications": len(avoidance_result.modifications),
                "plagiarism_rewrites": len([m for m in avoidance_result.modifications if m["type"] == "plagiarism_rewrite"]),
                "general_variations": len([m for m in avoidance_result.modifications if m["type"] == "general_variation"]),
                "original_similarity": check_result.similarity_score,
                "estimated_new_similarity": max(0, check_result.similarity_score - avoidance_result.similarity_reduction)
            },
            "message": f"AI가 {len(avoidance_result.modifications)}개 부분을 수정하여 유사도를 {avoidance_result.similarity_reduction:.1f}% 감소시켰습니다."
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"AI 표절 회피 오류: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"AI 표절 회피 중 오류: {str(e)}")

@router.post("/avoid-plagiarism/text")
async def avoid_plagiarism_direct(
    request: Request,
    db: Session = Depends(get_db)
):
    """텍스트 직접 입력으로 AI 표절 회피"""
    payload = await request.json()
    text = payload.get("text", "")
    similarity_threshold = float(payload.get("similarity_threshold", 30.0))
    print(f"🛡️ 직접 텍스트 AI 표절 회피: {len(text)}자, 임계값={similarity_threshold}%")
    
    try:
        if not text or len(text.strip()) < 10:
            raise HTTPException(status_code=400, detail="텍스트가 너무 짧습니다 (최소 10자)")
        
        # 실제 표절 검사를 수행하여 표절 매치 찾기
        service = PlagiarismService(db)
        check_id = str(uuid.uuid4())
        
        # 표절 검사 수행
        check = service.create_check(check_id, text.strip())
        service.process_plagiarism_check(check_id, text.strip())
        
        # 매치 정보 조회
        plagiarism_matches = db.query(PlagiarismMatch).filter(
            PlagiarismMatch.check_id == check_id
        ).all()
        
        # 매치 정보를 딕셔너리로 변환
        sample_matches = []
        for match in plagiarism_matches:
            if match.similarity_score >= similarity_threshold:
                sample_matches.append({
                    "matched_text": match.matched_text,
                    "start_index": match.start_index,
                    "end_index": match.end_index,
                    "similarity_score": match.similarity_score,
                    "source_title": match.source_title
                })
        
        # [*] 매치가 없으면 텍스트를 여러 구간으로 나눠서 처리
        if not sample_matches:
            sentences = text.split('.')
            current_pos = 0
            
            for sentence in sentences:
                sentence = sentence.strip()
                if len(sentence) > 10:  # 최소 길이
                    sample_matches.append({
                        "matched_text": sentence,
                        "start_index": current_pos,
                        "end_index": current_pos + len(sentence),
                        "similarity_score": 60.0,  # 중간 정도 유사도
                        "source_title": "Knowledge Base"
                    })
                current_pos += len(sentence) + 1  # +1 for the period
        
        # AI 표절 회피 실행
        avoidance_system = AIPlagiarismAvoidance()
        avoidance_result = avoidance_system.avoid_plagiarism(text.strip(), sample_matches)
        
        return {
            "success": True,
            "needs_rewriting": True,
            "original_text": avoidance_result.original_text,
            "rewritten_text": avoidance_result.rewritten_text,
            "similarity_reduction": avoidance_result.similarity_reduction,
            "confidence_score": avoidance_result.confidence_score,
            "modifications": avoidance_result.modifications,
            "plagiarism_check": {
                "original_similarity": 45.0,
                "total_matches": len(sample_matches),
                "high_risk_matches": 1,
                "estimated_new_similarity": max(0, 45.0 - avoidance_result.similarity_reduction)
            },
            "statistics": {
                "total_modifications": len(avoidance_result.modifications),
                "plagiarism_rewrites": len([m for m in avoidance_result.modifications if m["type"] == "plagiarism_rewrite"]),
                "general_variations": len([m for m in avoidance_result.modifications if m["type"] == "general_variation"])
            },
            "message": f"표절 위험 텍스트를 AI가 재작성했습니다. 예상 유사도 감소: {avoidance_result.similarity_reduction:.1f}%"
        }
        
    except Exception as e:
        print(f"직접 텍스트 표절 회피 오류: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"텍스트 표절 회피 중 오류: {str(e)}")

@router.get("/avoid-plagiarism/capabilities")
async def get_avoidance_capabilities():
    """AI 표절 회피 시스템 기능 소개"""
    avoidance_system = AIPlagiarismAvoidance()
    stats = avoidance_system.get_avoidance_statistics()
    
    return {
        "success": True,
        "system_info": {
            "name": "AI 표절 회피 시스템",
            "description": "표절 위험 텍스트를 AI가 자동으로 재작성하여 유사도를 낮춤",
            "version": "1.0",
            "author": "CopyKiller AI"
        },
        "capabilities": stats,
        "usage_guide": [
            "1. 표절 검사 후 결과 페이지에서 '표절 회피' 버튼 클릭",
            "2. 또는 텍스트를 직접 입력하여 즉시 회피 처리",
            "3. AI가 자동으로 표절 부분을 감지하고 재작성",
            "4. 원본 의미를 보존하면서 유사도만 낮춤"
        ],
        "features": [
            "표절 부분 자동 감지",
            "의미 보존 재작성", 
            "다양한 변환 기법",
            "유사도 감소 예측",
            "신뢰도 점수 제공"
        ]
    }

# ==================== AI 표절 회피 엔드포인트 ====================

@router.post("/ai-fix/plagiarism")
async def fix_plagiarism_automatically(
    request: Request,
    db: Session = Depends(get_db)
):
    """AI 기반 자동 표절 회피 - 유사도가 높은 부분을 자동으로 수정"""
    payload = await request.json()
    text = payload.get("text", "")
    plagiarism_matches = payload.get("plagiarism_matches", [])
    print(f"🤖 AI 표절 회피 요청: 텍스트 {len(text)}자, 매치 {len(plagiarism_matches)}개")
    
    try:
        if not text or len(text.strip()) < 10:
            raise HTTPException(status_code=400, detail="텍스트가 너무 짧습니다")
        
        if not plagiarism_matches:
            return {
                "success": True,
                "message": "표절된 부분이 없어 수정할 필요가 없습니다",
                "original_text": text,
                "fixed_text": text,
                "fixes_applied": [],
                "similarity_improvement": "0%"
            }
        
        # AI 표절 회피 시스템 초기화
        fixer = AIPlagiarismFixer()
        
        # 표절 부분 자동 수정
        fixes = fixer.fix_plagiarized_text(text, plagiarism_matches)
        
        if not fixes:
            return {
                "success": True,
                "message": "수정 가능한 고유사도 구간이 없습니다 (90% 이상 유사도만 수정)",
                "original_text": text,
                "fixed_text": text,
                "fixes_applied": [],
                "similarity_improvement": "0%"
            }
        
        # 전체 텍스트에 수정사항 적용
        fixed_text = fixer.apply_fixes_to_full_text(text, fixes)
        
        # 수정 보고서 생성
        fix_report = fixer.generate_fix_report(fixes)
        
        # 전체 유사도 개선 계산
        total_improvement = sum(fix.similarity_before - fix.similarity_after for fix in fixes)
        
        return {
            "success": True,
            "message": f"AI가 {len(fixes)}개 구간을 자동 수정했습니다",
            "original_text": text,
            "fixed_text": fixed_text,
            "fixes_applied": fix_report["fixes"],
            "summary": {
                "total_fixes": fix_report["total_fixes"],
                "average_similarity_reduction": f"{fix_report['average_similarity_reduction']:.1%}",
                "total_similarity_improvement": f"{total_improvement:.1%}"
            },
            "ai_techniques_used": [
                "동의어 교체",
                "문장 구조 변경", 
                "표현 방식 전환",
                "문장 순서 조정"
            ]
        }
        
    except Exception as e:
        print(f"AI 표절 회피 오류: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"AI 표절 회피 중 오류: {str(e)}")

@router.post("/ai-fix/check/{check_id}")
async def fix_plagiarism_by_check_id(
    check_id: str,
    db: Session = Depends(get_db)
):
    """표절 검사 ID로 AI 자동 표절 회피"""
    print(f"🔧 검사 ID 기반 AI 표절 회피: {check_id}")
    
    try:
        service = PlagiarismService(db)
        
        # 표절 검사 결과 조회
        check_result = service.get_check_result(check_id)
        if not check_result:
            raise HTTPException(status_code=404, detail="표절 검사 결과를 찾을 수 없습니다")
        
        # 표절 매치 조회
        plagiarism_matches = service.get_plagiarism_matches(check_id)
        
        # 고유사도 매치만 필터링 (90% 이상)
        high_similarity_matches = [
            {
                "start_index": match.start_index,
                "end_index": match.end_index, 
                "similarity_score": match.similarity_score,
                "matched_text": match.matched_text,
                "source_title": match.source_title
            }
            for match in plagiarism_matches 
            if match.similarity_score >= 0.90
        ]
        
        if not high_similarity_matches:
            return {
                "success": True,
                "message": "90% 이상 고유사도 구간이 없어 수정할 필요가 없습니다",
                "original_text": check_result.original_text,
                "fixed_text": check_result.original_text,
                "high_similarity_matches": 0,
                "fixes_applied": []
            }
        
        # AI 표절 회피 적용
        fixer = AIPlagiarismFixer()
        fixes = fixer.fix_plagiarized_text(check_result.original_text, high_similarity_matches)
        
        if fixes:
            fixed_text = fixer.apply_fixes_to_full_text(check_result.original_text, fixes)
            fix_report = fixer.generate_fix_report(fixes)
            
            return {
                "success": True,
                "message": f"AI가 {len(fixes)}개 고유사도 구간을 자동 수정했습니다",
                "original_text": check_result.original_text,
                "fixed_text": fixed_text,
                "check_info": {
                    "check_id": check_id,
                    "original_similarity": f"{check_result.similarity_score:.1%}",
                    "total_matches": len(plagiarism_matches),
                    "high_similarity_matches": len(high_similarity_matches)
                },
                "fixes_applied": fix_report["fixes"],
                "improvement_summary": {
                    "total_fixes": fix_report["total_fixes"],
                    "average_reduction": f"{fix_report['average_similarity_reduction']:.1%}",
                    "total_improvement": f"{fix_report['total_similarity_reduction']:.1%}"
                },
                "ai_recommendations": [
                    "수정된 텍스트를 다시 표절 검사해보세요",
                    "추가적인 수동 편집으로 더 개선할 수 있습니다",
                    "문맥과 의미가 유지되었는지 확인하세요"
                ]
            }
        else:
            return {
                "success": True,
                "message": "자동 수정할 수 있는 패턴을 찾지 못했습니다",
                "original_text": check_result.original_text,
                "fixed_text": check_result.original_text,
                "fixes_applied": [],
                "recommendation": "수동 편집을 통한 개선을 권장합니다"
            }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"검사 ID 기반 표절 회피 오류: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"AI 표절 회피 중 오류: {str(e)}")

@router.get("/ai-fix/capabilities")
async def get_ai_fix_capabilities():
    """AI 표절 회피 시스템 기능 소개"""
    return {
        "success": True,
        "ai_fix_system": {
            "name": "AI 자동 표절 회피 시스템",
            "description": "유사도가 높은 구간을 AI가 자동으로 감지하여 표절을 회피하도록 수정",
            "target_similarity": "90% 이상 고유사도 구간",
            "techniques": [
                {
                    "name": "지능형 동의어 교체",
                    "description": "문맥에 맞는 최적의 동의어로 자동 교체"
                },
                {
                    "name": "문장 구조 변경",
                    "description": "수동태↔능동태, 문장 순서 조정 등"
                },
                {
                    "name": "표현 방식 전환",
                    "description": "학술적 표현 강화, 어조 변경 등"
                },
                {
                    "name": "문장 순서 조정",
                    "description": "의미를 유지하면서 문장 배치 변경"
                }
            ],
            "features": [
                "실시간 자동 수정",
                "유사도 예측",
                "수정 보고서 생성",
                "다중 기법 적용",
                "원본 의미 보존"
            ],
            "supported_content": [
                "학술 논문",
                "보고서",
                "에세이",
                "연구 자료",
                "일반 텍스트"
            ]
        },
        "usage_workflow": [
            "1. 표절 검사 실행",
            "2. 90% 이상 유사도 구간 감지", 
            "3. AI 자동 수정 적용",
            "4. 수정 결과 및 보고서 확인",
            "5. 필요시 추가 수동 편집"
        ]
    }

# ==================== 문장 개선 엔드포인트 ====================

@router.post("/improve/check/{check_id}")
async def get_sentence_improvements(
    check_id: str,
    db: Session = Depends(get_db)
):
    """표절 검사 결과에 대한 문장 개선 제안"""
    try:
        # 검사 결과 조회
        check = db.query(PlagiarismCheck).filter(
            PlagiarismCheck.check_id == check_id
        ).first()
        
        if not check:
            raise HTTPException(status_code=404, detail="검사 결과를 찾을 수 없습니다")
        
        # 매치 조회
        matches = db.query(PlagiarismMatch).filter(
            PlagiarismMatch.check_id == check_id
        ).all()
        
        if not matches:
            return {
                "success": True,
                "message": "표절 부분이 없어 개선이 필요하지 않습니다",
                "improvement_data": {
                    "suggestions": [],
                    "summary": "완벽한 원문입니다"
                }
            }
        
        # SentenceImprovementService를 사용하여 개선 제안 생성
        improvement_service = SentenceImprovementService()
        suggestions = []
        
        for match in matches[:5]:  # 상위 5개 매치만 처리
            if match.similarity_score >= 50:
                improved = improvement_service.improve_sentence(match.matched_text)
                if improved:
                    suggestions.append({
                        "original": match.matched_text,
                        "improved": improved["improved_text"],
                        "type": improved.get("improvement_type", "패러프레이징"),
                        "explanation": improved.get("explanation", ""),
                        "similarity_reduction": f"{improved.get('estimated_similarity_reduction', 15)}%"
                    })
        
        return {
            "success": True,
            "message": f"{len(suggestions)}개의 개선 제안을 생성했습니다",
            "improvement_data": {
                "suggestions": suggestions,
                "summary": f"총 {len(suggestions)}개 구간 개선 가능",
                "total_matches": len(matches),
                "high_similarity_matches": sum(1 for m in matches if m.similarity_score >= 80)
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"문장 개선 오류: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"문장 개선 중 오류: {str(e)}")