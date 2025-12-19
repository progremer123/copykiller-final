-- 초기 데이터 삽입

-- 샘플 문서 소스 데이터
INSERT INTO document_sources (title, content, source_type, url, language) VALUES
('인공지능과 학술 연구의 미래', 
 '인공지능 기술의 발전은 학술 연구 방법론에 혁신적인 변화를 가져오고 있다. 머신러닝과 딥러닝 알고리즘을 활용한 데이터 분석은 기존의 연구 패러다임을 크게 변화시키고 있으며, 연구자들은 이제 대용량 데이터를 효율적으로 처리하고 분석할 수 있게 되었다. 특히 자연어 처리 기술의 발전으로 텍스트 마이닝과 문헌 분석이 자동화되면서, 연구의 속도와 정확성이 크게 향상되었다.',
 'academic',
 'https://example-academic.com/ai-research',
 'ko'),

('기계학습 응용 분야와 산업 혁신',
 '기계학습 기술은 다양한 산업 분야에서 혁신적인 변화를 주도하고 있다. 제조업에서는 예측 유지보수와 품질 관리에, 금융업에서는 위험 관리와 자동 거래에, 의료 분야에서는 진단 보조와 신약 개발에 활용되고 있다. 이러한 응용 사례들은 기계학습이 단순한 기술을 넘어 사회 전반의 디지털 전환을 이끄는 핵심 동력임을 보여준다.',
 'article',
 'https://example-tech.com/ml-applications',
 'ko'),

('학술 글쓰기의 윤리와 표절 방지',
 '학술 글쓰기에서 가장 중요한 것은 윤리적 기준을 준수하는 것이다. 표절은 학술적 부정행위의 대표적인 사례로, 타인의 아이디어나 연구 결과를 적절한 인용 없이 사용하는 행위를 말한다. 현대의 디지털 환경에서는 다양한 표절 검사 도구들이 개발되어 연구자들이 자신의 작업의 독창성을 확인할 수 있도록 돕고 있다.',
 'academic',
 'https://example-ethics.edu/plagiarism-prevention',
 'ko'),

('자연어 처리 기술의 발전과 응용',
 '자연어 처리(NLP) 기술은 컴퓨터가 인간의 언어를 이해하고 처리할 수 있도록 하는 인공지능의 핵심 분야이다. 최근 트랜스포머 아키텍처와 대규모 언어 모델의 등장으로 NLP 성능이 급격히 향상되었으며, 번역, 요약, 질의응답, 텍스트 생성 등 다양한 작업에서 인간 수준의 성능을 보이고 있다.',
 'academic',
 'https://example-nlp.com/nlp-advances',
 'ko'),

('데이터 마이닝과 지식 발견',
 '데이터 마이닝은 대용량 데이터에서 숨겨진 패턴과 유용한 정보를 발견하는 과정이다. 클러스터링, 분류, 연관 규칙 학습 등의 기법을 통해 데이터에서 의미 있는 인사이트를 추출할 수 있으며, 이는 비즈니스 의사결정과 과학적 발견에 중요한 역할을 한다.',
 'article',
 'https://example-datamining.com/knowledge-discovery',
 'ko');

-- 샘플 검사 세션 (테스트용)
INSERT INTO user_sessions (id, ip_address, user_agent, check_count) VALUES
('session-001', '127.0.0.1', 'Mozilla/5.0 (Test Browser)', 5),
('session-002', '192.168.1.100', 'Chrome/118.0.0.0', 3);

-- 샘플 통계 데이터
INSERT INTO statistics (date, total_checks, completed_checks, error_checks, avg_similarity_score, avg_processing_time)
VALUES 
(CURRENT_DATE - INTERVAL '1 day', 45, 42, 3, 35.6, 2.3),
(CURRENT_DATE - INTERVAL '2 days', 38, 36, 2, 28.9, 2.1),
(CURRENT_DATE - INTERVAL '3 days', 52, 49, 3, 42.1, 2.5);

-- N-gram 인덱스 생성 (샘플 데이터 기반)
INSERT INTO ngrams (source_id, ngram_text, ngram_size, position_start, position_end)
SELECT 
    id as source_id,
    substring(content from generate_series(1, length(content) - 4)) as ngram_text,
    5 as ngram_size,
    generate_series(1, length(content) - 4) as position_start,
    generate_series(5, length(content)) as position_end
FROM document_sources
WHERE length(content) > 10
LIMIT 1000; -- 샘플 데이터이므로 제한

-- 기본 설정 테이블
CREATE TABLE IF NOT EXISTS app_settings (
    key VARCHAR(100) PRIMARY KEY,
    value TEXT NOT NULL,
    description TEXT,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 기본 설정 값들
INSERT INTO app_settings (key, value, description) VALUES
('similarity_threshold', '0.3', '표절 의심 최소 유사도 임계값'),
('high_similarity_threshold', '0.7', '높은 유사도 임계값'),
('max_file_size', '10485760', '최대 파일 크기 (10MB)'),
('supported_languages', 'ko,en', '지원 언어'),
('processing_timeout', '300', '처리 타임아웃 (초)'),
('max_text_length', '100000', '최대 텍스트 길이'),
('ngram_size', '5', '기본 N-gram 크기');

-- 데이터베이스 버전 정보
CREATE TABLE IF NOT EXISTS schema_version (
    version VARCHAR(20) PRIMARY KEY,
    applied_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    description TEXT
);

INSERT INTO schema_version (version, description) VALUES
('1.0.0', '초기 스키마 생성');

-- 성능 최적화를 위한 추가 설정
-- 자동 VACUUM 설정
ALTER TABLE plagiarism_checks SET (autovacuum_vacuum_scale_factor = 0.1);
ALTER TABLE plagiarism_matches SET (autovacuum_vacuum_scale_factor = 0.1);
ALTER TABLE document_sources SET (autovacuum_vacuum_scale_factor = 0.2);

-- 쿼리 성능 향상을 위한 통계 정보 업데이트
ANALYZE plagiarism_checks;
ANALYZE plagiarism_matches;
ANALYZE document_sources;
ANALYZE ngrams;