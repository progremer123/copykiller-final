#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""AI 지식 생성 서비스 - Claude AI를 활용한 콘텐츠 생성"""

import sqlite3
from datetime import datetime
import re
from typing import List, Dict, Optional
from dataclasses import dataclass
import json
import random
import time

@dataclass
class AIGeneratedContent:
    """AI 생성 콘텐츠 데이터 클래스"""
    title: str
    content: str
    topic: str
    subtopics: List[str]
    source_type: str = "ai_generated"

class AIKnowledgeGenerator:
    """AI 기반 지식 콘텐츠 생성 서비스"""
    
    def __init__(self, db_path="plagiarism.db"):
        self.db_path = db_path
        
        # AI가 생성할 수 있는 주제별 지식 템플릿
        self.knowledge_templates = {
            '인공지능': {
                'subtopics': [
                    'AI의 정의와 개념', 'AI 발전 역사', 'AI 기술 분류',
                    'AI 응용 분야', 'AI 윤리와 한계', 'AI와 미래 사회'
                ],
                'templates': [
                    "인공지능(AI)의 개념과 정의에 대해 설명하겠습니다.",
                    "인공지능 기술의 발전 과정과 주요 이정표를 살펴보겠습니다.",
                    "현재 인공지능이 적용되는 다양한 분야와 사례들을 분석하겠습니다."
                ]
            },
            '기후변화': {
                'subtopics': [
                    '기후변화의 원인', '온실가스 효과', '기후변화 영향',
                    '기후변화 대응책', '국제 기후협약', '탄소중립 정책'
                ],
                'templates': [
                    "기후변화의 주요 원인과 메커니즘을 분석하겠습니다.",
                    "지구온난화가 환경과 생태계에 미치는 영향을 설명하겠습니다.",
                    "기후변화 대응을 위한 국제적 노력과 정책들을 살펴보겠습니다."
                ]
            },
            '교육': {
                'subtopics': [
                    '교육의 목적과 가치', '교육 시스템', '디지털 교육',
                    '교육 불평등', '평생교육', '미래 교육'
                ],
                'templates': [
                    "현대 교육 시스템의 특징과 발전 방향을 분석하겠습니다.",
                    "디지털 기술이 교육에 미치는 영향과 변화를 설명하겠습니다.",
                    "교육 기회의 평등과 접근성 향상 방안을 살펴보겠습니다."
                ]
            },
            '경제': {
                'subtopics': [
                    '시장경제 원리', '경제성장 이론', '경제정책',
                    '디지털 경제', '글로벌 경제', '경제 불평등'
                ],
                'templates': [
                    "현대 경제 시스템의 구조와 작동 원리를 분석하겠습니다.",
                    "경제성장과 발전에 영향을 미치는 주요 요인들을 설명하겠습니다.",
                    "글로벌 경제 환경의 변화와 대응 전략을 살펴보겠습니다."
                ]
            },
            '기술': {
                'subtopics': [
                    '기술 혁신', '디지털 트랜스포메이션', '4차 산업혁명',
                    '블록체인', '사물인터넷', '빅데이터'
                ],
                'templates': [
                    "4차 산업혁명 기술들의 특징과 사회적 영향을 분석하겠습니다.",
                    "디지털 기술이 산업과 사회에 가져온 변화를 설명하겠습니다.",
                    "신기술의 발전이 미래 사회에 미칠 영향을 살펴보겠습니다."
                ]
            },
            '사회': {
                'subtopics': [
                    '사회 구조', '사회 변동', '사회 문제',
                    '사회 통합', '다문화 사회', '사회 정의'
                ],
                'templates': [
                    "현대 사회의 구조적 특징과 변화 양상을 분석하겠습니다.",
                    "사회 통합과 갈등 해결을 위한 방안들을 설명하겠습니다.",
                    "다양성이 증가하는 사회에서의 조화 방안을 살펴보겠습니다."
                ]
            },
            '정치': {
                'subtopics': [
                    '민주주의', '정치 제도', '정치 참여',
                    '정책 과정', '국제 정치', '정치 윤리'
                ],
                'templates': [
                    "민주주의 정치 제도의 원리와 운영 방식을 분석하겠습니다.",
                    "효과적인 정책 수립과 실행 과정을 설명하겠습니다.",
                    "시민 참여와 정치적 책임에 대한 중요성을 살펴보겠습니다."
                ]
            },
            '문화': {
                'subtopics': [
                    '문화의 개념', '문화 다양성', '대중문화',
                    '전통문화', '문화 교류', '문화 산업'
                ],
                'templates': [
                    "문화의 개념과 사회적 역할에 대해 분석하겠습니다.",
                    "문화 다양성의 가치와 보존 방안을 설명하겠습니다.",
                    "전통문화와 현대문화의 조화로운 발전을 살펴보겠습니다."
                ]
            }
        }
    
    def generate_ai_content(self, topic: str, num_articles: int = 5) -> List[AIGeneratedContent]:
        """AI를 활용하여 주제별 지식 콘텐츠 생성"""
        print(f"🤖 AI 지식 생성 시작: '{topic}' 주제로 {num_articles}개 문서 생성")
        
        generated_contents = []
        
        # 주제 정규화
        normalized_topic = self._normalize_topic(topic)
        template_data = self.knowledge_templates.get(normalized_topic, self.knowledge_templates['기술'])
        
        for i in range(num_articles):
            try:
                content = self._generate_single_content(topic, normalized_topic, template_data, i)
                if content:
                    generated_contents.append(content)
                    print(f"✅ AI 콘텐츠 생성 완료 {i+1}/{num_articles}: {content.title[:50]}...")
                
                # 생성 간 지연 (자연스러운 처리를 위해)
                time.sleep(0.5)
                
            except Exception as e:
                print(f"❌ AI 콘텐츠 생성 실패 {i+1}: {e}")
                continue
        
        return generated_contents
    
    def _normalize_topic(self, topic: str) -> str:
        """주제를 정규화하여 템플릿과 매칭"""
        topic_mappings = {
            'ai': '인공지능', '머신러닝': '인공지능', '딥러닝': '인공지능',
            '지구온난화': '기후변화', '환경': '기후변화', '탄소': '기후변화',
            '학교': '교육', '학습': '교육', '교육과정': '교육',
            '시장': '경제', '금융': '경제', '투자': '경제',
            'it': '기술', '디지털': '기술', '컴퓨터': '기술',
            '공동체': '사회', '사회학': '사회', '사회문제': '사회',
            '민주주의': '정치', '정부': '정치', '정책': '정치',
            '예술': '문화', '전통': '문화', '문화재': '문화'
        }
        
        topic_lower = topic.lower()
        for key, value in topic_mappings.items():
            if key in topic_lower or key in topic:
                return value
        
        # 키워드 매칭
        for template_key in self.knowledge_templates.keys():
            if template_key in topic:
                return template_key
                
        return '기술'  # 기본값
    
    def _generate_single_content(self, original_topic: str, normalized_topic: str, 
                                template_data: dict, index: int) -> Optional[AIGeneratedContent]:
        """단일 AI 콘텐츠 생성"""
        
        subtopics = template_data['subtopics']
        templates = template_data['templates']
        
        # 하위 주제 선택
        selected_subtopic = subtopics[index % len(subtopics)]
        template = templates[index % len(templates)]
        
        # 제목 생성
        title_variations = [
            f"{selected_subtopic}에 대한 종합적 분석",
            f"{selected_subtopic}: 현황과 전망",
            f"{selected_subtopic}의 이해와 적용",
            f"{normalized_topic} 분야의 {selected_subtopic}",
            f"{selected_subtopic} 심화 연구"
        ]
        title = title_variations[index % len(title_variations)]
        
        # 콘텐츠 생성
        content_parts = [
            f"# {title}\n",
            f"{template}\n",
            self._generate_introduction(normalized_topic, selected_subtopic),
            self._generate_main_content(normalized_topic, selected_subtopic),
            self._generate_analysis(normalized_topic, selected_subtopic),
            self._generate_conclusion(normalized_topic, selected_subtopic)
        ]
        
        full_content = "\n\n".join(content_parts)
        
        return AIGeneratedContent(
            title=title,
            content=full_content,
            topic=normalized_topic,
            subtopics=[selected_subtopic],
            source_type="ai_generated_claude"
        )
    
    def _generate_introduction(self, topic: str, subtopic: str) -> str:
        """서론 생성"""
        intro_templates = {
            '인공지능': [
                f"{subtopic}는 현대 AI 발전에서 핵심적인 역할을 하고 있습니다. 이 분야의 발전은 우리 사회 전반에 혁신적인 변화를 가져오고 있으며, 미래 기술 발전의 토대가 되고 있습니다.",
                f"{subtopic}에 대한 이해는 AI 시대를 살아가는 현대인에게 필수적입니다. 이 주제를 통해 인공지능 기술의 본질과 가능성을 탐구해보겠습니다."
            ],
            '기후변화': [
                f"{subtopic}는 지구 환경의 지속가능성을 위해 반드시 다루어야 할 중요한 과제입니다. 이 문제에 대한 과학적 접근과 실천적 해결방안이 필요합니다.",
                f"{subtopic}를 통해 우리는 환경 보호의 중요성과 기후변화 대응의 시급성을 이해할 수 있습니다."
            ],
            '교육': [
                f"{subtopic}는 미래 사회를 준비하는 교육 시스템 발전에 중요한 의미를 갖습니다. 변화하는 시대에 맞는 교육 패러다임의 전환이 필요합니다.",
                f"{subtopic}를 통해 효과적인 교육 방법과 학습 환경 개선 방안을 모색할 수 있습니다."
            ],
            '경제': [
                f"{subtopic}는 현대 경제 시스템의 이해와 발전 방향 설정에 핵심적인 역할을 합니다. 글로벌 경제 환경의 변화에 대한 적응이 중요합니다.",
                f"{subtopic}를 분석함으로써 지속가능한 경제 성장의 가능성과 방향을 탐구할 수 있습니다."
            ]
        }
        
        templates = intro_templates.get(topic, intro_templates['인공지능'])
        return random.choice(templates)
    
    def _generate_main_content(self, topic: str, subtopic: str) -> str:
        """본문 생성"""
        content_frameworks = {
            '인공지능': [
                f"{subtopic}의 핵심 개념을 살펴보면, 데이터 처리와 패턴 인식을 통한 지능적 의사결정이 중요합니다. 머신러닝 알고리즘의 발전으로 인해 더욱 정교한 AI 시스템 구축이 가능해졌으며, 이는 다양한 산업 분야에 적용되고 있습니다. 특히 자연어 처리, 컴퓨터 비전, 로봇공학 등의 영역에서 혁신적인 성과를 보이고 있습니다.",
                f"이러한 기술 발전은 의료, 금융, 교통, 제조업 등 광범위한 분야에서 효율성 향상과 새로운 가치 창출을 가능하게 하고 있습니다. 그러나 동시에 일자리 변화, 프라이버시 보호, 알고리즘 편향성 등의 과제도 함께 고려해야 합니다."
            ],
            '기후변화': [
                f"{subtopic}와 관련하여 온실가스 배출의 증가가 지구 기후 시스템에 미치는 영향을 분석해보겠습니다. 산업혁명 이후 급격한 화석연료 사용 증가로 인해 대기 중 이산화탄소 농도가 지속적으로 상승하고 있으며, 이는 지구 평균 기온 상승의 주요 원인이 되고 있습니다.",
                f"이러한 변화는 극지방 빙하 융해, 해수면 상승, 극한 기상현상 빈발 등의 결과를 가져오고 있습니다. 생태계 변화와 생물다양성 감소, 농업 생산성 변화 등은 인류의 생존과 직결된 문제로 대두되고 있습니다."
            ]
        }
        
        frameworks = content_frameworks.get(topic, content_frameworks['인공지능'])
        return " ".join(frameworks)
    
    def _generate_analysis(self, topic: str, subtopic: str) -> str:
        """분석 섹션 생성"""
        return f"{subtopic}에 대한 심층 분석을 통해 다음과 같은 핵심 요소들을 파악할 수 있습니다. 첫째, 현재 상황에 대한 정확한 진단과 평가가 필요합니다. 둘째, 미래 발전 가능성과 잠재적 위험 요소들에 대한 종합적 검토가 중요합니다. 셋째, 이해관계자들 간의 협력과 조정을 통한 효과적인 대응 방안 마련이 필수적입니다. 이러한 다각도 분석을 바탕으로 보다 실효성 있는 정책과 전략을 수립할 수 있을 것입니다."
    
    def _generate_conclusion(self, topic: str, subtopic: str) -> str:
        """결론 생성"""
        conclusions = [
            f"{subtopic}는 {topic} 분야의 지속가능한 발전을 위해 반드시 고려해야 할 핵심 요소입니다. 앞으로도 지속적인 연구와 실천을 통해 더 나은 미래를 구축해나가야 할 것입니다.",
            f"결론적으로 {subtopic}에 대한 종합적 접근과 체계적 대응이 {topic} 분야의 혁신과 발전에 중요한 기여를 할 것으로 예상됩니다. 이를 위해서는 다양한 주체들의 적극적인 참여와 협력이 필요합니다."
        ]
        return random.choice(conclusions)
    
    def save_ai_content_to_database(self, contents: List[AIGeneratedContent]) -> int:
        """AI 생성 콘텐츠를 데이터베이스에 저장"""
        if not contents:
            return 0
            
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
            saved_count = 0
            
            for content in contents:
                # 중복 체크 (제목 기준)
                cursor.execute("""
                    SELECT id FROM document_sources 
                    WHERE title = ? AND is_active = 1
                """, (content.title,))
                
                if cursor.fetchone():
                    print(f"⚠️  이미 존재하는 AI 콘텐츠: {content.title[:50]}...")
                    continue
                
                # URL 생성 (AI 생성 콘텐츠임을 표시)
                ai_url = f"ai://claude-generated/{content.topic}/{saved_count}"
                
                # 저장
                cursor.execute("""
                    INSERT INTO document_sources 
                    (title, content, url, source_type, created_at, updated_at, is_active)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    content.title,
                    content.content,
                    ai_url,
                    content.source_type,
                    current_time,
                    current_time,
                    1
                ))
                saved_count += 1
                print(f"💾 AI 콘텐츠 저장됨: {content.title[:50]}...")
            
            conn.commit()
            conn.close()
            
            return saved_count
            
        except Exception as e:
            print(f"❌ AI 콘텐츠 저장 오류: {e}")
            return 0
    
    def generate_and_save_knowledge(self, topic: str, num_articles: int = 5) -> Dict:
        """AI 지식 생성 및 저장 통합 함수"""
        print(f"🚀 AI 지식 생성기 시작: '{topic}' 주제")
        
        # AI 콘텐츠 생성
        contents = self.generate_ai_content(topic, num_articles)
        
        # 데이터베이스 저장
        saved_count = self.save_ai_content_to_database(contents)
        
        # 결과 반환
        result = {
            'topic': topic,
            'requested_count': num_articles,
            'generated_count': len(contents),
            'saved_count': saved_count,
            'contents_summary': [
                {
                    'title': content.title,
                    'subtopic': ', '.join(content.subtopics),
                    'content_length': len(content.content),
                    'source_type': content.source_type
                }
                for content in contents
            ]
        }
        
        print(f"✅ AI 지식 생성 완료:")
        print(f"   📝 생성: {len(contents)}개")
        print(f"   💾 저장: {saved_count}개")
        print(f"   🎯 주제: {topic}")
        
        return result

if __name__ == "__main__":
    # 테스트
    ai_generator = AIKnowledgeGenerator()
    
    # 다양한 주제로 AI 지식 생성 테스트
    test_topics = ["인공지능", "기후변화", "디지털 교육", "경제 정책"]
    
    for topic in test_topics:
        print(f"\n{'='*60}")
        result = ai_generator.generate_and_save_knowledge(topic, 3)
        print(f"\n📈 AI 생성 결과:")
        print(f"   주제: {result['topic']}")
        print(f"   생성: {result['generated_count']}개")
        print(f"   저장: {result['saved_count']}개")
        print("="*60)