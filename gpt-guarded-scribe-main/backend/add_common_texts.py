#!/usr/bin/env python3
"""대용량 일반 문서 데이터 추가"""

import sqlite3
from datetime import datetime

def add_common_texts():
    try:
        conn = sqlite3.connect("plagiarism.db")
        cursor = conn.cursor()
        
        # 일반적으로 자주 사용되는 표현들과 문장들
        common_docs = [
            {
                "title": "일반적인 인사말과 표현",
                "content": """안녕하세요. 반갑습니다. 오늘 날씨가 좋네요.
                어떻게 지내세요? 잘 부탁드립니다. 감사합니다.
                죄송합니다. 실례합니다. 수고하셨습니다.
                좋은 하루 되세요. 안녕히 가세요. 또 뵙겠습니다.""",
                "url": "https://example.com/common-greetings",
                "source_type": "common"
            },
            {
                "title": "기본적인 설명 문장들",
                "content": """이것은 매우 중요한 내용입니다. 
                다음과 같은 방법을 사용할 수 있습니다.
                여러 가지 선택사항이 있습니다.
                이에 대한 자세한 내용은 다음과 같습니다.
                결론적으로 말하면 이것이 가장 좋은 방법입니다.""",
                "url": "https://example.com/basic-explanations",
                "source_type": "common"
            },
            {
                "title": "시간과 날짜 표현",
                "content": """오늘은 좋은 날입니다. 내일도 기대가 됩니다.
                어제 일어난 일이 기억납니다. 지난주에 만났었죠.
                다음 주에 다시 만나요. 이번 달은 바쁜 한 달이었습니다.
                새해가 다가오고 있습니다. 시간이 빨리 갑니다.""",
                "url": "https://example.com/time-expressions",
                "source_type": "common"
            },
            {
                "title": "감정과 생각 표현",
                "content": """정말 기쁩니다. 조금 걱정이 됩니다.
                매우 흥미로운 이야기입니다. 놀라운 일이 일어났습니다.
                생각해보니 그것도 좋은 아이디어네요.
                개인적으로는 다른 의견입니다. 동감합니다.""",
                "url": "https://example.com/emotions-thoughts",
                "source_type": "common"
            },
            {
                "title": "일상 생활 표현",
                "content": """집에서 쉬고 있습니다. 학교에 가야 합니다.
                회사에서 일하고 있습니다. 친구들과 만날 예정입니다.
                가족과 시간을 보내고 싶습니다. 취미 활동을 즐기고 있습니다.
                운동을 하러 갑니다. 책을 읽고 있습니다.""",
                "url": "https://example.com/daily-life",
                "source_type": "common"
            },
            {
                "title": "학술적 표현들",
                "content": """연구 결과에 따르면 이것이 사실입니다.
                분석해보면 다음과 같은 결론을 얻을 수 있습니다.
                실험을 통해 확인할 수 있었습니다.
                데이터를 바탕으로 판단하면 맞는 것 같습니다.
                이론적으로 접근해보겠습니다.""",
                "url": "https://example.com/academic-expressions",
                "source_type": "academic"
            },
            {
                "title": "비즈니스 표현들",
                "content": """회의를 진행하겠습니다. 프로젝트가 진행 중입니다.
                목표를 달성했습니다. 성과가 좋습니다.
                고객과 미팅이 있습니다. 계약을 체결했습니다.
                매출이 증가했습니다. 비용을 절감해야 합니다.""",
                "url": "https://example.com/business-expressions",
                "source_type": "business"
            },
            {
                "title": "기술과 컴퓨터 용어",
                "content": """프로그램을 실행합니다. 데이터를 저장합니다.
                파일을 다운로드 받았습니다. 웹사이트에 접속했습니다.
                소프트웨어를 설치합니다. 하드웨어를 업그레이드합니다.
                네트워크가 연결되었습니다. 보안이 중요합니다.""",
                "url": "https://example.com/tech-terms",
                "source_type": "technology"
            },
            {
                "title": "음식과 요리 관련",
                "content": """맛있는 음식을 먹었습니다. 요리를 배우고 싶습니다.
                새로운 레시피를 시도해봤습니다. 재료를 준비했습니다.
                음식점에서 식사했습니다. 집에서 만든 음식이 최고입니다.
                건강한 식단을 유지하고 있습니다. 다이어트를 시작했습니다.""",
                "url": "https://example.com/food-cooking",
                "source_type": "food"
            },
            {
                "title": "날씨와 계절 표현",
                "content": """오늘 날씨가 맑습니다. 비가 내리고 있습니다.
                바람이 강하게 붑니다. 눈이 많이 왔습니다.
                봄이 왔습니다. 여름이 더웠습니다.
                가을 단풍이 아름답습니다. 겨울이 추웠습니다.""",
                "url": "https://example.com/weather-seasons",
                "source_type": "weather"
            }
        ]
        
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
        
        for doc in common_docs:
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
        print(f"✅ {len(common_docs)}개 일반 표현 문서가 추가되었습니다.")
        
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
    add_common_texts()