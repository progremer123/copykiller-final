#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""AI 기반 표절 회피 서비스 - 유사도가 높은 부분을 자동으로 수정"""

from typing import Dict, List, Optional, Tuple
import re
from dataclasses import dataclass
import random

@dataclass
class PlagiarismFix:
    """표절 수정 결과"""
    original_segment: str
    fixed_segment: str
    similarity_before: float
    similarity_after: float  # 예상 유사도
    fix_type: str
    confidence: float
    start_index: int
    end_index: int

class AIPlagiarismFixer:
    """AI 기반 표절 회피 시스템"""
    
    def __init__(self):
        # 고급 동의어 사전 (표절 회피용)
        self.plagiarism_synonyms = {
            # 학술 용어
            "연구": ["조사", "탐구", "분석", "검토", "고찰", "연구조사", "학술연구"],
            "분석": ["검토", "고찰", "탐구", "해석", "평가", "조사분석", "심층분석"],
            "결과": ["성과", "산출", "도출", "귀결", "결론", "연구결과", "분석결과"],
            "방법": ["수단", "방식", "기법", "접근법", "절차", "연구방법", "분석방법"],
            "이론": ["학설", "가설", "개념", "원리", "이념", "이론체계", "학술이론"],
            "모델": ["모형", "틀", "체계", "구조", "패턴", "분석모델", "이론모델"],
            
            # 일반 동사
            "제시하다": ["제안하다", "내세우다", "주장하다", "표명하다", "건의하다", "언급하다"],
            "나타나다": ["드러나다", "보이다", "발현되다", "표출되다", "나오다", "보여지다"],
            "보여주다": ["드러내다", "제시하다", "나타내다", "입증하다", "시사하다", "보여주다"],
            "확인하다": ["검증하다", "입증하다", "증명하다", "파악하다", "알아보다", "점검하다"],
            "발견하다": ["찾아내다", "알아내다", "파악하다", "규명하다", "밝혀내다", "도출하다"],
            "증가하다": ["늘어나다", "확대되다", "상승하다", "향상되다", "신장되다", "팽창하다"],
            "감소하다": ["줄어들다", "축소되다", "하락하다", "저하되다", "위축되다", "감축되다"],
            
            # 형용사
            "중요한": ["핵심적인", "필수적인", "결정적인", "주요한", "중대한", "의미있는", "중차대한"],
            "효과적인": ["유효한", "효율적인", "성공적인", "유용한", "실효성있는", "효과있는"],
            "새로운": ["혁신적인", "참신한", "최신의", "신규", "첨단", "새롭다", "신선한"],
            "다양한": ["여러", "각종", "다종", "갖가지", "온갖", "여러가지", "다채로운"],
            "복잡한": ["복합적인", "다면적인", "복수적인", "다층적인", "어려운", "난해한"],
            
            # 접속어/부사
            "그러나": ["하지만", "다만", "반면에", "그럼에도", "그렇지만", "그런데도"],
            "따라서": ["그러므로", "그런 이유로", "이에 따라", "결과적으로", "그리하여", "때문에"],
            "또한": ["더불어", "아울러", "동시에", "뿐만 아니라", "그리고", "게다가"],
            "특히": ["특별히", "무엇보다", "주로", "특히나", "더욱이", "그중에서도"],
            "즉": ["다시 말해", "바꾸어 말하면", "요약하면", "구체적으로", "말하자면", "정리하면"],
            
            # 명사
            "문제": ["과제", "이슈", "사안", "쟁점", "현안", "문제점", "해결과제"],
            "사회": ["공동체", "집단", "커뮤니티", "사회구조", "사회체계", "사회집단"],
            "기술": ["테크놀로지", "공학", "기법", "방법론", "노하우", "첨단기술"],
            "경제": ["경제학", "경제체계", "경제구조", "시장", "경제활동", "경제상황"],
            "교육": ["학습", "교육과정", "교육제도", "교육시스템", "학교교육", "교육활동"],
            "정치": ["정치학", "정치제도", "정치체계", "정부", "행정", "국정운영"],
        }
        
        # 문장 구조 변환 패턴
        self.structure_patterns = {
            # 수동태 → 능동태
            "passive_to_active": [
                (r'(\w+)이 (\w+)되었다', r'\2가 \1을 이루었다'),
                (r'(\w+)가 (\w+)되다', r'\1이 \2를 만들다'),
                (r'(\w+)에 의해 (\w+)되다', r'\1이 \2를 하다'),
                (r'(\w+)으로 (\w+)된다', r'\1을 통해 \2한다'),
            ],
            
            # 능동태 → 수동태
            "active_to_passive": [
                (r'(\w+)가 (\w+)을 (\w+)한다', r'\2는 \1에 의해 \3된다'),
                (r'(\w+)이 (\w+)를 (\w+)했다', r'\2가 \1에 의해 \3되었다'),
            ],
            
            # 문장 순서 변경
            "order_change": [
                (r'(\w+)하기 위해 (\w+)한다', r'\2하여 \1한다'),
                (r'(\w+)이며, (\w+)이다', r'\2이고, \1이다'),
                (r'(\w+) 그리고 (\w+)', r'\2 및 \1'),
            ]
        }
        
        # 표현 방식 변경
        self.expression_changes = {
            "formal_to_informal": {
                "것이다": "거다",
                "하는 것": "하기",
                "되는 것": "되기",
                "있는 것": "있기"
            },
            "informal_to_formal": {
                "거다": "것이다",
                "하기": "하는 것",
                "되기": "되는 것",
                "있기": "있는 것"
            },
            "academic_enhancement": {
                "많다": "다수이다",
                "적다": "소수이다",
                "크다": "상당하다",
                "작다": "미흡하다",
                "좋다": "우수하다",
                "나쁘다": "부적절하다"
            }
        }
    
    def fix_plagiarized_text(self, original_text: str, plagiarism_matches: List[Dict]) -> List[PlagiarismFix]:
        """표절된 텍스트를 AI가 자동으로 수정"""
        print(f"🔧 AI 표절 회피 시작: {len(plagiarism_matches)}개 매치 감지")
        
        fixes = []
        
        # 유사도가 높은 순으로 정렬
        sorted_matches = sorted(plagiarism_matches, key=lambda x: x.get('similarity_score', 0), reverse=True)
        
        for i, match in enumerate(sorted_matches):
            try:
                # 매치된 텍스트 추출
                start_idx = match.get('start_index', 0)
                end_idx = match.get('end_index', len(original_text))
                similarity = match.get('similarity_score', 0)
                
                # 유사도 90% 이상만 수정
                if similarity < 0.9:
                    print(f"⏭️  유사도 {similarity:.1%} - 수정 스킵")
                    continue
                
                matched_segment = original_text[start_idx:end_idx]
                print(f"🎯 수정 대상 {i+1}: '{matched_segment[:50]}...' (유사도: {similarity:.1%})")
                
                # AI 기반 수정 적용
                fixed_segment = self._apply_ai_fixes(matched_segment, similarity)
                
                if fixed_segment and fixed_segment != matched_segment:
                    # 예상 유사도 계산 (간단한 계산)
                    estimated_similarity = self._estimate_similarity_reduction(matched_segment, fixed_segment)
                    
                    fix = PlagiarismFix(
                        original_segment=matched_segment,
                        fixed_segment=fixed_segment,
                        similarity_before=similarity,
                        similarity_after=estimated_similarity,
                        fix_type="ai_automatic_fix",
                        confidence=0.85,
                        start_index=start_idx,
                        end_index=end_idx
                    )
                    
                    fixes.append(fix)
                    print(f"✅ 수정 완료: {similarity:.1%} → {estimated_similarity:.1%}")
                else:
                    print(f"❌ 수정 실패: 변경사항 없음")
                    
            except Exception as e:
                print(f"❌ 수정 오류: {e}")
                continue
        
        print(f"🎉 AI 표절 회피 완료: {len(fixes)}개 수정")
        return fixes
    
    def _apply_ai_fixes(self, text: str, similarity: float) -> str:
        """AI 기반 다층 수정 적용"""
        fixed_text = text
        
        # 1단계: 동의어 교체 (가장 효과적)
        fixed_text = self._apply_synonym_replacement(fixed_text)
        
        # 2단계: 문장 구조 변경
        if similarity > 0.95:  # 매우 높은 유사도
            fixed_text = self._apply_structure_changes(fixed_text)
        
        # 3단계: 표현 방식 변경
        if similarity > 0.92:
            fixed_text = self._apply_expression_changes(fixed_text)
        
        # 4단계: 문장 순서 조정
        if similarity > 0.90:
            fixed_text = self._apply_sentence_reordering(fixed_text)
        
        return fixed_text
    
    def _apply_synonym_replacement(self, text: str) -> str:
        """동의어 교체 적용"""
        result = text
        
        for original, synonyms in self.plagiarism_synonyms.items():
            if original in result:
                # 가장 적절한 동의어 선택 (문맥 고려)
                best_synonym = self._select_best_synonym(original, synonyms, result)
                result = result.replace(original, best_synonym)
                print(f"  🔄 동의어 교체: '{original}' → '{best_synonym}'")
        
        return result
    
    def _select_best_synonym(self, original: str, synonyms: List[str], context: str) -> str:
        """문맥에 맞는 최적의 동의어 선택"""
        # 문맥 분석을 통한 동의어 선택
        if "학술" in context or "연구" in context:
            # 학술적 맥락
            academic_synonyms = [s for s in synonyms if len(s) > 2]
            return random.choice(academic_synonyms) if academic_synonyms else synonyms[0]
        elif "비즈니스" in context or "경영" in context:
            # 비즈니스 맥락
            business_synonyms = [s for s in synonyms if "경영" in s or "비즈니스" in s]
            return business_synonyms[0] if business_synonyms else synonyms[0]
        else:
            # 일반적 맥락
            return random.choice(synonyms)
    
    def _apply_structure_changes(self, text: str) -> str:
        """문장 구조 변경 적용"""
        result = text
        
        for pattern_type, patterns in self.structure_patterns.items():
            for pattern, replacement in patterns:
                if re.search(pattern, result):
                    result = re.sub(pattern, replacement, result)
                    print(f"  🔄 구조 변경 ({pattern_type}): 적용됨")
                    break  # 한 번만 적용
        
        return result
    
    def _apply_expression_changes(self, text: str) -> str:
        """표현 방식 변경 적용"""
        result = text
        
        # 학술적 표현 강화
        for original, enhanced in self.expression_changes["academic_enhancement"].items():
            if original in result:
                result = result.replace(original, enhanced)
                print(f"  🎓 학술적 강화: '{original}' → '{enhanced}'")
        
        return result
    
    def _apply_sentence_reordering(self, text: str) -> str:
        """문장 순서 조정"""
        sentences = text.split('.')
        if len(sentences) > 2:
            # 간단한 문장 순서 변경
            sentences[0], sentences[1] = sentences[1], sentences[0]
            result = '.'.join(sentences)
            print(f"  🔄 문장 순서 변경 적용")
            return result
        return text
    
    def _estimate_similarity_reduction(self, original: str, fixed: str) -> float:
        """수정 후 예상 유사도 계산"""
        # 간단한 유사도 계산 (실제로는 더 복잡한 알고리즘 필요)
        original_words = set(original.split())
        fixed_words = set(fixed.split())
        
        intersection = len(original_words & fixed_words)
        union = len(original_words | fixed_words)
        
        if union == 0:
            return 0.0
        
        jaccard_similarity = intersection / union
        
        # 구조 변경 등을 고려하여 추가 감소
        structure_reduction = 0.1 if len(original) != len(fixed) else 0.05
        
        return max(0.0, jaccard_similarity - structure_reduction)
    
    def apply_fixes_to_full_text(self, original_text: str, fixes: List[PlagiarismFix]) -> str:
        """전체 텍스트에 수정사항 적용"""
        result_text = original_text
        
        # 인덱스 역순으로 정렬하여 적용 (뒤에서부터 수정)
        sorted_fixes = sorted(fixes, key=lambda x: x.start_index, reverse=True)
        
        for fix in sorted_fixes:
            # 텍스트 교체
            result_text = (
                result_text[:fix.start_index] + 
                fix.fixed_segment + 
                result_text[fix.end_index:]
            )
            
            print(f"✅ 적용됨: {fix.similarity_before:.1%} → {fix.similarity_after:.1%}")
        
        return result_text
    
    def generate_fix_report(self, fixes: List[PlagiarismFix]) -> Dict:
        """수정 보고서 생성"""
        if not fixes:
            return {
                "total_fixes": 0,
                "average_similarity_reduction": 0,
                "fixes": []
            }
        
        total_reduction = sum(fix.similarity_before - fix.similarity_after for fix in fixes)
        average_reduction = total_reduction / len(fixes)
        
        return {
            "total_fixes": len(fixes),
            "average_similarity_reduction": average_reduction,
            "total_similarity_reduction": total_reduction,
            "fixes": [
                {
                    "original": fix.original_segment[:100] + "..." if len(fix.original_segment) > 100 else fix.original_segment,
                    "fixed": fix.fixed_segment[:100] + "..." if len(fix.fixed_segment) > 100 else fix.fixed_segment,
                    "similarity_before": f"{fix.similarity_before:.1%}",
                    "similarity_after": f"{fix.similarity_after:.1%}",
                    "reduction": f"{fix.similarity_before - fix.similarity_after:.1%}",
                    "fix_type": fix.fix_type,
                    "confidence": f"{fix.confidence:.1%}"
                }
                for fix in fixes
            ]
        }

if __name__ == "__main__":
    # 테스트
    fixer = AIPlagiarismFixer()
    
    test_text = "인공지능은 현대 사회에서 중요한 역할을 한다. 연구 결과에 따르면 새로운 기술이 제시되었다."
    test_matches = [
        {
            "start_index": 0,
            "end_index": 30,
            "similarity_score": 0.95
        }
    ]
    
    fixes = fixer.fix_plagiarized_text(test_text, test_matches)
    report = fixer.generate_fix_report(fixes)
    
    print("\n📊 수정 보고서:")
    print(f"총 수정: {report['total_fixes']}개")
    print(f"평균 유사도 감소: {report['average_similarity_reduction']:.1%}")