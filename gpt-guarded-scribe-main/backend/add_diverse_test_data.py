#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
다양한 주제의 테스트 데이터 추가 스크립트
표절 검사가 제대로 작동하도록 풍부한 문서 데이터베이스를 구축합니다.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import sessionmaker
from database import engine
from models import DocumentSource
from datetime import datetime

def add_diverse_test_data():
    """다양한 주제의 테스트 문서 추가"""
    
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        # 기후 변화 관련 문서들
        climate_docs = [
            {
                "title": "기후 변화의 원인과 영향",
                "content": """
                기후 변화는 21세기 인류가 직면한 가장 심각한 도전 중 하나입니다. 지구 온난화로 인한 기온 상승은 
                극지방의 빙하를 녹이고 해수면 상승을 가져오고 있습니다. 산업혁명 이후 화석 연료의 사용 증가로 
                대기 중 온실가스 농도가 급격히 증가했습니다. 이산화탄소, 메탄, 아산화질소 등의 온실가스는 
                지구의 복사 평형을 변화시켜 지구 표면 온도를 상승시킵니다. 기후 변화의 주요 원인은 
                인간 활동에 의한 온실가스 배출입니다.
                """,
                "url": "https://example.com/climate-change",
                "source_type": "academic"
            },
            {
                "title": "지구 온난화와 환경 파괴",
                "content": """
                지구 온난화는 지구의 평균 기온이 상승하는 현상으로, 주로 인간 활동으로 인한 온실가스 배출이 
                주된 원인입니다. 온실가스 중 가장 큰 비중을 차지하는 것은 이산화탄소로, 화석 연료의 연소, 
                산림 벌채, 시멘트 생산 등에서 발생합니다. 지구 온난화로 인해 극지방의 빙하가 녹고, 
                해수면이 상승하며, 기상 이변이 빈발하고 있습니다. 이러한 변화는 생태계 파괴와 
                인간 사회에 심각한 영향을 미치고 있습니다.
                """,
                "url": "https://example.com/global-warming",
                "source_type": "research"
            }
        ]
        
        # 인공지능 관련 문서들
        ai_docs = [
            {
                "title": "인공지능의 정의와 발전 역사",
                "content": """
                인공지능(Artificial Intelligence, AI)은 인간의 지능을 모방하여 기계가 학습, 추론, 
                인식 등의 인지적 기능을 수행할 수 있도록 하는 기술입니다. 1956년 다트머스 컨퍼런스에서 
                처음 제안된 이후, 인공지능은 여러 단계의 발전을 거쳐왔습니다. 초기에는 규칙 기반 시스템이 
                주를 이루었으나, 1980년대 기계학습이 등장하면서 새로운 전환점을 맞았습니다. 
                최근 딥러닝 기술의 발전으로 컴퓨터 비전, 자연어 처리, 음성 인식 등 다양한 분야에서 
                인간 수준의 성능을 보이고 있습니다.
                """,
                "url": "https://example.com/ai-definition",
                "source_type": "encyclopedia"
            },
            {
                "title": "머신러닝과 딥러닝 기술",
                "content": """
                머신러닝은 컴퓨터가 명시적으로 프로그래밍되지 않고도 데이터로부터 패턴을 학습할 수 있는 
                인공지능의 한 분야입니다. 지도학습, 비지도학습, 강화학습으로 구분되며, 각각 다른 
                학습 방법론을 사용합니다. 딥러닝은 인공신경망을 깊게 쌓아 복잡한 패턴을 학습하는 
                머신러닝의 한 방법으로, 이미지 인식, 자연어 처리, 게임 등에서 혁신적인 성과를 보였습니다. 
                합성곱 신경망(CNN), 순환 신경망(RNN), 트랜스포머 등 다양한 아키텍처가 개발되었습니다.
                """,
                "url": "https://example.com/machine-learning",
                "source_type": "technical"
            }
        ]
        
        # 교육 관련 문서들
        education_docs = [
            {
                "title": "디지털 시대의 교육 혁신",
                "content": """
                21세기 디지털 시대에 교육 분야도 급격한 변화를 맞고 있습니다. 온라인 교육 플랫폼의 
                확산으로 시간과 공간의 제약 없이 학습할 수 있게 되었고, 개인화된 학습 경험을 제공하는 
                적응형 학습 시스템이 등장했습니다. 가상현실(VR)과 증강현실(AR) 기술을 활용한 
                몰입형 교육 콘텐츠는 학습자의 참여도와 이해도를 높이고 있습니다. 
                인공지능을 활용한 개별 맞춤형 교육은 학습자의 수준과 속도에 맞춰 
                최적화된 학습 경로를 제공합니다.
                """,
                "url": "https://example.com/digital-education",
                "source_type": "article"
            }
        ]
        
        # 경제 관련 문서들
        economy_docs = [
            {
                "title": "디지털 경제와 플랫폼 비즈니스",
                "content": """
                디지털 경제는 디지털 기술을 기반으로 한 새로운 경제 패러다임입니다. 
                플랫폼 비즈니스 모델이 전통적인 산업 구조를 변화시키고 있으며, 
                네트워크 효과를 통해 빠른 성장과 시장 지배력을 확보할 수 있게 되었습니다. 
                공유 경제, 구독 경제, 크리에이터 경제 등 새로운 비즈니스 모델들이 등장하면서 
                경제 활동의 방식이 근본적으로 변화하고 있습니다. 데이터가 새로운 자본으로 
                인식되면서 데이터 경제학이 중요한 연구 분야로 부상하고 있습니다.
                """,
                "url": "https://example.com/digital-economy",
                "source_type": "business"
            }
        ]
        
        all_docs = climate_docs + ai_docs + education_docs + economy_docs
        
        print(f"📚 {len(all_docs)}개의 테스트 문서 추가 중...")
        
        for doc_data in all_docs:
            # 이미 존재하는지 확인
            existing = db.query(DocumentSource).filter(
                DocumentSource.title == doc_data["title"]
            ).first()
            
            if existing:
                print(f"⚠️ 이미 존재: {doc_data['title']}")
                continue
            
            # 새 문서 생성
            doc = DocumentSource(
                title=doc_data["title"],
                content=doc_data["content"].strip(),
                url=doc_data["url"],
                source_type=doc_data["source_type"],
                created_at=datetime.now(),
                updated_at=datetime.now(),
                is_active=True
            )
            
            db.add(doc)
            print(f"✅ 추가됨: {doc_data['title']}")
        
        db.commit()
        
        # 최종 문서 수 확인
        total_count = db.query(DocumentSource).count()
        print(f"\n🎉 테스트 데이터 추가 완료!")
        print(f"📊 총 문서 수: {total_count}개")
        
        # 주제별 분포 확인
        by_type = db.query(DocumentSource.source_type, db.func.count()).group_by(DocumentSource.source_type).all()
        print(f"\n📋 주제별 분포:")
        for source_type, count in by_type:
            print(f"   - {source_type}: {count}개")
        
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    add_diverse_test_data()