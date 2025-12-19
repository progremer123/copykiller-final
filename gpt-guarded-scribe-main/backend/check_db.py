#!/usr/bin/env python3
"""데이터베이스 문서 확인"""

import sqlite3
import os

def check_database_documents():
    db_path = "plagiarism.db"
    
    if not os.path.exists(db_path):
        print("❌ 데이터베이스 파일을 찾을 수 없습니다.")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 문서 테이블 조회
        cursor.execute("SELECT title, content FROM documents WHERE is_active = 1")
        docs = cursor.fetchall()
        
        print(f"📚 활성 문서 수: {len(docs)}개")
        print("\n📄 데이터베이스 문서 목록:")
        
        for i, (title, content) in enumerate(docs, 1):
            print(f"\n{i}. 제목: {title}")
            print(f"   내용: {content[:100]}...")
            
        conn.close()
        
    except Exception as e:
        print(f"❌ 데이터베이스 오류: {e}")

if __name__ == "__main__":
    check_database_documents()