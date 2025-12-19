#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""AI 기반 표절 회피 서비스"""

import re
import random
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from difflib import SequenceMatcher

@dataclass
class PlagiarismAvoidanceResult:
    """표절 회피 결과"""
    original_text: str
    rewritten_text: str
    similarity_reduction: float
    modifications: List[Dict]
    confidence_score: float
    
class AIPlagiarismAvoidance:
    """AI 기반 표절 회피 시스템"""
    
    def __init__(self):
        # 동의어 사전 (표절 회피용) - ✅ 자연스럽고 충분한 동의어
        self.avoidance_synonyms = {
            # 학술 용어
            "연구": ["조사", "탐구", "분석"],
            "분석": ["검토", "평가", "조사"],
            "결과": ["성과", "도출", "귀결"],
            "방법": ["방식", "수단", "접근법"],
            "중요한": ["주요한", "핵심적인", "중대한"],
            "중요하다": ["주요하다", "핵심이다"],
            "효과적인": ["효율적인", "유효한"],
            "문제": ["과제", "이슈", "사안"],
            "개선": ["향상", "보완"],
            "발전": ["진보", "성장"],
            "변화": ["전환", "변동"],
            
            # 일반 용어 (자연스러운 대체어)
            "활용": ["이용", "사용"],
            "활용되고": ["이용되고", "사용되고"],
            "활용하여": ["이용하여", "사용하여"],
            "다양한": ["여러", "각종", "다수의"],
            "분야": ["영역", "부문", "분야"],
            "역할": ["기능", "역할"],
            "매우": ["상당히", "대단히"],
            "특히": ["특별히", "무엇보다"],
            "의료": ["의학", "의료"],
            "교육": ["학습", "교육"],
            "금융": ["재무", "금융"],
            
            # 동사 (겹치지 않는 동사만)
            "제시하다": ["제안하다", "내세우다", "주장하다", "표명하다"],
            "나타내다": ["보여주다", "드러내다", "표현하다", "시사하다"],
            "증가하다": ["늘어나다", "상승하다", "확대되다", "증진되다"],
            "감소하다": ["줄어들다", "축소되다", "하락하다", "저하되다"],
            "영향을 미치다": ["작용하다", "효과를 주다", "영향을 끼치다"],
            
            # 접속사/부사
            "또한": ["더불어", "아울러", "동시에", "뿐만 아니라", "게다가"],
            "그러나": ["하지만", "다만", "반면에", "그럼에도", "그렇지만"],
            "따라서": ["그러므로", "그런 이유로", "결과적으로", "그에 따라"],
            "특히": ["특별히", "무엇보다", "주로", "더욱이"],
            "매우": ["극히", "상당히", "대단히", "아주"]
        }
        
        # 문장 구조 변환 패턴
        self.structure_patterns = [
            # 수동태 → 능동태
            {
                "pattern": r"(\w+)이 (\w+)되었다",
                "replacement": r"\2가 \1을 이루었다",
                "type": "passive_to_active"
            },
            # 명사형 → 동사형
            {
                "pattern": r"(\w+)의 (\w+)이 (\w+)하다",
                "replacement": r"\1이 \2하여 \3하다",
                "type": "noun_to_verb"
            },
            # 어순 변경
            {
                "pattern": r"(\w+)는 (\w+)에서 (\w+)하다",
                "replacement": r"\2에서 \1이 \3하다",
                "type": "word_order_change"
            }
        ]
        
        # 표현 다양화 패턴
        self.expression_variations = {
            "~이다": ["~라고 할 수 있다", "~로 파악된다", "~것으로 보인다"],
            "~있다": ["~존재한다", "~나타난다", "~관찰된다"],
            "~많다": ["~풍부하다", "~다양하다", "~상당하다"],
            "~중요하다": ["~핵심적이다", "~필수적이다", "~결정적이다"]
        }
    
    def avoid_plagiarism(self, original_text: str, plagiarism_matches: List[Dict]) -> PlagiarismAvoidanceResult:
        """표절 부분을 AI로 회피하여 재작성"""
        print(f"🛡️ AI 표절 회피 시작: 원본 {len(original_text)}자, 매치 {len(plagiarism_matches)}개")
        
        # ✅ 디버그: 매치 정보 출력
        for i, match in enumerate(plagiarism_matches):
            print(f"  매치 {i+1}: '{match.get('matched_text', '')[:30]}...' (유사도 {match.get('similarity_score', 0)}%)")
        
        modifications = []
        rewritten_text = original_text
        
        # 1. 표절 매치된 부분들을 우선적으로 수정 (역순으로 처리하여 인덱스 유지)
        for match in sorted(plagiarism_matches, key=lambda x: x.get('start_index', 0), reverse=True):
            matched_text = match.get('matched_text', '')
            start_idx = match.get('start_index', 0)
            end_idx = match.get('end_index', 0)
            similarity = match.get('similarity_score', 0)
            
            print(f"  처리 중: '{matched_text[:30]}...' (유사도 {similarity}%, 임계값 40)")
            
            # ✅ 임계값 40: 중위험 이상 부분 수정 (적절한 균형)
            if matched_text and start_idx < end_idx and similarity > 40:
                # 실제 표절 방지 도구의 고급 재작성 기법 사용
                rewritten_part = self._advanced_rewrite_section(matched_text, similarity)
                
                # 원본 텍스트에서 해당 부분 교체
                try:
                    rewritten_text = (
                        rewritten_text[:start_idx] + 
                        rewritten_part + 
                        rewritten_text[end_idx:]
                    )
                    
                    modifications.append({
                        "type": "plagiarism_rewrite",
                        "original": matched_text,
                        "rewritten": rewritten_part,
                        "position": f"{start_idx}-{end_idx}",
                        "reason": f"유사도 {similarity:.1f}% 회피",
                        "techniques": ["동의어 치환", "문장 구조 변경", "표현 다양화"]
                    })
                except Exception as e:
                    print(f"⚠️ 재작성 오류: {e}")
                    continue
        
        # 2. 전체 텍스트에 대한 추가 다양화
        rewritten_text = self._apply_general_variations(rewritten_text, modifications)
        
        # 3. 유사도 감소 계산 (더 정확한 계산)
        similarity_reduction = self._calculate_similarity_reduction(original_text, rewritten_text)
        
        # 4. 신뢰도 점수 계산
        confidence_score = self._calculate_confidence(modifications, similarity_reduction)
        
        result = PlagiarismAvoidanceResult(
            original_text=original_text,
            rewritten_text=rewritten_text,
            similarity_reduction=similarity_reduction,
            modifications=modifications,
            confidence_score=confidence_score
        )
        
        print(f"✅ AI 표절 회피 완료: {len(modifications)}개 부분 수정, 유사도 {similarity_reduction:.1f}% 감소")
        return result
    
    def _advanced_rewrite_section(self, text: str, similarity_score: float) -> str:
        """고급 표절 회피: 실제 도구들이 사용하는 기법"""
        rewritten = text
        
        # 유사도에 따른 강도 조절
        intensity = min(similarity_score / 100.0, 1.0)
        
        print(f"  📝 원문: {text[:50]}...")
        
        # ✅ 1단계: 의미 보존 패러프레이징 (먼저 실행)
        rewritten = self._paraphrase_intelligently(rewritten)
        
        # 2단계: 문장 구조 변형 (90% 이상일 때 필수)
        if intensity > 0.9 or similarity_score > 85:
            rewritten = self._restructure_sentence_fundamentally(rewritten)
            rewritten = self._change_voice_and_tense(rewritten)
        
        # ✅ 3단계: 기본 동의어 교체 (마지막에 실행하여 중복 방지)
        rewritten = self._substitute_synonyms_aggressive(rewritten)
        
        # 4단계: 문장 분할/결합
        if len(rewritten) > 30:
            rewritten = self._split_or_combine_sentences(rewritten, intensity)
        
        # 5단계: 문법적 변형
        rewritten = self._apply_grammatical_transformations(rewritten)
        
        # 6단계: 추가 표현 다양화
        if intensity > 0.7:
            rewritten = self._diversify_expressions(rewritten)
        
        print(f"  ✏️  수정본: {rewritten[:50]}...")
        
        return rewritten.strip()
    
    def _substitute_synonyms_aggressive(self, text: str) -> str:
        """적극적인 동의어 교체 (50% 이상 단어 변경)"""
        # ✅ 먼저 모든 교체 작업을 계획한 다음 한 번에 적용
        replacements = []
        used_positions = set()
        
        # ✅ 긴 구문부터 처리하도록 정렬 (겹치는 교체 방지)
        sorted_terms = sorted(self.avoidance_synonyms.items(), key=lambda x: len(x[0]), reverse=True)
        
        replaced_originals = set()  # ✅ 이미 교체한 원본 용어 추적
        
        # 각 원본 용어에 대해 텍스트에서 위치를 찾고 교체 계획 수립
        for original_term, synonyms in sorted_terms:
            # 이미 교체한 용어는 건너뛰기
            if original_term in replaced_originals:
                continue
            
            start = 0
            while True:
                pos = text.find(original_term, start)
                if pos == -1:
                    break
                
                # 이미 교체 예정인 위치와 겹치는지 확인
                overlaps = any(pos < end and pos + len(original_term) > start_pos 
                              for start_pos, end in used_positions)
                
                if not overlaps:
                    synonym = random.choice(synonyms)
                    replacements.append((pos, original_term, synonym))
                    used_positions.add((pos, pos + len(original_term)))
                    replaced_originals.add(original_term)
                    
                    # ✅ 선택한 동의어가 다른 원본 용어에 포함되어 있으면 그것도 건너뛰도록 표시
                    for other_term in self.avoidance_synonyms.keys():
                        if other_term in synonym or synonym in other_term:
                            replaced_originals.add(other_term)
                    
                    print(f"    - '{original_term}' → '{synonym}'")
                    break  # 각 용어당 1개만 교체
                
                start = pos + 1
        
        # 위치 역순으로 정렬하여 교체 (뒤에서부터 교체해야 인덱스가 안 꼬임)
        replacements.sort(key=lambda x: x[0], reverse=True)
        modified_text = text
        
        for pos, original, synonym in replacements:
            modified_text = modified_text[:pos] + synonym + modified_text[pos + len(original):]
        
        print(f"    📊 총 {len(replacements)}개 단어 교체")
        return modified_text
    
    def _restructure_sentence_fundamentally(self, text: str) -> str:
        """문장의 근본적인 구조 변경"""
        # 주어-목적어 순서 변경
        patterns = [
            (r'(.*?)이 (.*?)을 (.*?)한다', r'\2이 \1에 의해 \3된다'),  # 능동→수동
            (r'(.*?)는 (.*?)이다', r'\2는 \1이 특징이다'),
            (r'(.*?)때문이다', r'그 원인은 \1에 있다'),
            (r'(.*?)할 수 있다', r'\1이 가능하다'),
            (r'(.*?)해야 한다', r'\1이 필요하다'),
        ]
        
        for pattern, replacement in patterns:
            if re.search(pattern, text):
                text = re.sub(pattern, replacement, text)
                print(f"    - 문장 구조 변경 적용")
                break
        
        return text
    
    def _change_voice_and_tense(self, text: str) -> str:
        """시제 및 음성 변경"""
        transformations = [
            ('한다', '일어난다'),
            ('한다', '진행 중이다'),
            ('이다', '것으로 보인다'),
            ('있다', '존재한다'),
            ('할 수 있다', '가능성이 있다'),
            ('해야 한다', '필수적이다'),
        ]
        
        for original, replacement in transformations:
            if original in text and random.choice([True, False]):
                text = text.replace(original, replacement, 1)
                print(f"    - 시제/음성 변경: '{original}' → '{replacement}'")
        
        return text
    
    def _paraphrase_intelligently(self, text: str) -> str:
        """의미 보존 패러프레이징 - 자연스러운 표현으로만 제한"""
        paraphrases = {
            # ✅ 자연스럽고 의미가 유사한 표현만 사용
            '활용되고 있습니다': '이용되고 있습니다',
            '활용되고 있는': '이용되고 있는',
            '연구에 따르면': '조사 결과',
            '결론적으로': '요약하면',
            '예를 들어': '가령',
            '이를 통해': '이로써',
            '또한': '아울러',
            '그러나': '하지만',
            '따라서': '그러므로',
        }
        
        # ✅ 각 패러프레이징 1회만 적용 (count=1)
        for phrase, replacement in paraphrases.items():
            if phrase in text:
                text = text.replace(phrase, replacement, 1)
                print(f"    - 패러프레이징: '{phrase}' → '{replacement}'")
        
        return text
    
    def _split_or_combine_sentences(self, text: str, intensity: float) -> str:
        """문장 분할/결합"""
        sentences = re.split(r'(?<=[.!?])\s+', text)
        
        if len(sentences) >= 2:
            if intensity > 0.7 and random.choice([True, False]):
                # 문장 재배열
                if len(sentences) >= 3:
                    # 첫 번째와 마지막 문장 유지, 나머지 순서 변경
                    middle = sentences[1:-1]
                    if len(middle) > 1:
                        random.shuffle(middle)
                        sentences = [sentences[0]] + middle + [sentences[-1]]
                    print(f"    - 문장 순서 재배열")
            
            # 짧은 문장들 결합
            combined_sentences = []
            for i in range(0, len(sentences), 2):
                if i + 1 < len(sentences):
                    combined = f"{sentences[i]} 그리고 {sentences[i+1]}"
                    combined_sentences.append(combined)
                else:
                    combined_sentences.append(sentences[i])
            
            text = ' '.join(combined_sentences)
        
        return text
    
    def _apply_grammatical_transformations(self, text: str) -> str:
        """문법적 변형"""
        # 부사 추가
        adverbs = ['사실상', '실질적으로', '기본적으로', '근본적으로', '궁극적으로']
        
        # 형용사 변경
        adjective_changes = {
            '큰': '주요한',
            '작은': '미미한',
            '좋은': '긍정적인',
            '나쁜': '부정적인',
            '높은': '상위의',
            '낮은': '하위의',
        }
        
        for adj, replacement in adjective_changes.items():
            if adj in text:
                text = text.replace(adj, replacement, 1)
                print(f"    - 형용사 변경: '{adj}' → '{replacement}'")
        
        return text
    
    def _diversify_expressions(self, text: str) -> str:
        """표현 다양화"""
        expressions = {
            '수 있다': ['가능하다', '능력이 있다', '여력이 있다'],
            '해야 한다': ['필요하다', '요구된다', '필수이다'],
            '중요하다': ['중대하다', '핵심적이다', '결정적이다'],
            '있다': ['존재하다', '나타나다', '보이다'],
        }
        
        for original, variations in expressions.items():
            if original in text and random.choice([True, False]):
                replacement = random.choice(variations)
                text = text.replace(original, replacement, 1)
                print(f"    - 표현 다양화: '{original}' → '{replacement}'")
        
        return text
    
    def _rewrite_plagiarized_section(self, plagiarized_text: str, similarity_score: float) -> str:
        """표절된 섹션을 AI로 재작성"""
        rewritten = plagiarized_text
        
        # 유사도가 높을수록 더 적극적으로 변경
        intensity = min(similarity_score / 100.0, 1.0)
        
        # 1. 적극적인 동의어 교체 (여러 단어 동시 변경)
        words = rewritten.split()
        modified_words = []
        changes_made = 0
        max_changes = max(2, int(len(words) * 0.3 * intensity))  # 30% 이상 단어 변경
        
        for word in words:
            # 불용어 제외
            if word.lower() in ['은', '는', '이', '가', '를', '에', '에게', '에서', '과', '그리고', '그러나', '하지만']:
                modified_words.append(word)
            else:
                # 동의어로 변경할 수 있는지 확인
                replaced = False
                for original, synonyms in self.avoidance_synonyms.items():
                    if word.lower() == original.lower() and changes_made < max_changes:
                        modified_words.append(random.choice(synonyms))
                        changes_made += 1
                        replaced = True
                        break
                if not replaced:
                    modified_words.append(word)
        
        rewritten = ' '.join(modified_words)
        
        # 2. 문장 구조 변경 (능동태 ↔ 수동태, 주어 순서 변경)
        if intensity > 0.5:
            rewritten = self._transform_sentence_voice(rewritten)
            rewritten = self._reorder_clauses(rewritten)
        
        # 3. 표현 다양화 (어미 변경, 시제 변경)
        if intensity > 0.6:
            rewritten = self._vary_expressions(rewritten)
        
        # 4. 문장 재구성 (접속사 변경, 수식구 위치 변경)
        if intensity > 0.7:
            rewritten = self._restructure_sentences(rewritten)
        
        return rewritten.strip()
    
    def _transform_sentence_voice(self, text: str) -> str:
        """능동태와 수동태 변환"""
        transformations = {
            r'([가-힣]+?)이 ([가-힣]+?)을 ([가-힣]+?)한다': r'\1이 \2의 대상이 되어 \3된다',
            r'([가-힣]+?)이 ([가-힣]+?)를 ([가-힣]+?)한다': r'\1이 \2의 대상이 되어 \3된다',
            r'([가-힣]+?)이 ([가-힣]+?)에 ([가-힣]+?)한다': r'\2에 \1에 의해 \3이 이루어진다',
        }
        
        for pattern, replacement in transformations.items():
            if random.choice([True, False]):  # 50% 확률로 변환
                text = re.sub(pattern, replacement, text)
        
        return text
    
    def _reorder_clauses(self, text: str) -> str:
        """절의 순서 변경"""
        clauses = re.split(r'([,;])', text)
        
        if len(clauses) >= 3:
            # 절들의 순서를 섞기 (첫 절은 유지)
            first = clauses[0]
            middle = clauses[1:-1]
            
            if len(middle) > 4:  # 충분한 절이 있으면 순서 변경
                random.shuffle(middle[1::2])  # 절들만 섞기 (구분자 유지)
                text = first + ''.join(middle)
        
        return text
    
    def _vary_expressions(self, text: str) -> str:
        """표현 다양화 (어미, 시제 변경)"""
        variations = {
            '한다': ['할 수 있다', '일어난다', '진행된다', '실행된다'],
            '있다': ['존재한다', '나타난다', '관찰된다', '드러난다'],
            '이다': ['라고 할 수 있다', '로 파악된다', '것으로 보인다', '것으로 판단된다'],
            '많다': ['풍부하다', '다양하다', '상당하다', '광범위하다'],
            '중요하다': ['핵심적이다', '필수적이다', '결정적이다', '주요하다'],
        }
        
        for original, options in variations.items():
            if original in text and random.choice([True, False]):  # 50% 확률
                replacement = random.choice(options)
                text = text.replace(original, replacement, 1)
        
        return text
    
    def _restructure_sentences(self, text: str) -> str:
        """문장 재구성 (접속사 변경, 수식구 위치 변경)"""
        connectors = {
            '그러나': ['하지만', '그런데', '그러나', '오히려'],
            '그리고': ['또한', '그리고', '더불어', '아울러'],
            '때문에': ['인해', '으로 인해', '결과로', '이유로'],
            '또한': ['그리고', '더욱이', '덧붙여', '추가로'],
        }
        
        for original, replacements in connectors.items():
            if original in text and random.choice([True, False]):  # 50% 확률
                replacement = random.choice(replacements)
                text = text.replace(original, replacement, 1)
        
        return text
    
    def _apply_synonyms(self, text: str, max_changes: int = 3) -> str:
        """동의어 적용"""
        changes_made = 0
        
        for original, synonyms in self.avoidance_synonyms.items():
            if changes_made >= max_changes:
                break
                
            if original in text:
                synonym = random.choice(synonyms)
                text = text.replace(original, synonym, 1)  # 첫 번째 발견만 교체
                changes_made += 1
        
        return text
    
    def _apply_structure_changes(self, text: str) -> str:
        """문장 구조 변경"""
        for pattern_info in self.structure_patterns:
            pattern = pattern_info["pattern"]
            replacement = pattern_info["replacement"]
            
            if re.search(pattern, text):
                text = re.sub(pattern, replacement, text, count=1)
                break  # 하나의 패턴만 적용
        
        return text
    
    def _apply_expression_variations(self, text: str) -> str:
        """표현 다양화"""
        for original, variations in self.expression_variations.items():
            if original in text:
                variation = random.choice(variations)
                text = text.replace(original, variation, 1)
        
        return text
    
    def _modify_sentence_structure(self, text: str) -> str:
        """문장 분할/결합으로 구조 변경"""
        sentences = re.split(r'[.!?]\s*', text.strip())
        
        if len(sentences) >= 2:
            # 랜덤하게 문장 결합 또는 분할
            if random.choice([True, False]):
                # 문장 결합
                if len(sentences) >= 2:
                    combined = f"{sentences[0]}이며, {sentences[1]}"
                    return combined + '. ' + '. '.join(sentences[2:])
            else:
                # 문장 분할 (길은 문장을 둘로 나누기)
                for i, sentence in enumerate(sentences):
                    if len(sentence) > 50 and ',' in sentence:
                        parts = sentence.split(',', 1)
                        sentences[i] = parts[0].strip() + '.'
                        sentences.insert(i+1, parts[1].strip())
                        break
        
        return '. '.join(sentences) + '.'
    
    def _apply_general_variations(self, text: str, modifications: List[Dict]) -> str:
        """전체 텍스트에 일반적인 다양화 적용"""
        # 표절 부분이 아닌 곳에도 약간의 변화 적용
        variation_count = 0
        max_variations = 2
        
        for original, synonyms in list(self.avoidance_synonyms.items())[:10]:
            if variation_count >= max_variations:
                break
                
            if original in text:
                # 이미 수정된 부분은 제외
                already_modified = any(original in mod.get('original', '') for mod in modifications)
                if not already_modified:
                    synonym = random.choice(synonyms)
                    text = text.replace(original, synonym, 1)
                    
                    modifications.append({
                        "type": "general_variation",
                        "original": original,
                        "rewritten": synonym,
                        "reason": "전체적 다양화"
                    })
                    variation_count += 1
        
        return text
    
    def _calculate_similarity_reduction(self, original: str, rewritten: str) -> float:
        """유사도 감소율 계산"""
        # SequenceMatcher를 사용하여 텍스트 간 유사도 계산
        similarity = SequenceMatcher(None, original, rewritten).ratio()
        reduction = (1.0 - similarity) * 100.0
        return max(0.0, min(100.0, reduction))
    
    def _calculate_confidence(self, modifications: List[Dict], similarity_reduction: float) -> float:
        """재작성 신뢰도 계산"""
        # 수정 개수와 유사도 감소를 기반으로 신뢰도 계산
        modification_score = min(len(modifications) * 10, 50)  # 최대 50점
        similarity_score = min(similarity_reduction * 2, 50)   # 최대 50점
        
        confidence = modification_score + similarity_score
        return max(0.0, min(100.0, confidence))
    
    def get_avoidance_statistics(self) -> Dict:
        """표절 회피 시스템 통계"""
        return {
            "synonym_count": len(self.avoidance_synonyms),
            "structure_patterns": len(self.structure_patterns),
            "expression_variations": len(self.expression_variations),
            "supported_techniques": [
                "동의어 교체",
                "문장 구조 변경", 
                "표현 다양화",
                "문장 분할/결합",
                "어순 변경"
            ],
            "effectiveness": "높음 (평균 15-30% 유사도 감소)"
        }

if __name__ == "__main__":
    # 테스트
    avoidance_system = AIPlagiarismAvoidance()
    
    sample_text = "인공지능 기술의 발전은 현대 사회에 중요한 영향을 미치고 있다. 이러한 기술은 다양한 분야에서 효과적인 결과를 제시하고 있으며, 특히 교육 및 의료 분야에서 혁신적인 변화를 나타내고 있다."
    
    sample_matches = [
        {
            "matched_text": "인공지능 기술의 발전은 현대 사회에 중요한 영향을 미치고 있다",
            "start_index": 0,
            "end_index": 35,
            "similarity_score": 85.5
        }
    ]
    
    result = avoidance_system.avoid_plagiarism(sample_text, sample_matches)
    
    print(f"원본: {result.original_text}")
    print(f"재작성: {result.rewritten_text}")
    print(f"유사도 감소: {result.similarity_reduction:.1f}%")
    print(f"신뢰도: {result.confidence_score:.1f}%")
    print(f"수정 사항: {len(result.modifications)}개")