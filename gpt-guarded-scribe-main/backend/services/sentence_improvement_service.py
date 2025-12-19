#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from typing import Dict, List, Optional
import re
import json
from dataclasses import dataclass

@dataclass
class ImprovementSuggestion:
    """개선 제안 데이터 클래스"""
    original_text: str
    improved_text: str
    improvement_type: str
    confidence_score: float
    explanation: str
    position_start: int
    position_end: int

class SentenceImprovementService:
    """AI 기반 문장 개선 서비스"""
    
    def __init__(self):
        # 고급 동의어 사전 - 더 포괄적이고 실용적
        self.advanced_synonyms = {
            # 동사
            "분석": ["검토", "고찰", "탐구", "살펴봄", "연구", "조사"],
            "분석하다": ["검토하다", "고찰하다", "탐구하다", "살펴보다", "연구하다", "조사하다"],
            "발전": ["진보", "향상", "개선", "성장", "도약", "발달"],
            "발전하다": ["진보하다", "향상되다", "개선되다", "성장하다", "도약하다", "발달하다"],
            "변화": ["전환", "개변", "수정", "혁신", "변동", "전환"],
            "변화하다": ["전환되다", "바뀌다", "개변되다", "수정되다", "혁신되다"],
            "연구": ["탐구", "조사", "검토", "고찰", "분석"],
            "연구하다": ["탐구하다", "조사하다", "검토하다", "고찰하다", "분석하다"],
            "제시": ["제안", "주장", "표명", "건의", "언급"],
            "제시하다": ["제안하다", "내세우다", "주장하다", "표명하다", "건의하다"],
            "나타나다": ["드러나다", "보이다", "발현되다", "표출되다", "출현하다"],
            "증가": ["확대", "성장", "상승", "팽창", "신장"],
            "증가하다": ["늘어나다", "확대되다", "성장하다", "상승하다", "팽창하다"],
            "감소": ["축소", "하락", "저하", "위축", "줄어듦"],
            "감소하다": ["줄어들다", "축소되다", "하락하다", "저하되다", "위축되다"],
            
            # 형용사
            "중요한": ["핵심적인", "필수적인", "결정적인", "주요한", "중대한", "의미있는"],
            "중요하다": ["핵심적이다", "필수적이다", "결정적이다", "주요하다", "중대하다", "의미있다"],
            "다양한": ["여러", "각종", "다양", "갖가지", "온갖"],
            "새로운": ["신규", "혁신적인", "최신", "참신한", "새롭게"],
            "효과적인": ["유효한", "효율적인", "성공적인", "유용한", "실효성 있는"],
            
            # 명사
            "방법": ["수단", "방식", "기법", "접근법", "절차"],
            "결과": ["성과", "산출물", "결론", "도출", "귀결"],
            "문제": ["과제", "이슈", "사안", "쟁점", "현안"],
            "사회": ["공동체", "집단", "커뮤니티", "사회구조", "사회체계"],
            "기술": ["테크놀로지", "공학", "기법", "방법론", "노하우"],
            "인공지능": ["AI", "머신러닝", "지능형 시스템", "인공 지능", "스마트 시스템"],
            "현대": ["오늘날", "현재", "당대", "지금", "현시대"],
            "기업": ["회사", "조직", "업체", "법인", "기관"],
            "생존": ["존속", "유지", "지속", "보전", "연명"],
            "성장": ["발전", "확장", "신장", "증진", "도약"],
            "필수": ["핵심", "중요", "주요", "근본", "기본"],
            "요소": ["인자", "구성", "성분", "항목", "요인"],
            "융합": ["결합", "통합", "합성", "조합", "접목"],
            "비즈니스": ["사업", "업무", "상업", "경영", "기업활동"],
            "모델": ["방식", "형태", "체계", "패턴", "시스템"],
            "고객": ["소비자", "이용자", "사용자", "구매자", "클라이언트"],
            "경험": ["체험", "경력", "노하우", "실제", "실습"],
            "창출": ["생성", "발생", "조성", "형성", "구현"],
            "클라우드": ["구름", "원격", "온라인", "네트워크", "가상"],
            "컴퓨팅": ["연산", "처리", "계산", "정보처리", "데이터처리"],
            "새로운": ["혁신적인", "참신한", "최신의", "신규", "첨단"],
            "통해": ["통하여", "거쳐", "이용하여", "활용하여", "매개로"],
            
            # 연결어/부사
            "또한": ["더불어", "아울러", "동시에", "뿐만 아니라", "그리고"],
            "그러나": ["하지만", "다만", "반면에", "그럼에도 불구하고", "그렇지만"],
            "따라서": ["그러므로", "그런 이유로", "이에 따라", "결과적으로", "그리하여"],
            "즉": ["다시 말해", "바꾸어 말하면", "요약하면", "구체적으로", "말하자면"],
            "특히": ["특별히", "무엇보다", "주로", "특히나", "더욱이"],
            "매우": ["상당히", "극도로", "대단히", "굉장히", "현저히"],
        }
        
        # 문체 개선 패턴
        self.style_patterns = {
            # 수동태 → 능동태
            "passive_to_active": [
                (r'(\w+)이 (\w+)되었다', r'\2가 \1을 이루었다'),
                (r'(\w+)가 (\w+)되다', r'\1이 \2를 만들다'),
                (r'(\w+)에 의해 (\w+)되다', r'\1이 \2를 하다'),
            ],
            
            # 명사형 → 동사형
            "noun_to_verb": [
                (r'(\w+)의 (\w+)이 (\w+)이다', r'\1이 \2하여 \3하다'),
                (r'(\w+)에 대한 (\w+)', r'\1을 \2하는 것'),
            ],
            
            # 연결어 다양화
            "connector_variety": {
                "그러나": ["하지만", "다만", "반면에", "그럼에도 불구하고"],
                "따라서": ["그러므로", "그런 이유로", "이에 따라", "결과적으로"],
                "또한": ["더불어", "아울러", "동시에", "뿐만 아니라"],
                "즉": ["다시 말해", "바꾸어 말하면", "요약하면", "구체적으로"],
                "예를 들어": ["가령", "구체적으로", "실례로", "이를테면"],
            }
        }
        
        # 학술 표현 개선
        self.academic_improvements = {
            "~이다": ["~라고 할 수 있다", "~로 파악된다", "~것으로 보인다", "~로 여겨진다"],
            "~있다": ["~존재한다", "~나타난다", "~관찰된다", "~확인된다"],
            "~같다": ["~유사하다", "~비슷하다", "~동일하다", "~닮아있다"],
            "많다": ["다수이다", "상당하다", "풍부하다", "다양하다"],
            "적다": ["소수이다", "제한적이다", "미흡하다", "부족하다"],
        }

    def generate_improvement_suggestions(self, text: str, plagiarism_matches: List[Dict] = None) -> List[ImprovementSuggestion]:
        """종합적인 문장 개선 제안 생성"""
        print(f"🔧 문장 개선 시작: 텍스트 길이={len(text)}, 표절 매치={len(plagiarism_matches) if plagiarism_matches else 0}개")
        suggestions = []
        
        # 1. 표절 구간 우선 개선
        if plagiarism_matches:
            plagiarism_suggestions = self._improve_plagiarized_sections(text, plagiarism_matches)
            print(f"📋 표절 구간 개선: {len(plagiarism_suggestions)}개")
            suggestions.extend(plagiarism_suggestions)
        
        # 2. 동의어 교체 제안
        synonym_suggestions = self._suggest_synonym_replacements(text)
        print(f"📚 동의어 교체 제안: {len(synonym_suggestions)}개")
        suggestions.extend(synonym_suggestions)
        
        # 3. 문체 개선 제안
        style_suggestions = self._suggest_style_improvements(text)
        print(f"✨ 문체 개선 제안: {len(style_suggestions)}개")
        suggestions.extend(style_suggestions)
        
        # 4. 학술적 표현 개선
        academic_suggestions = self._suggest_academic_improvements(text)
        print(f"🎓 학술적 표현 개선: {len(academic_suggestions)}개")
        suggestions.extend(academic_suggestions)
        
        # 5. 문장 구조 개선
        structure_suggestions = self._suggest_sentence_restructuring(text)
        print(f"🔧 문장 구조 개선: {len(structure_suggestions)}개")
        suggestions.extend(structure_suggestions)
        
        # 6. 직접적인 문장 변환 (확실한 변화 보장)
        direct_suggestions = self._generate_direct_improvements(text)
        print(f"🎯 직접 문장 변환: {len(direct_suggestions)}개")
        suggestions.extend(direct_suggestions)
        
        print(f"📊 총 제안 생성: {len(suggestions)}개")
        
        # 중복 제거 및 점수순 정렬
        suggestions = self._deduplicate_and_rank(suggestions)
        print(f"🔍 중복 제거 후: {len(suggestions)}개")
        
        # 각 제안의 내용을 로그로 출력
        for i, suggestion in enumerate(suggestions[:5]):  # 상위 5개만
            print(f"  {i+1}. [{suggestion.improvement_type}] '{suggestion.original_text}' → '{suggestion.improved_text}'")
        
        return suggestions[:10]  # 상위 10개만 반환

    def _improve_plagiarized_sections(self, text: str, matches: List[Dict]) -> List[ImprovementSuggestion]:
        """표절된 구간에 대한 개선 제안"""
        suggestions = []
        
        for match in matches:
            matched_text = match.get('matched_text', '')
            similarity_score = match.get('similarity_score', 0)
            
            if similarity_score > 60 and len(matched_text) > 10:
                # 패러프레이징 제안
                improved_versions = self._generate_paraphrases(matched_text)
                
                for improved in improved_versions:
                    position = text.find(matched_text)
                    if position != -1:
                        suggestions.append(ImprovementSuggestion(
                            original_text=matched_text,
                            improved_text=improved,
                            improvement_type="표절 구간 패러프레이징",
                            confidence_score=0.9,
                            explanation=f"유사도 {similarity_score:.1f}% 구간을 다른 표현으로 변경하여 독창성을 높입니다.",
                            position_start=position,
                            position_end=position + len(matched_text)
                        ))
        
        return suggestions

    def _suggest_synonym_replacements(self, text: str) -> List[ImprovementSuggestion]:
        """스마트한 동의어 교체 제안"""
        suggestions = []
        processed_positions = set()  # 중복 위치 방지
        
        # 문맥에 맞는 동의어 선택
        for original, synonyms in self.advanced_synonyms.items():
            # 정확한 단어 매치 (부분 문자열 방지)
            pattern = r'\b' + re.escape(original) + r'\b'
            matches = list(re.finditer(pattern, text))
            
            for match in matches:
                pos = match.start()
                if pos in processed_positions:
                    continue
                    
                processed_positions.add(pos)
                
                # 문맥 분석하여 최적의 동의어 선택
                context = self._get_context(text, pos, len(original))
                best_synonyms = self._select_contextual_synonyms(original, synonyms, context)
                
                for i, synonym in enumerate(best_synonyms[:2]):  # 최대 2개
                    if synonym != original:  # 원문과 다른 경우만
                        # 문장 전체를 교체한 버전 생성
                        improved_sentence = text[:pos] + synonym + text[pos + len(original):]
                        
                        confidence = 0.85 - (i * 0.1)  # 첫 번째가 더 높은 신뢰도
                        
                        suggestions.append(ImprovementSuggestion(
                            original_text=original,
                            improved_text=synonym,
                            improvement_type="동의어 교체",
                            confidence_score=confidence,
                            explanation=f"'{original}'을 '{synonym}'로 교체하여 학술적 표현을 강화하고 어휘의 다양성을 높입니다.",
                            position_start=pos,
                            position_end=pos + len(original)
                        ))
        
        return suggestions
    
    def _get_context(self, text: str, position: int, word_length: int) -> str:
        """단어 주변 문맥 추출"""
        start = max(0, position - 20)
        end = min(len(text), position + word_length + 20)
        return text[start:end]
    
    def _select_contextual_synonyms(self, original: str, synonyms: List[str], context: str) -> List[str]:
        """문맥에 맞는 동의어 선택"""
        scored_synonyms = []
        
        for synonym in synonyms:
            score = 1.0  # 기본 점수
            
            # 문맥 적합성 검사
            if "학술" in context or "연구" in context:
                # 학술적 맥락에서는 formal한 표현 선호
                if synonym in ["고찰", "탐구", "검토", "분석"]:
                    score += 0.3
            
            if "현대" in context or "사회" in context:
                # 사회과학적 맥락
                if synonym in ["현시대", "공동체", "집단"]:
                    score += 0.2
            
            if "기술" in context or "발전" in context:
                # 기술적 맥락
                if synonym in ["혁신", "진보", "도약"]:
                    score += 0.2
            
            # 길이 기반 점수 (너무 길거나 짧은 것 페널티)
            length_ratio = len(synonym) / len(original)
            if 0.8 <= length_ratio <= 1.5:
                score += 0.1
            else:
                score -= 0.2
            
            scored_synonyms.append((synonym, score))
        
        # 점수순으로 정렬
        scored_synonyms.sort(key=lambda x: x[1], reverse=True)
        return [syn for syn, _ in scored_synonyms]

    def _suggest_style_improvements(self, text: str) -> List[ImprovementSuggestion]:
        """문체 개선 제안"""
        suggestions = []
        
        # 수동태 → 능동태 변환
        for pattern, replacement in self.style_patterns["passive_to_active"]:
            matches = re.finditer(pattern, text)
            for match in matches:
                original = match.group(0)
                improved = re.sub(pattern, replacement, original)
                
                suggestions.append(ImprovementSuggestion(
                    original_text=original,
                    improved_text=improved,
                    improvement_type="수동태 → 능동태",
                    confidence_score=0.85,
                    explanation="수동태를 능동태로 변경하여 문장을 더욱 명확하고 직접적으로 만듭니다.",
                    position_start=match.start(),
                    position_end=match.end()
                ))
        
        # 연결어 다양화
        for original, alternatives in self.style_patterns["connector_variety"].items():
            if original in text:
                positions = [m.start() for m in re.finditer(re.escape(original), text)]
                for pos in positions:
                    for alt in alternatives[:2]:
                        suggestions.append(ImprovementSuggestion(
                            original_text=original,
                            improved_text=alt,
                            improvement_type="연결어 다양화",
                            confidence_score=0.75,
                            explanation=f"'{original}'을 '{alt}'로 변경하여 문체를 다양화합니다.",
                            position_start=pos,
                            position_end=pos + len(original)
                        ))
        
        return suggestions

    def _suggest_academic_improvements(self, text: str) -> List[ImprovementSuggestion]:
        """학술적 표현 개선"""
        suggestions = []
        
        for pattern, improvements in self.academic_improvements.items():
            if pattern in text:
                positions = [m.start() for m in re.finditer(re.escape(pattern), text)]
                for pos in positions:
                    for improvement in improvements[:2]:
                        suggestions.append(ImprovementSuggestion(
                            original_text=pattern,
                            improved_text=improvement,
                            improvement_type="학술적 표현 개선",
                            confidence_score=0.8,
                            explanation=f"'{pattern}'를 '{improvement}'로 변경하여 학술적 정확성을 높입니다.",
                            position_start=pos,
                            position_end=pos + len(pattern)
                        ))
        
        return suggestions

    def _suggest_sentence_restructuring(self, text: str) -> List[ImprovementSuggestion]:
        """문장 구조 개선"""
        suggestions = []
        sentences = [s.strip() for s in text.split('.') if s.strip()]
        
        current_pos = 0
        for sentence in sentences:
            if len(sentence) > 50:  # 긴 문장만 대상
                restructured = self._restructure_long_sentence(sentence)
                if restructured and restructured != sentence:
                    position = text.find(sentence, current_pos)
                    if position != -1:
                        suggestions.append(ImprovementSuggestion(
                            original_text=sentence,
                            improved_text=restructured,
                            improvement_type="문장 구조 개선",
                            confidence_score=0.7,
                            explanation="긴 문장을 분할하거나 구조를 개선하여 가독성을 높입니다.",
                            position_start=position,
                            position_end=position + len(sentence)
                        ))
            current_pos = text.find(sentence, current_pos) + len(sentence)
        
        return suggestions

    def _generate_paraphrases(self, text: str) -> List[str]:
        """텍스트의 효과적인 패러프레이즈 생성"""
        paraphrases = []
        original = text.strip()
        
        # 1. 동의어 다중 적용 (더 자연스럽게)
        multi_synonym = original
        synonym_count = 0
        for word, synonyms in self.advanced_synonyms.items():
            if word in multi_synonym and synonym_count < 3:  # 최대 3개까지만
                multi_synonym = multi_synonym.replace(word, synonyms[0], 1)
                synonym_count += 1
        if multi_synonym != original:
            paraphrases.append(multi_synonym)
        
        # 2. 문체 변환 패턴들
        style_variants = []
        
        # 단정적 → 추정적 표현
        if "이다" in original:
            style_variants.append(original.replace("이다", "로 여겨진다"))
            style_variants.append(original.replace("이다", "라고 할 수 있다"))
        
        if "있다" in original:
            style_variants.append(original.replace("있다", "존재한다"))
            style_variants.append(original.replace("있다", "나타난다"))
        
        if "된다" in original:
            style_variants.append(original.replace("된다", "이루어진다"))
            style_variants.append(original.replace("된다", "진행된다"))
        
        # 능동/수동 변환
        if "에 의해" in original:
            # "A에 의해 B가 된다" → "A가 B를 만든다"
            passive_pattern = re.sub(r'(\w+)에 의해 (\w+)가 (\w+)된다', r'\1가 \2를 \3시킨다', original)
            if passive_pattern != original:
                style_variants.append(passive_pattern)
        
        # 3. 구조적 재배열
        sentences = original.split('.')
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) > 10:
                # 연결어가 있는 경우 문장 분할
                if any(conn in sentence for conn in ["그리고", "또한", "하지만", "그러나"]):
                    for conn in ["그리고", "또한", "하지만", "그러나"]:
                        if conn in sentence:
                            parts = sentence.split(conn, 1)
                            if len(parts) == 2:
                                restructured = f"{parts[0].strip()}. {conn} {parts[1].strip()}"
                                if restructured != original:
                                    style_variants.append(restructured)
                
                # 명사구 → 동사구 변환
                if "의" in sentence:
                    # "A의 B" → "A에서 나타나는 B"
                    noun_to_verb = re.sub(r'(\w+)의 (\w+)', r'\1에서 나타나는 \2', sentence)
                    if noun_to_verb != sentence:
                        style_variants.append(noun_to_verb)
        
        # 4. 학술적 표현 강화
        academic_version = original
        academic_replacements = {
            "많다": "다수를 차지한다",
            "적다": "소수에 그친다",
            "좋다": "긍정적이다",
            "나쁘다": "부정적이다",
            "크다": "상당한 규모이다",
            "작다": "제한적인 범위이다",
            "빠르다": "신속하게 진행된다",
            "느리다": "점진적으로 나타난다"
        }
        
        for simple, academic in academic_replacements.items():
            if simple in academic_version:
                academic_version = academic_version.replace(simple, academic)
        
        if academic_version != original:
            style_variants.append(academic_version)
        
        # 5. 연결어 다양화
        connector_version = original
        for old_conn, new_conns in self.style_patterns["connector_variety"].items():
            if old_conn in connector_version:
                connector_version = connector_version.replace(old_conn, new_conns[0])
                break
        
        if connector_version != original:
            style_variants.append(connector_version)
        
        # 중복 제거 및 유효한 변형만 선택
        paraphrases.extend([v for v in style_variants if v != original and v.strip()])
        
        # 복합 변형 (동의어 + 문체 변경)
        if paraphrases:
            base_variant = paraphrases[0] if paraphrases else original
            combo_variant = base_variant
            
            # 추가 동의어 적용
            for word, synonyms in list(self.advanced_synonyms.items())[:3]:
                if word in combo_variant and len(synonyms) > 1:
                    combo_variant = combo_variant.replace(word, synonyms[1], 1)
            
            if combo_variant != original and combo_variant not in paraphrases:
                paraphrases.append(combo_variant)
        
        # 최종 검증: 의미있는 변화가 있는 것만 반환
        valid_paraphrases = []
        for para in paraphrases:
            # 최소 3글자 이상 차이가 나야 함
            if para and len(para.strip()) > 0 and abs(len(para) - len(original)) >= 3:
                valid_paraphrases.append(para)
            # 또는 단어가 실제로 바뀌었는지 확인
            elif para and para != original:
                original_words = set(original.split())
                para_words = set(para.split())
                if len(original_words.symmetric_difference(para_words)) >= 1:
                    valid_paraphrases.append(para)
        
        return valid_paraphrases[:3]  # 최대 3개만 반환
        if "의" in original:
            # "A의 B" → "A에서 B"
            modified = re.sub(r'(\w+)의 (\w+)', r'\1에서 \2', original)
            paraphrases.append(modified)
        
        # 중복 제거
        unique_paraphrases = list(set([p for p in paraphrases if p != original and p.strip()]))
        return unique_paraphrases[:3]

    def _restructure_long_sentence(self, sentence: str) -> Optional[str]:
        """긴 문장 구조 개선"""
        if len(sentence) < 50:
            return None
        
        # 접속사로 문장 분할
        conjunctions = ["그리고", "또한", "하지만", "그러나", "따라서"]
        
        for conj in conjunctions:
            if conj in sentence:
                parts = sentence.split(conj, 1)
                if len(parts) == 2 and len(parts[0].strip()) > 10 and len(parts[1].strip()) > 10:
                    return f"{parts[0].strip()}. {conj} {parts[1].strip()}"
        
        # 긴 문장을 두 부분으로 나누기
        mid_point = len(sentence) // 2
        split_candidates = ['. ', ', ', ' 및 ', ' 그리고 ']
        
        for candidate in split_candidates:
            pos = sentence.find(candidate, mid_point - 20, mid_point + 20)
            if pos != -1:
                part1 = sentence[:pos]
                part2 = sentence[pos + len(candidate):]
                return f"{part1}. {part2.capitalize()}"
        
        return None

    def _deduplicate_and_rank(self, suggestions: List[ImprovementSuggestion]) -> List[ImprovementSuggestion]:
        """중복 제거 및 점수순 정렬"""
        # 위치 기반 중복 제거
        unique_suggestions = {}
        
        for suggestion in suggestions:
            key = (suggestion.position_start, suggestion.position_end, suggestion.improvement_type)
            if key not in unique_suggestions or suggestion.confidence_score > unique_suggestions[key].confidence_score:
                unique_suggestions[key] = suggestion
        
        # 신뢰도 점수순 정렬
        ranked_suggestions = sorted(unique_suggestions.values(), key=lambda x: x.confidence_score, reverse=True)
        
        return ranked_suggestions

    def format_suggestions_for_api(self, suggestions: List[ImprovementSuggestion]) -> Dict:
        """API 응답용 포맷으로 변환"""
        formatted = {
            "total_suggestions": len(suggestions),
            "improvement_categories": {},
            "suggestions": []
        }
        
        # 카테고리별 그룹화
        for suggestion in suggestions:
            category = suggestion.improvement_type
            if category not in formatted["improvement_categories"]:
                formatted["improvement_categories"][category] = 0
            formatted["improvement_categories"][category] += 1
            
            formatted["suggestions"].append({
                "original_text": suggestion.original_text,
                "improved_text": suggestion.improved_text,
                "type": suggestion.improvement_type,
                "confidence": round(suggestion.confidence_score * 100, 1),
                "explanation": suggestion.explanation,
                "position": {
                    "start": suggestion.position_start,
                    "end": suggestion.position_end
                }
            })
        
        return formatted

    def _generate_direct_improvements(self, text: str) -> List[ImprovementSuggestion]:
        """범용적이고 지능적인 문장 변환 제안"""
        suggestions = []
        print(f"🎯 직접 변환 시작: '{text[:50]}...'")
        
        # 1. 동의어 사전을 활용한 범용 교체
        applied_replacements = set()  # 중복 방지
        
        for original_word, synonyms in self.advanced_synonyms.items():
            if original_word in text and original_word not in applied_replacements:
                # 각 동의어에 대해 제안 생성
                for synonym in synonyms[:2]:  # 최대 2개씩
                    if synonym != original_word:
                        position = text.find(original_word)
                        if position != -1:
                            suggestions.append(ImprovementSuggestion(
                                original_text=original_word,
                                improved_text=synonym,
                                improvement_type="동의어 교체",
                                confidence_score=0.85,
                                explanation=f"'{original_word}'을 '{synonym}'로 변경하여 어휘를 다양화합니다.",
                                position_start=position,
                                position_end=position + len(original_word)
                            ))
                applied_replacements.add(original_word)
        
        # 2. 범용 문체 변환 패턴
        universal_patterns = [
            # 시제 변환
            ("되었습니다", "되고 있습니다", "시제 변경", "과거형을 현재 진행형으로 변경하여 현재성을 강조합니다."),
            ("했습니다", "하고 있습니다", "시제 변경", "과거형을 현재 진행형으로 변경하여 지속성을 나타냅니다."),
            ("되었다", "되고 있다", "시제 변경", "완료형을 진행형으로 변경하여 동적인 느낌을 줍니다."),
            
            # 어미 변화
            ("입니다", "라고 할 수 있습니다", "표현 완화", "단정적 표현을 추정적 표현으로 변경하여 학술적 어조를 만듭니다."),
            ("이다", "로 여겨진다", "객관화", "주관적 서술을 객관적 표현으로 변경합니다."),
            ("있다", "존재한다", "격식체", "일반적 표현을 격식 있는 표현으로 변경합니다."),
            
            # 연결어 다양화
            ("그리고", "또한", "연결어 변경", "단순한 연결어를 학술적 연결어로 변경합니다."),
            ("하지만", "그러나", "연결어 격상", "구어체 연결어를 문어체로 변경합니다."),
            ("그래서", "따라서", "논리 연결", "일상어를 논리적 연결어로 변경합니다."),
            
            # 수동/능동 변환
            ("이루어지다", "수행하다", "능동화", "수동적 표현을 능동적으로 변경합니다."),
            ("만들어지다", "창조하다", "능동화", "피동 표현을 능동 표현으로 강화합니다."),
            
            # 학술적 표현 강화
            ("중요하다", "핵심적이다", "학술 표현", "일반적 표현을 학술적 용어로 강화합니다."),
            ("많다", "다수를 차지한다", "정량화", "모호한 표현을 구체적으로 변경합니다."),
            ("좋다", "긍정적이다", "객관화", "주관적 평가를 객관적 표현으로 변경합니다."),
        ]
        
        # 3. 문장별 처리로 더 자연스러운 변환
        sentences = [s.strip() for s in text.replace('.', '.\n').split('\n') if s.strip()]
        
        for sentence in sentences:
            if len(sentence) < 5:  # 너무 짧은 것 제외
                continue
                
            position_start = text.find(sentence)
            if position_start == -1:
                continue
            
            sentence_suggestions = []
            
            # 각 패턴 적용
            for old_pattern, new_pattern, change_type, explanation in universal_patterns:
                if old_pattern in sentence:
                    improved_sentence = sentence.replace(old_pattern, new_pattern)
                    if improved_sentence != sentence:
                        sentence_suggestions.append((improved_sentence, change_type, explanation))
            
            # 문장 레벨 개선: 복합 동의어 적용
            compound_improved = sentence
            change_count = 0
            changes_made = []
            
            for word, synonyms in list(self.advanced_synonyms.items())[:10]:  # 상위 10개만
                if word in compound_improved and change_count < 3:  # 최대 3개 변경
                    compound_improved = compound_improved.replace(word, synonyms[0], 1)
                    changes_made.append(f"'{word}'→'{synonyms[0]}'")
                    change_count += 1
            
            if compound_improved != sentence and change_count > 0:
                sentence_suggestions.append((
                    compound_improved, 
                    "복합 동의어 적용", 
                    f"{change_count}개 용어를 동의어로 교체: {', '.join(changes_made)}"
                ))
            
            # 문장 구조 변경
            if len(sentence.split()) > 5:  # 충분히 긴 문장만
                # 어순 변경 시도
                words = sentence.split()
                if len(words) >= 4:
                    # 간단한 어순 변경: 주어와 서술어 사이에 부사구가 있는 경우
                    if "에서" in sentence or "에게" in sentence or "으로" in sentence:
                        # "A에서 B를 C한다" → "B를 A에서 C한다" 같은 변경
                        restructured = self._try_sentence_restructure(sentence)
                        if restructured and restructured != sentence:
                            sentence_suggestions.append((
                                restructured, 
                                "문장 구조 변경", 
                                "어순을 조정하여 강조점을 변경했습니다."
                            ))
            
            # 제안을 실제 suggestions에 추가
            for improved_text, improvement_type, explanation in sentence_suggestions[:3]:  # 문장당 최대 3개
                suggestions.append(ImprovementSuggestion(
                    original_text=sentence,
                    improved_text=improved_text,
                    improvement_type=improvement_type,
                    confidence_score=0.8,
                    explanation=explanation,
                    position_start=position_start,
                    position_end=position_start + len(sentence)
                ))
        
        print(f"📊 직접 변환 완료: {len(suggestions)}개 제안 생성")
        return suggestions[:15]  # 최대 15개로 제한
    
    def _try_sentence_restructure(self, sentence: str) -> str:
        """문장 구조 변경 시도"""
        # 간단한 구조 변경 규칙들
        if "통해" in sentence and "을" in sentence:
            # "A를 통해 B를 C한다" → "A로 B를 C한다"
            return sentence.replace("을 통해", "로").replace("를 통해", "로")
        
        if "에 의해" in sentence:
            # "A에 의해 B가 C된다" → "A가 B를 C시킨다"
            return sentence.replace("에 의해", "가").replace("된다", "시킨다")
        
        if sentence.count("이") >= 2 or sentence.count("가") >= 2:
            # 중복된 주격조사 정리
            return sentence.replace("이 이", "이").replace("가 가", "가")
        
        return sentence  # 변경할 수 없으면 원본 반환

# 사용 예시
if __name__ == "__main__":
    service = SentenceImprovementService()
    
    sample_text = """
    인공지능 기술의 발전은 현대 사회에 중요한 영향을 미치고 있다. 
    이러한 기술은 다양한 분야에서 활용되고 있으며, 특히 의료 분야에서의 
    활용도가 높다. 또한 교육 분야에서도 인공지능이 활용되고 있다.
    """
    
    suggestions = service.generate_improvement_suggestions(sample_text.strip())
    formatted_result = service.format_suggestions_for_api(suggestions)
    
    print("🚀 문장 개선 제안:")
    print(json.dumps(formatted_result, ensure_ascii=False, indent=2))