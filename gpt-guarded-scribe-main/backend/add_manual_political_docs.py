#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from database import get_db
from models import DocumentSource
from datetime import datetime

def add_manual_political_docs():
    """수동으로 정치/시사 관련 문서 추가"""
    
    db = next(get_db())
    
    # 정치/시사 관련 텍스트들 (실제 뉴스 기사 스타일)
    political_docs = [
        {
            "title": "한미 정상회담 결과 분석",
            "url": "https://example.com/korea-us-summit",
            "content": """
            이번 한미 정상회담에서 양국 지도자들은 다양한 현안에 대해 논의했다. 
            대통령은 "미국은 물론 자국 이익을 극대화하려고 하겠지만 그게 한국에 파멸적인 결과를 초래할 정도여서는 안 된다"고 강조했다.
            
            대통령은 또한 "대화가 계속되고 있으며 생각에 일부 차이가 있지만, 지연이 꼭 실패를 의미하지는 않는다"면서 
            "한국은 미국의 동맹이자 우방이기 때문에 우리는 모두가 받아들일 수 있는 합리적인 결과에 도달할 수 있을 것"이라고 밝혔다.
            
            트럼프 대통령은 아시아 순방길에 오르면서 "타결에 매우 가깝다"며 "그들이 준비가 된다면, 나는 준비됐다"고 했었다.
            양국 간 협상이 진행되고 있으며, 합리적인 결과를 위해 지속적인 노력이 필요한 상황이다.
            """
        },
        {
            "title": "한미 통상 협상 현황",
            "url": "https://example.com/trade-negotiation",
            "content": """
            한미 간 통상 협상이 막바지에 이르렀다. 대통령은 기자회견에서 협상 진행 상황에 대해 언급했다.
            "미국은 자국 이익을 극대화하려 하지만, 한국에 파멸적 결과를 초래해서는 안 된다"는 입장을 재확인했다.
            
            협상 관계자들은 "생각에 일부 차이가 있지만 타결 지연이 꼭 실패를 의미하지는 않는다"고 설명했다.
            "한국은 미국의 동맹이자 우방이기 때문에 합리적인 결과에 도달할 수 있을 것"이라는 전망도 나왔다.
            
            트럼프 대통령의 "타결에 매우 가깝다"는 발언과 "준비가 된다면 나는 준비됐다"는 표현이 주목받고 있다.
            """
        },
        {
            "title": "외교부 브리핑 주요 내용",
            "url": "https://example.com/foreign-ministry-brief",
            "content": """
            외교부는 오늘 정례 브리핑에서 한미관계 현안에 대해 설명했다.
            대통령은 "대화가 계속되고 있으며 일부 차이는 있지만 지연이 실패를 의미하지 않는다"고 말했다.
            
            "한국과 미국은 동맹이자 우방 관계로, 모두가 받아들일 수 있는 합리적인 결과 도달이 가능하다"고 강조했다.
            미국 측에서는 "자국 이익 극대화를 추구하되 한국에 파멸적 결과는 피해야 한다"는 입장이 전해졌다.
            
            트럼프 대통령의 최근 발언 중 "타결이 임박했다"와 "그들이 준비되면 나도 준비됐다"는 표현이 온도차를 보여준다.
            """
        },
        {
            "title": "정치권 반응과 전망",
            "url": "https://example.com/political-reaction",
            "content": """
            정치권에서는 최근 대통령 발언에 대한 다양한 해석이 나오고 있다.
            "미국이 자국 이익을 극대화하려 하지만 한국에 파멸적 결과를 초래하면 안 된다"는 발언의 의미를 둘러싼 논의가 활발하다.
            
            야당에서는 "대화 지속과 일부 차이에도 불구하고 타결 지연이 실패는 아니다"라는 대통령 입장에 우려를 표했다.
            "한국은 미국의 동맹이자 우방으로 합리적 결과 도달이 가능하다"는 낙관론에 대해서도 신중한 접근을 요구했다.
            
            트럼프의 "타결 임박" 발언과 "준비 완료" 표현 사이의 온도차 분석도 이어지고 있다.
            """
        }
    ]
    
    print("📄 정치/시사 관련 문서 수동 추가...")
    
    saved_count = 0
    for doc in political_docs:
        try:
            # 중복 확인
            existing = db.query(DocumentSource).filter(
                DocumentSource.title == doc["title"]
            ).first()
            
            if not existing:
                source = DocumentSource(
                    title=doc["title"],
                    url=doc["url"],
                    content=doc["content"].strip(),
                    source_type="article",
                    is_active=True
                )
                db.add(source)
                saved_count += 1
                print(f"✅ 저장: {doc['title']}")
            else:
                print(f"⚠️  이미 존재: {doc['title']}")
                
        except Exception as e:
            print(f"❌ 오류: {doc['title']} - {e}")
    
    db.commit()
    print(f"\n🎉 총 {saved_count}개의 정치/시사 문서를 추가했습니다!")
    
    # 총 문서 수 확인
    total_docs = db.query(DocumentSource).filter(DocumentSource.is_active == True).count()
    print(f"📚 현재 총 활성 문서 수: {total_docs}개")

if __name__ == "__main__":
    add_manual_political_docs()