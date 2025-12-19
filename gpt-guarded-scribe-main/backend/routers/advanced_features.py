#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from services.ai_analysis_service import AIAnalysisService, PlagiarismContextAnalyzer
from services.realtime_improvement_service import RealTimeImprovementService
from pydantic import BaseModel
from typing import List, Dict

router = APIRouter()

class AdvancedAnalysisRequest(BaseModel):
    text: str

class ImprovementRequest(BaseModel):
    text: str
    matches: List[Dict]

@router.post("/advanced-analysis")
async def advanced_analysis(request: AdvancedAnalysisRequest, db: Session = Depends(get_db)):
    """🚀 AI 기반 고급 분석"""
    try:
        ai_service = AIAnalysisService()
        
        # 글쓰기 스타일 분석
        style_analysis = ai_service.analyze_writing_style(request.text)
        
        return {
            "success": True,
            "analysis": style_analysis,
            "features": [
                "📊 글쓰기 스타일 분석",
                "🎯 문체 및 어조 판별", 
                "📚 학술성 점수 측정",
                "🔍 문장 복잡도 분석"
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/context-analysis")  
async def context_analysis(request: ImprovementRequest, db: Session = Depends(get_db)):
    """🎯 표절 맥락 분석"""
    try:
        context_analyzer = PlagiarismContextAnalyzer()
        
        # 표절 맥락 분석
        context_analysis = context_analyzer.analyze_plagiarism_context(
            request.text, 
            request.matches
        )
        
        return {
            "success": True,
            "context_analysis": context_analysis,
            "features": [
                "⚠️ 위험도 평가",
                "🔍 표절 유형 분석",
                "💡 개선 제안",
                "⚖️ 법적 위험도 평가"
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/improvement-suggestions")
async def improvement_suggestions(request: ImprovementRequest, db: Session = Depends(get_db)):
    """💡 실시간 개선 제안"""
    try:
        improvement_service = RealTimeImprovementService()
        
        # 실시간 개선 제안
        suggestions = improvement_service.generate_real_time_suggestions(
            request.text,
            request.matches
        )
        
        return {
            "success": True,
            "suggestions": suggestions,
            "features": [
                "🔄 동의어 제안",
                "📝 문장 구조 개선",
                "🎨 표현 다양화",
                "📚 인용 가이드",
                "✏️ 패러프레이징"
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/premium-features")
async def premium_features():
    """🌟 프리미엄 기능 소개"""
    return {
        "premium_features": {
            "ai_analysis": {
                "name": "🤖 AI 글쓰기 분석",
                "description": "인공지능이 글쓰기 스타일, 문체, 어조를 자동 분석",
                "benefits": [
                    "📊 상세한 글쓰기 통계",
                    "🎯 문체 유형 자동 판별",
                    "📚 학술성 점수 측정"
                ]
            },
            "smart_suggestions": {
                "name": "💡 스마트 개선 제안", 
                "description": "표절 부분에 대한 실시간 개선 방법 제시",
                "benefits": [
                    "🔄 동의어 자동 추천",
                    "📝 문장 재구성 가이드",
                    "✏️ 패러프레이징 예시"
                ]
            },
            "context_analysis": {
                "name": "🎯 맥락 기반 분석",
                "description": "단순 유사도를 넘어선 지능적 표절 맥락 분석",
                "benefits": [
                    "⚠️ 정확한 위험도 평가",
                    "🔍 표절 유형별 분석",
                    "⚖️ 법적 리스크 평가"
                ]
            },
            "real_time_help": {
                "name": "⚡ 실시간 작성 도움",
                "description": "글을 쓰면서 바로바로 표절 위험도 체크",
                "benefits": [
                    "🚨 실시간 위험 알림",
                    "📈 글 품질 향상 팁",
                    "🎨 창의적 표현 제안"
                ]
            }
        },
        "differentiation": [
            "🆚 기존 표절검사기와의 차별점:",
            "• 단순 비교 → 인공지능 분석",
            "• 결과만 제공 → 개선 방법까지",
            "• 사후 검사 → 실시간 도움",
            "• 기계적 판단 → 맥락적 이해"
        ]
    }