#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import openai
import os
from typing import Dict, List

class AIAnalysisService:
    """AI 기반 고급 분석 서비스"""
    
    def __init__(self):
        # OpenAI API 키 설정 (환경변수에서 가져오기)
        self.openai_api_key = os.getenv('OPENAI_API_KEY', 'your-api-key-here')
    
    def analyze_writing_style(self, text: str) -> Dict:
        """글쓰기 스타일 분석"""
        
        # 간단한 통계 분석
        sentences = text.split('.')
        words = text.split()
        
        analysis = {
            "sentence_count": len([s for s in sentences if s.strip()]),
            "word_count": len(words),
            "avg_sentence_length": len(words) / max(len(sentences), 1),
            "complexity_score": 7.5,  # 임시 값
            "tone": self._analyze_tone(text),
            "detected_style": self._analyze_writing_style(text),
            "academic_score": self._calculate_academic_score(text),
            "improvement_areas": [
                "문장 길이 조절",
                "어휘 다양성 증대",
                "논리적 연결성 강화"
            ]
        }
        
        return analysis
    
    def _calculate_complexity(self, text: str) -> str:
        """문장 복잡도 계산"""
        avg_word_length = sum(len(word) for word in text.split()) / max(len(text.split()), 1)
        
        if avg_word_length > 4:
            return "높음"
        elif avg_word_length > 3:
            return "보통"
        else:
            return "낮음"
    
    def _analyze_tone(self, text: str) -> str:
        """어조 분석"""
        formal_indicators = ["습니다", "있습니다", "됩니다", "것입니다"]
        informal_indicators = ["해요", "이에요", "거예요"]
        
        formal_count = sum(1 for indicator in formal_indicators if indicator in text)
        informal_count = sum(1 for indicator in informal_indicators if indicator in text)
        
        if formal_count > informal_count:
            return "격식체"
        elif informal_count > formal_count:
            return "비격식체"
        else:
            return "중립"
    
    def _analyze_writing_style(self, text: str) -> str:
        """문체 분석"""
        academic_words = ["따라서", "그러므로", "이에 따라", "결과적으로", "연구", "분석"]
        news_words = ["발표했다", "밝혔다", "전했다", "보도됐다"]
        essay_words = ["생각한다", "느낀다", "개인적으로", "내 의견으로는"]
        
        academic_score = sum(1 for word in academic_words if word in text)
        news_score = sum(1 for word in news_words if word in text)
        essay_score = sum(1 for word in essay_words if word in text)
        
        scores = {"학술논문": academic_score, "뉴스기사": news_score, "에세이": essay_score}
        
        return max(scores, key=scores.get)
    
    def _calculate_academic_score(self, text: str) -> int:
        """학술성 점수 계산 (1-100점)"""
        academic_indicators = [
            "연구", "분석", "검토", "고찰", "논의", "결론", "가설", "실험",
            "데이터", "결과", "방법론", "이론", "모델", "프레임워크"
        ]
        
        score = 0
        for indicator in academic_indicators:
            if indicator in text:
                score += 5
        
        return min(score, 100)

