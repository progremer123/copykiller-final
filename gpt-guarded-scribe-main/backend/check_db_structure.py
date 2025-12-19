#!/usr/bin/env python3
"""데이터베이스 구조 확인"""

import sqlite3
import os

def check_database_structure():
    db_path = "plagiarism.db"
    
    if not os.path.exists(db_path):
        print("❌ 데이터베이스 파일을 찾을 수 없습니다.")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 모든 테이블 조회
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        print(f"📊 데이터베이스 테이블: {len(tables)}개")
        
        for table_name in tables:
            table = table_name[0]
            print(f"\n📋 테이블: {table}")
            
            # 테이블 스키마
            cursor.execute(f"PRAGMA table_info({table})")
            columns = cursor.fetchall()
            for col in columns:
                print(f"   - {col[1]} ({col[2]})")
                
            # 데이터 수
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            print(f"   📈 데이터 수: {count}개")
            
            # 샘플 데이터
            if count > 0:
                cursor.execute(f"SELECT * FROM {table} LIMIT 3")
                samples = cursor.fetchall()
                print(f"   🔍 샘플:")
                for sample in samples:
                    print(f"      {sample}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ 데이터베이스 오류: {e}")

if __name__ == "__main__":
    check_database_structure()