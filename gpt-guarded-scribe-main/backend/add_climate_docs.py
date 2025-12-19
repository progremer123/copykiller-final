#!/usr/bin/env python3
"""기후 변화 관련 문서 추가"""

import sqlite3
from datetime import datetime

def add_climate_documents():
    try:
        conn = sqlite3.connect("plagiarism.db")
        cursor = conn.cursor()
        
        climate_docs = [
            {
                "title": "기후 변화와 지구 온난화",
                "content": """기후 변화는 21세기 인류가 직면한 가장 심각한 도전 중 하나입니다. 
                지구 온난화로 인한 해수면 상승, 극단적 기상 현상의 증가, 생태계 파괴 등은 
                전 세계적인 대응을 필요로 합니다. 온실가스 배출 감소와 재생에너지 확산이 
                시급한 과제입니다.""",
                "url": "https://example.com/climate-change",
                "source_type": "test"
            },
            {
                "title": "환경 보호와 지속가능한 발전",
                "content": """환경 보호는 현재와 미래 세대를 위한 필수적인 노력입니다.
                지구 온난화와 기후 변화에 대응하기 위해서는 화석 연료 사용을 줄이고
                청정 에너지로의 전환이 필요합니다. 지속가능한 발전을 통해 경제 성장과
                환경 보전의 균형을 맞춰야 합니다.""",
                "url": "https://example.com/environment-protection",
                "source_type": "test"
            }
        ]
        
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
        
        for doc in climate_docs:
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
        print(f"✅ {len(climate_docs)}개 기후 변화 문서가 추가되었습니다.")
        
        # 전체 문서 수 확인
        cursor.execute("SELECT COUNT(*) FROM document_sources WHERE is_active = 1")
        total_docs = cursor.fetchone()[0]
        print(f"📚 총 활성 문서 수: {total_docs}개")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ 오류 발생: {e}")

if __name__ == "__main__":
    add_climate_documents()