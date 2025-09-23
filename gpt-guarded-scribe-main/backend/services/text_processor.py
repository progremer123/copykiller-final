import re
import string
from typing import List, Dict
import PyPDF2
from docx import Document
import io

class TextProcessor:
    def __init__(self):
        # 불용어 리스트 (한국어 + 영어)
        self.stop_words = {
            '그', '이', '저', '것', '들', '에', '를', '이', '가', '은', '는', '의', '와', '과', '도', '만',
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'
        }
    
    def extract_text_from_file(self, file_content: bytes, content_type: str) -> str:
        """파일에서 텍스트 추출"""
        try:
            if content_type == "text/plain":
                return file_content.decode('utf-8')
            
            elif content_type == "application/pdf":
                return self._extract_from_pdf(file_content)
            
            elif content_type in ["application/msword", 
                                "application/vnd.openxmlformats-officedocument.wordprocessingml.document"]:
                return self._extract_from_docx(file_content)
            
            else:
                raise ValueError(f"Unsupported file type: {content_type}")
                
        except Exception as e:
            raise ValueError(f"텍스트 추출 실패: {str(e)}")
    
    def _extract_from_pdf(self, file_content: bytes) -> str:
        """PDF에서 텍스트 추출"""
        pdf_file = io.BytesIO(file_content)
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        
        return text
    
    def _extract_from_docx(self, file_content: bytes) -> str:
        """DOCX에서 텍스트 추출"""
        doc_file = io.BytesIO(file_content)
        doc = Document(doc_file)
        
        text = ""
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
        
        return text
    
    def preprocess_text(self, text: str) -> str:
        """텍스트 전처리"""
        # 소문자 변환
        text = text.lower()
        
        # 특수문자 제거 (한글, 영문, 숫자, 공백만 유지)
        text = re.sub(r'[^\w\s가-힣]', ' ', text)
        
        # 여러 공백을 하나로 변환
        text = re.sub(r'\s+', ' ', text)
        
        # 앞뒤 공백 제거
        text = text.strip()
        
        return text
    
    def remove_stop_words(self, text: str) -> str:
        """불용어 제거"""
        words = text.split()
        filtered_words = [word for word in words if word not in self.stop_words]
        return ' '.join(filtered_words)
    
    def generate_ngrams(self, text: str, n: int = 5) -> List[str]:
        """N-gram 생성"""
        words = text.split()
        ngrams = []
        
        for i in range(len(words) - n + 1):
            ngram = ' '.join(words[i:i + n])
            ngrams.append(ngram)
        
        return ngrams
    
    def generate_shingles(self, text: str, k: int = 5) -> List[str]:
        """Shingling (k-shingle) 생성"""
        # 문자 단위 k-shingle
        shingles = []
        text = re.sub(r'\s+', '', text)  # 공백 제거
        
        for i in range(len(text) - k + 1):
            shingle = text[i:i + k]
            shingles.append(shingle)
        
        return list(set(shingles))  # 중복 제거
    
    def extract_sentences(self, text: str) -> List[str]:
        """문장 분리"""
        # 한국어와 영어 문장 구분
        sentences = re.split(r'[.!?。！？]', text)
        
        # 빈 문장 제거 및 정리
        sentences = [s.strip() for s in sentences if s.strip()]
        
        return sentences
    
    def calculate_word_frequency(self, text: str) -> Dict[str, int]:
        """단어 빈도 계산"""
        words = text.split()
        frequency = {}
        
        for word in words:
            if word not in self.stop_words:
                frequency[word] = frequency.get(word, 0) + 1
        
        return frequency
    
    def extract_key_phrases(self, text: str, top_k: int = 10) -> List[str]:
        """핵심 구문 추출"""
        # 간단한 구현: 빈도 기반
        word_freq = self.calculate_word_frequency(text)
        
        # 빈도순으로 정렬
        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        
        # 상위 k개 단어로 구성된 구문들 추출
        key_phrases = []
        sentences = self.extract_sentences(text)
        
        for word, freq in sorted_words[:top_k]:
            for sentence in sentences:
                if word in sentence.lower():
                    # 해당 단어를 포함한 구문 추출 (앞뒤 3단어)
                    words_in_sentence = sentence.split()
                    for i, w in enumerate(words_in_sentence):
                        if word in w.lower():
                            start = max(0, i - 3)
                            end = min(len(words_in_sentence), i + 4)
                            phrase = ' '.join(words_in_sentence[start:end])
                            key_phrases.append(phrase)
                            break
                    break
        
        return key_phrases[:top_k]
    
    def clean_text_for_comparison(self, text: str) -> str:
        """비교를 위한 텍스트 정리"""
        # 전처리
        cleaned = self.preprocess_text(text)
        
        # 불용어 제거
        cleaned = self.remove_stop_words(cleaned)
        
        return cleaned
    
    def segment_text(self, text: str, max_length: int = 1000) -> List[str]:
        """텍스트를 적절한 크기로 분할"""
        sentences = self.extract_sentences(text)
        segments = []
        current_segment = ""
        
        for sentence in sentences:
            if len(current_segment + sentence) > max_length:
                if current_segment:
                    segments.append(current_segment.strip())
                    current_segment = sentence
                else:
                    # 문장이 너무 긴 경우 강제 분할
                    segments.append(sentence[:max_length])
                    current_segment = sentence[max_length:]
            else:
                current_segment += " " + sentence
        
        if current_segment:
            segments.append(current_segment.strip())
        
        return segments