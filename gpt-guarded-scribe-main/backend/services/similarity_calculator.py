import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from typing import List, Dict, Tuple
import hashlib
import math
from collections import Counter

class SimilarityCalculator:
    def __init__(self):
        self.tfidf_vectorizer = TfidfVectorizer(
            max_features=10000,
            ngram_range=(1, 3),
            stop_words=None,  # 우리가 직접 처리
            lowercase=True
        )
        
    def vectorize_text(self, text: str) -> np.ndarray:
        """텍스트를 벡터로 변환"""
        try:
            # TF-IDF 벡터화
            tfidf_matrix = self.tfidf_vectorizer.fit_transform([text])
            return tfidf_matrix.toarray()[0]
        except:
            # 빈 텍스트 처리
            return np.zeros(1000)
    
    def calculate_similarity(self, text1: str, text2: str) -> float:
        """두 텍스트 간의 유사도 계산"""
        try:
            # TF-IDF 벡터화
            tfidf_matrix = self.tfidf_vectorizer.fit_transform([text1, text2])
            
            # 코사인 유사도 계산
            similarity_matrix = cosine_similarity(tfidf_matrix)
            
            return float(similarity_matrix[0][1])
        except:
            return 0.0
    
    def jaccard_similarity(self, set1: set, set2: set) -> float:
        """자카드 유사도 계산"""
        if not set1 and not set2:
            return 1.0
        
        intersection = len(set1.intersection(set2))
        union = len(set1.union(set2))
        
        return intersection / union if union > 0 else 0.0
    
    def calculate_ngram_similarity(self, text1: str, text2: str, n: int = 5) -> float:
        """N-gram 기반 유사도 계산"""
        # N-gram 생성
        ngrams1 = self._generate_ngrams(text1, n)
        ngrams2 = self._generate_ngrams(text2, n)
        
        # 자카드 유사도 계산
        return self.jaccard_similarity(set(ngrams1), set(ngrams2))
    
    def _generate_ngrams(self, text: str, n: int) -> List[str]:
        """N-gram 생성"""
        words = text.split()
        ngrams = []
        
        for i in range(len(words) - n + 1):
            ngram = ' '.join(words[i:i + n])
            ngrams.append(ngram)
        
        return ngrams
    
    def min_hash_similarity(self, text1: str, text2: str, num_hashes: int = 100) -> float:
        """MinHash를 이용한 유사도 계산"""
        # Shingle 생성
        shingles1 = set(self._generate_shingles(text1))
        shingles2 = set(self._generate_shingles(text2))
        
        # MinHash 계산
        minhash1 = self._compute_minhash(shingles1, num_hashes)
        minhash2 = self._compute_minhash(shingles2, num_hashes)
        
        # 유사도 계산
        matches = sum(1 for h1, h2 in zip(minhash1, minhash2) if h1 == h2)
        return matches / num_hashes
    
    def _generate_shingles(self, text: str, k: int = 5) -> List[str]:
        """k-shingle 생성"""
        text = text.replace(' ', '')  # 공백 제거
        shingles = []
        
        for i in range(len(text) - k + 1):
            shingle = text[i:i + k]
            shingles.append(shingle)
        
        return shingles
    
    def _compute_minhash(self, shingles: set, num_hashes: int) -> List[int]:
        """MinHash 계산"""
        minhashes = []
        
        for i in range(num_hashes):
            min_hash = float('inf')
            
            for shingle in shingles:
                # 해시 함수 적용
                hash_value = hash(shingle + str(i)) % (2**32)
                min_hash = min(min_hash, hash_value)
            
            minhashes.append(min_hash)
        
        return minhashes
    
    def semantic_similarity(self, text1: str, text2: str) -> float:
        """의미적 유사도 계산 (간단한 구현)"""
        # 실제로는 BERT, Sentence-BERT 등을 사용
        # 여기서는 TF-IDF 코사인 유사도로 대체
        return self.calculate_similarity(text1, text2)
    
    def calculate_overlap_ratio(self, text1: str, text2: str) -> float:
        """텍스트 중복 비율 계산"""
        words1 = set(text1.split())
        words2 = set(text2.split())
        
        if not words1:
            return 0.0
        
        overlap = len(words1.intersection(words2))
        return overlap / len(words1)
    
    def find_longest_common_substring(self, text1: str, text2: str) -> Tuple[str, int, int]:
        """가장 긴 공통 부분 문자열 찾기"""
        m, n = len(text1), len(text2)
        
        # DP 테이블 생성
        dp = [[0] * (n + 1) for _ in range(m + 1)]
        
        max_length = 0
        ending_pos = 0
        
        for i in range(1, m + 1):
            for j in range(1, n + 1):
                if text1[i-1] == text2[j-1]:
                    dp[i][j] = dp[i-1][j-1] + 1
                    if dp[i][j] > max_length:
                        max_length = dp[i][j]
                        ending_pos = i
                else:
                    dp[i][j] = 0
        
        start_pos = ending_pos - max_length
        longest_substring = text1[start_pos:ending_pos]
        
        return longest_substring, start_pos, ending_pos
    
    def calculate_fuzzy_similarity(self, text1: str, text2: str) -> float:
        """퍼지 문자열 매칭"""
        # Levenshtein 거리 기반 유사도
        def levenshtein_distance(s1, s2):
            if len(s1) < len(s2):
                return levenshtein_distance(s2, s1)
            
            if len(s2) == 0:
                return len(s1)
            
            previous_row = range(len(s2) + 1)
            for i, c1 in enumerate(s1):
                current_row = [i + 1]
                for j, c2 in enumerate(s2):
                    insertions = previous_row[j + 1] + 1
                    deletions = current_row[j] + 1
                    substitutions = previous_row[j] + (c1 != c2)
                    current_row.append(min(insertions, deletions, substitutions))
                previous_row = current_row
            
            return previous_row[-1]
        
        distance = levenshtein_distance(text1, text2)
        max_length = max(len(text1), len(text2))
        
        return 1 - (distance / max_length) if max_length > 0 else 1.0
    
    def calculate_weighted_similarity(self, text1: str, text2: str) -> Dict[str, float]:
        """가중 유사도 계산"""
        similarities = {
            'tfidf_cosine': self.calculate_similarity(text1, text2),
            'ngram_jaccard': self.calculate_ngram_similarity(text1, text2, 5),
            'word_overlap': self.calculate_overlap_ratio(text1, text2),
            'fuzzy_match': self.calculate_fuzzy_similarity(text1, text2)
        }
        
        # 가중 평균 계산
        weights = {
            'tfidf_cosine': 0.4,
            'ngram_jaccard': 0.3,
            'word_overlap': 0.2,
            'fuzzy_match': 0.1
        }
        
        weighted_score = sum(
            similarities[method] * weights[method] 
            for method in similarities
        )
        
        similarities['weighted_average'] = weighted_score
        
        return similarities
    
    def detect_paraphrasing(self, text1: str, text2: str, threshold: float = 0.7) -> bool:
        """패러프레이징 탐지"""
        semantic_sim = self.semantic_similarity(text1, text2)
        ngram_sim = self.calculate_ngram_similarity(text1, text2, 3)
        
        # 의미적으로 유사하지만 n-gram이 다른 경우 패러프레이징으로 판단
        return semantic_sim > threshold and ngram_sim < 0.5
    
    def calculate_sentence_level_similarity(self, text1: str, text2: str) -> List[Dict]:
        """문장 레벨 유사도 계산"""
        sentences1 = [s.strip() for s in text1.split('.') if s.strip()]
        sentences2 = [s.strip() for s in text2.split('.') if s.strip()]
        
        similarities = []
        
        for i, sent1 in enumerate(sentences1):
            for j, sent2 in enumerate(sentences2):
                sim_score = self.calculate_similarity(sent1, sent2)
                if sim_score > 0.5:  # 임계값 이상인 경우만
                    similarities.append({
                        'sentence1_index': i,
                        'sentence2_index': j,
                        'sentence1': sent1,
                        'sentence2': sent2,
                        'similarity': sim_score
                    })
        
        return sorted(similarities, key=lambda x: x['similarity'], reverse=True)