class PlagiarismContextAnalyzer:
    """표절 맥락 분석기"""
    
    def analyze_plagiarism_context(self, original_text: str, matches: List[Dict]) -> Dict:
        """표절 맥락 분석"""
        
        risk_level = self._calculate_risk_level(matches)
        plagiarism_type = self._identify_plagiarism_type(matches)
        
        analysis = {
            "risk_score": self._calculate_risk_score(matches),
            "risk_level": risk_level,
            "plagiarism_types": [plagiarism_type],
            "legal_assessment": self._assess_legal_risk(matches),
            "severity": self._assess_severity(matches),
            "improvement_suggestions": self._generate_improvement_suggestions(matches)
        }
        
        return analysis
    
    def _calculate_risk_level(self, matches: List[Dict]) -> str:
        """위험도 계산"""
        if not matches:
            return "안전"
        
        max_similarity = max(match.get('similarity_score', 0) for match in matches)
        
        if max_similarity >= 80:
            return "매우 위험"
        elif max_similarity >= 60:
            return "위험"
        elif max_similarity >= 40:
            return "주의"
        else:
            return "낮음"
    
    def _identify_plagiarism_type(self, matches: List[Dict]) -> str:
        """표절 유형 분석"""
        if not matches:
            return "표절 없음"
        
        total_matches = len(matches)
        avg_similarity = sum(match.get('similarity_score', 0) for match in matches) / total_matches
        
        if avg_similarity > 70 and total_matches > 10:
            return "직접 복사"
        elif avg_similarity > 50:
            return "부분 표절"
        elif total_matches > 15:
            return "모자이크 표절"
        else:
            return "유사 표현"
    
    def _generate_improvement_suggestions(self, matches: List[Dict]) -> List[str]:
        """개선 제안 생성"""
        if not matches:
            return ["✅ 독창적인 내용입니다."]
        
        suggestions = []
        max_similarity = max(match.get('similarity_score', 0) for match in matches)
        
        if max_similarity > 70:
            suggestions.extend([
                "🔴 높은 유사도가 감지되었습니다. 내용을 다시 작성해주세요.",
                "💡 인용문을 사용할 경우 출처를 명확히 표기하세요.",
                "✏️ 동일한 의미를 다른 표현으로 바꿔보세요."
            ])
        elif max_similarity > 40:
            suggestions.extend([
                "🟡 부분적 유사성이 있습니다.",
                "💡 핵심 아이디어는 유지하되 표현을 다양화하세요.",
                "📚 추가 자료를 참고하여 내용을 보완해보세요."
            ])
        else:
            suggestions.append("🟢 적절한 수준의 독창성을 보입니다.")
        
        return suggestions
    
    def _assess_severity(self, matches: List[Dict]) -> str:
        """심각도 평가"""
        if not matches:
            return "문제없음"
        
        high_similarity_count = sum(1 for match in matches if match.get('similarity_score', 0) > 60)
        
        if high_similarity_count >= 5:
            return "심각"
        elif high_similarity_count >= 2:
            return "보통"
        else:
            return "경미"
    
    def _assess_legal_risk(self, matches: List[Dict]) -> str:
        """법적 위험도 평가"""
        if not matches:
            return "위험없음"
        
        max_similarity = max(match.get('similarity_score', 0) for match in matches)
        
        if max_similarity >= 85:
            return "높음 - 저작권 침해 가능성"
        elif max_similarity >= 65:
            return "보통 - 주의 필요"
        else:
            return "낮음"
    
    def _calculate_risk_score(self, matches: List[Dict]) -> float:
        """위험도 점수 계산 (0-10점)"""
        if not matches:
            return 0.0
        
        max_similarity = max(match.get('similarity_score', 0) for match in matches)
        match_count = len(matches)
        
        # 기본 점수는 최대 유사도 기반
        base_score = max_similarity / 10
        
        # 매치 수에 따른 가중치
        count_weight = min(match_count * 0.5, 3.0)
        
        # 최종 점수 (0-10점)
        final_score = min(base_score + count_weight, 10.0)
        
        return round(final_score, 1)

# 사용 예시
if __name__ == "__main__":
    # AI 분석 테스트
    ai_service = AIAnalysisService()
    
    sample_text = """
    인공지능은 현대 사회에서 중요한 역할을 하고 있습니다. 
    머신러닝 기술의 발전으로 많은 분야에서 혁신이 일어나고 있으며, 
    특히 자연어 처리와 컴퓨터 비전 분야에서 놀라운 성과를 보이고 있습니다.
    """
    
    style_analysis = ai_service.analyze_writing_style(sample_text)
    print("📊 글쓰기 스타일 분석:")
    for key, value in style_analysis.items():
        print(f"   {key}: {value}")
    
    # 표절 맥락 분석 테스트
    context_analyzer = PlagiarismContextAnalyzer()
    
    sample_matches = [
        {"similarity_score": 75.5, "source_title": "AI 논문"},
        {"similarity_score": 45.2, "source_title": "기술 블로그"}
    ]
    
    context_analysis = context_analyzer.analyze_plagiarism_context(sample_text, sample_matches)
    print(f"\n🎯 표절 맥락 분석:")
    for key, value in context_analysis.items():
        print(f"   {key}: {value}")