#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from typing import Dict, List
import re

class RealTimeImprovementService:
    """실시간 개선 제안 서비스"""
    
    def __init__(self):
        self.synonym_dict = {
            # 학술 용어 동의어 사전
            "분석": ["검토", "고찰", "조사", "탐구", "연구"],
            "결과": ["성과", "산출물", "결론", "도출", "귀결"],
            "방법": ["수단", "방식", "기법", "접근법", "절차"],
            "중요": ["핵심적", "필수적", "주요한", "결정적", "중대한"],
            "발전": ["진보", "향상", "개선", "성장", "도약"],
            "사회": ["공동체", "집단", "커뮤니티", "사회구조", "사회체계"]
        }
    
    def generate_real_time_suggestions(self, text: str, matches: List[Dict]) -> Dict:
        """실시간 개선 제안 생성"""
        
        suggestions = {
            "synonym_suggestions": self._suggest_synonyms(text, matches),
            "restructuring_suggestions": self._suggest_sentence_restructure(text, matches),
            "expression_variety": self._suggest_expression_variety(text),
            "citation_guide": self._generate_citation_guide(matches),
            "paraphrasing_examples": self._suggest_paraphrasing(text, matches)
        }
        
        return suggestions
    
    def _suggest_synonyms(self, text: str, matches: List[Dict]) -> List[Dict]:
        """동의어 제안"""
        suggestions = []
        
        for word, synonyms in self.synonym_dict.items():
            if word in text:
                # 해당 단어가 표절된 부분에 있는지 확인
                is_in_plagiarized = any(word in match.get('matched_text', '') for match in matches)
                
                if is_in_plagiarized:
                    suggestions.append({
                        "original": word,
                        "alternatives": synonyms,
                        "example": f"'{word}' → '{synonyms[0]}' 으로 변경",
                        "positions": self._find_word_positions(text, word)
                    })
        
        return suggestions
    
    def _suggest_sentence_restructure(self, text: str, matches: List[Dict]) -> List[Dict]:
        """문장 구조 개선 제안"""
        suggestions = []
        
        sentences = [s.strip() for s in text.split('.') if s.strip()]
        
        for match in matches:
            matched_text = match.get('matched_text', '')
            if len(matched_text) > 10:
                original_sentence = self._find_containing_sentence(text, matched_text)
                
                if original_sentence:
                    restructured = self._restructure_sentence(original_sentence)
                    
                    suggestions.append({
                        "original": original_sentence,
                        "improved": restructured,
                        "change_type": "문장구조 변경",
                        "reason": "주어와 서술어 위치를 변경하여 표현을 다양화했습니다."
                    })
        
        return suggestions[:3]  # 최대 3개만
    
    def _suggest_expression_variety(self, text: str) -> List[Dict]:
        """표현 다양화 제안"""
        suggestions = []
        
        # 반복되는 표현 패턴 찾기
        repeated_patterns = self._find_repeated_patterns(text)
        
        for pattern in repeated_patterns:
            alternatives = self._generate_alternatives(pattern)
            
            suggestions.append({
                "반복_표현": pattern,
                "대안_표현": alternatives,
                "사용_횟수": text.count(pattern),
                "개선_효과": "표현의 단조로움을 줄이고 글의 흐름을 개선합니다."
            })
        
        return suggestions
    
    def _generate_citation_guide(self, matches: List[Dict]) -> Dict:
        """인용 가이드 생성"""
        if not matches:
            return {"message": "인용이 필요한 부분이 없습니다."}
        
        high_similarity_matches = [m for m in matches if m.get('similarity_score', 0) > 60]
        
        if high_similarity_matches:
            return "💡 높은 유사도가 감지된 부분에 인용 표시를 추가하세요. 📝 인용 형식: (저자명, 연도) 또는 각주 사용하여 출처 정보를 명확히 기재하세요. ⚖️ 인용문은 전체 글의 30%를 넘지 않도록 주의하세요."
        
        return "현재 수준에서는 인용이 필수적이지 않습니다."
    
    def _suggest_paraphrasing(self, text: str, matches: List[Dict]) -> List[Dict]:
        """패러프레이징 제안"""
        suggestions = []
        
        for match in matches[:3]:  # 상위 3개 매치만
            matched_text = match.get('matched_text', '')
            similarity = match.get('similarity_score', 0)
            
            if similarity > 50 and len(matched_text) > 20:
                paraphrased = self._paraphrase_text(matched_text)
                
                suggestions.append({
                    "original": matched_text,
                    "paraphrased": paraphrased,
                    "technique": "수동태→능동태, 어순 변경, 동의어 사용",
                    "similarity_reduction": "예상 30-50% 감소"
                })
        
        return suggestions
    
    def _find_word_positions(self, text: str, word: str) -> List[int]:
        """단어 위치 찾기"""
        positions = []
        start = 0
        
        while True:
            pos = text.find(word, start)
            if pos == -1:
                break
            positions.append(pos)
            start = pos + 1
        
        return positions
    
    def _find_containing_sentence(self, text: str, matched_text: str) -> str:
        """매치된 텍스트를 포함하는 문장 찾기"""
        sentences = text.split('.')
        
        for sentence in sentences:
            if matched_text in sentence:
                return sentence.strip()
        
        return ""
    
    def _restructure_sentence(self, sentence: str) -> str:
        """문장 구조 변경"""
        # 간단한 구조 변경 예시
        if "이다" in sentence:
            return sentence.replace("이다", "라고 할 수 있다")
        elif "있다" in sentence:
            return sentence.replace("있다", "존재한다")
        elif "된다" in sentence:
            return sentence.replace("된다", "이루어진다")
        else:
            return f"즉, {sentence}"
    
    def _find_repeated_patterns(self, text: str) -> List[str]:
        """반복되는 표현 패턴 찾기"""
        words = text.split()
        patterns = []
        
        # 2-3단어 조합에서 반복 찾기
        for i in range(len(words) - 1):
            pattern = f"{words[i]} {words[i+1]}"
            if text.count(pattern) >= 2 and pattern not in patterns:
                patterns.append(pattern)
        
        return patterns[:5]  # 최대 5개
    
    def _generate_alternatives(self, pattern: str) -> List[str]:
        """대안 표현 생성"""
        alternatives = []
        
        # 기본 대안 생성 로직
        words = pattern.split()
        
        if len(words) == 2:
            # 간단한 대안 생성
            alternatives = [
                f"{words[1]} {words[0]}",  # 순서 바꾸기
                f"{words[0]}와 {words[1]}",  # 연결어 추가
                f"{words[0]}에 따른 {words[1]}"  # 관계 표현
            ]
        
        return alternatives[:3]
    
    def _paraphrase_text(self, text: str) -> str:
        """텍스트 패러프레이징"""
        # 기본적인 패러프레이징 규칙
        paraphrased = text
        
        # 수동태 → 능동태 변환
        paraphrased = re.sub(r'(\w+)이 (\w+)되다', r'\2가 \1을 만들다', paraphrased)
        
        # 연결어 변경
        replacements = {
            "그러나": "하지만",
            "따라서": "그러므로",
            "또한": "더불어",
            "즉": "다시 말해"
        }
        
        for old, new in replacements.items():
            paraphrased = paraphrased.replace(old, new)
        
        return paraphrased

# 사용 예시
if __name__ == "__main__":
    service = RealTimeImprovementService()
    
    sample_text = "인공지능 기술의 발전은 현대 사회에 중요한 영향을 미치고 있다. 이러한 발전은 다양한 분야에서 혁신을 가져오고 있다."
    
    sample_matches = [
        {
            "matched_text": "인공지능 기술의 발전",
            "similarity_score": 75.0,
            "source_title": "AI 논문"
        }
    ]
    
    suggestions = service.generate_real_time_suggestions(sample_text, sample_matches)
    
    print("🚀 실시간 개선 제안:")
    for category, content in suggestions.items():
        print(f"\n📌 {category}:")
        print(f"   {content}")