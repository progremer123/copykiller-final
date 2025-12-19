#!/usr/bin/env python3
"""다양한 주제의 문서 추가"""

import sqlite3
from datetime import datetime

def add_diverse_documents():
    try:
        conn = sqlite3.connect("plagiarism.db")
        cursor = conn.cursor()
        
        diverse_docs = [
            {
                "title": "한국의 전통 문화",
                "content": """한국의 전통 문화는 오랜 역사와 함께 발전해왔습니다. 
                한복, 한식, 한옥 등은 우리나라만의 독특한 문화적 특징을 보여줍니다.
                전통 음악인 국악과 민속놀이들은 조상들의 지혜가 담겨 있습니다.
                이러한 전통 문화는 현대에도 계승되어 우리의 정체성을 형성합니다.""",
                "url": "https://example.com/korean-culture",
                "source_type": "encyclopedia"
            },
            {
                "title": "교육의 중요성과 미래",
                "content": """교육은 개인과 사회 발전의 핵심 요소입니다.
                미래 사회에서는 창의적 사고와 문제 해결 능력이 중요합니다.
                디지털 시대에 맞는 새로운 교육 방법과 기술이 필요합니다.
                평생 학습의 개념이 더욱 중요해지고 있습니다.""",
                "url": "https://example.com/education-future",
                "source_type": "academic"
            },
            {
                "title": "건강한 생활 습관",
                "content": """건강한 생활 습관은 삶의 질을 향상시킵니다.
                규칙적인 운동과 균형 잡힌 식단이 기본입니다.
                충분한 수면과 스트레스 관리도 매우 중요합니다.
                금연, 금주와 같은 건전한 습관을 유지해야 합니다.""",
                "url": "https://example.com/healthy-lifestyle",
                "source_type": "health"
            },
            {
                "title": "경제와 사회 발전",
                "content": """경제 발전은 사회 전반에 큰 영향을 미칩니다.
                지속가능한 발전을 위해서는 환경과 경제의 조화가 필요합니다.
                기술 혁신과 인적 자원 개발이 경쟁력의 핵심입니다.
                글로벌 시대에 맞는 새로운 경제 모델이 요구됩니다.""",
                "url": "https://example.com/economy-development",
                "source_type": "economic"
            },
            {
                "title": "예술과 창작 활동",
                "content": """예술은 인간의 감정과 생각을 표현하는 중요한 수단입니다.
                창작 활동을 통해 새로운 아이디어와 영감을 얻을 수 있습니다.
                다양한 예술 장르가 서로 영향을 주고받으며 발전합니다.
                예술 교육은 창의성과 상상력을 키우는데 도움이 됩니다.""",
                "url": "https://example.com/art-creativity",
                "source_type": "culture"
            },
            {
                "title": "과학 기술의 발전",
                "content": """과학 기술의 발전은 인류 문명을 크게 변화시켰습니다.
                의학 기술의 발달로 인간의 수명이 늘어나고 있습니다.
                우주 탐사와 해양 탐구를 통해 새로운 지식을 얻고 있습니다.
                바이오 기술과 나노 기술이 미래를 이끌어갈 것입니다.""",
                "url": "https://example.com/science-technology",
                "source_type": "science"
            },
            {
                "title": "여행과 문화 체험",
                "content": """여행은 새로운 문화와 경험을 제공합니다.
                다른 나라의 역사와 전통을 직접 체험할 수 있습니다.
                여행을 통해 시야를 넓히고 세계관을 확장할 수 있습니다.
                현지 음식과 언어를 배우는 것도 여행의 즐거움입니다.""",
                "url": "https://example.com/travel-culture",
                "source_type": "travel"
            },
            {
                "title": "스포츠와 건강관리",
                "content": """스포츠는 신체 건강과 정신 건강에 도움이 됩니다.
                팀 스포츠를 통해 협동심과 리더십을 배울 수 있습니다.
                규칙적인 운동은 스트레스 해소에 효과적입니다.
                올림픽과 같은 국제 대회는 전 세계인이 함께 즐기는 축제입니다.""",
                "url": "https://example.com/sports-health",
                "source_type": "sports"
            }
        ]
        
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
        
        for doc in diverse_docs:
            cursor.execute("""
                INSERT INTO document_sources 
                (title, content, url, source_type, created_at, updated_at, is_active)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                doc["title"],
                doc["content"],
                doc["url"],
                doc["source_type"],
                current_time,
                current_time,
                1
            ))
            
        conn.commit()
        print(f"✅ {len(diverse_docs)}개 다양한 주제 문서가 추가되었습니다.")
        
        # 전체 문서 수 확인
        cursor.execute("SELECT COUNT(*) FROM document_sources WHERE is_active = 1")
        total_docs = cursor.fetchone()[0]
        print(f"📚 총 활성 문서 수: {total_docs}개")
        
        # 주제별 문서 수 확인
        cursor.execute("SELECT source_type, COUNT(*) FROM document_sources WHERE is_active = 1 GROUP BY source_type")
        categories = cursor.fetchall()
        print("\n📊 주제별 문서 수:")
        for category, count in categories:
            print(f"   - {category}: {count}개")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ 오류 발생: {e}")

if __name__ == "__main__":
    add_diverse_documents()