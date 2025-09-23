-- GPT 표절 검사기 데이터베이스 스키마

-- 확장 모듈 활성화
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";
CREATE EXTENSION IF NOT EXISTS "btree_gin";

-- 표절 검사 테이블
CREATE TABLE IF NOT EXISTS plagiarism_checks (
    id VARCHAR(36) PRIMARY KEY DEFAULT uuid_generate_v4()::text,
    original_text TEXT NOT NULL,
    similarity_score FLOAT DEFAULT 0.0,
    status VARCHAR(20) DEFAULT 'checking' CHECK (status IN ('checking', 'completed', 'error')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    file_name VARCHAR(255),
    file_type VARCHAR(100),
    processing_time FLOAT,
    text_length INTEGER GENERATED ALWAYS AS (LENGTH(original_text)) STORED,
    word_count INTEGER GENERATED ALWAYS AS (
        ARRAY_LENGTH(STRING_TO_ARRAY(TRIM(original_text), ' '), 1)
    ) STORED
);

-- 표절 매치 테이블
CREATE TABLE IF NOT EXISTS plagiarism_matches (
    id SERIAL PRIMARY KEY,
    check_id VARCHAR(36) NOT NULL REFERENCES plagiarism_checks(id) ON DELETE CASCADE,
    matched_text TEXT NOT NULL,
    source_text TEXT NOT NULL,
    source_title VARCHAR(500) NOT NULL,
    source_url TEXT,
    similarity_score FLOAT NOT NULL,
    start_index INTEGER NOT NULL,
    end_index INTEGER NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    match_length INTEGER GENERATED ALWAYS AS (end_index - start_index) STORED
);

-- 문서 소스 테이블
CREATE TABLE IF NOT EXISTS document_sources (
    id SERIAL PRIMARY KEY,
    title VARCHAR(500) NOT NULL,
    content TEXT NOT NULL,
    url TEXT,
    source_type VARCHAR(50) NOT NULL DEFAULT 'web' CHECK (source_type IN ('academic', 'web', 'book', 'article', 'thesis')),
    vector_embedding JSON,
    content_hash VARCHAR(64) UNIQUE GENERATED ALWAYS AS (
        ENCODE(SHA256(content::bytea), 'hex')
    ) STORED,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    language VARCHAR(10) DEFAULT 'ko',
    domain VARCHAR(100)
);

-- 사용자 세션 테이블
CREATE TABLE IF NOT EXISTS user_sessions (
    id VARCHAR(36) PRIMARY KEY DEFAULT uuid_generate_v4()::text,
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_activity TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    check_count INTEGER DEFAULT 0,
    total_processing_time FLOAT DEFAULT 0.0
);

-- N-gram 테이블 (빠른 검색을 위한)
CREATE TABLE IF NOT EXISTS ngrams (
    id SERIAL PRIMARY KEY,
    source_id INTEGER NOT NULL REFERENCES document_sources(id) ON DELETE CASCADE,
    ngram_text VARCHAR(500) NOT NULL,
    ngram_size INTEGER NOT NULL,
    position_start INTEGER NOT NULL,
    position_end INTEGER NOT NULL,
    frequency INTEGER DEFAULT 1
);

-- 인덱스 생성
CREATE INDEX IF NOT EXISTS idx_plagiarism_checks_status ON plagiarism_checks(status);
CREATE INDEX IF NOT EXISTS idx_plagiarism_checks_created_at ON plagiarism_checks(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_plagiarism_checks_similarity ON plagiarism_checks(similarity_score DESC);

CREATE INDEX IF NOT EXISTS idx_plagiarism_matches_check_id ON plagiarism_matches(check_id);
CREATE INDEX IF NOT EXISTS idx_plagiarism_matches_similarity ON plagiarism_matches(similarity_score DESC);
CREATE INDEX IF NOT EXISTS idx_plagiarism_matches_source_title ON plagiarism_matches USING GIN(source_title gin_trgm_ops);

CREATE INDEX IF NOT EXISTS idx_document_sources_content_hash ON document_sources(content_hash);
CREATE INDEX IF NOT EXISTS idx_document_sources_source_type ON document_sources(source_type);
CREATE INDEX IF NOT EXISTS idx_document_sources_is_active ON document_sources(is_active);
CREATE INDEX IF NOT EXISTS idx_document_sources_content_search ON document_sources USING GIN(to_tsvector('korean', content));
CREATE INDEX IF NOT EXISTS idx_document_sources_title_search ON document_sources USING GIN(to_tsvector('korean', title));

CREATE INDEX IF NOT EXISTS idx_user_sessions_ip ON user_sessions(ip_address);
CREATE INDEX IF NOT EXISTS idx_user_sessions_last_activity ON user_sessions(last_activity DESC);

CREATE INDEX IF NOT EXISTS idx_ngrams_text ON ngrams USING GIN(ngram_text gin_trgm_ops);
CREATE INDEX IF NOT EXISTS idx_ngrams_source_id ON ngrams(source_id);
CREATE INDEX IF NOT EXISTS idx_ngrams_size ON ngrams(ngram_size);

-- 전문 검색 인덱스
CREATE INDEX IF NOT EXISTS idx_full_text_search ON document_sources USING GIN(
    to_tsvector('korean', title || ' ' || content)
);

-- 트리거 함수들
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- 업데이트 트리거
CREATE TRIGGER update_plagiarism_checks_updated_at 
    BEFORE UPDATE ON plagiarism_checks 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_document_sources_updated_at 
    BEFORE UPDATE ON document_sources 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- 파티션 테이블 (대량 데이터 처리용)
CREATE TABLE IF NOT EXISTS plagiarism_checks_partitioned (
    LIKE plagiarism_checks INCLUDING ALL
) PARTITION BY RANGE (created_at);

-- 월별 파티션 예시
CREATE TABLE IF NOT EXISTS plagiarism_checks_2024_01 PARTITION OF plagiarism_checks_partitioned
    FOR VALUES FROM ('2024-01-01') TO ('2024-02-01');

-- 통계 테이블
CREATE TABLE IF NOT EXISTS statistics (
    id SERIAL PRIMARY KEY,
    date DATE DEFAULT CURRENT_DATE,
    total_checks INTEGER DEFAULT 0,
    completed_checks INTEGER DEFAULT 0,
    error_checks INTEGER DEFAULT 0,
    avg_similarity_score FLOAT DEFAULT 0.0,
    avg_processing_time FLOAT DEFAULT 0.0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 통계 업데이트 함수
CREATE OR REPLACE FUNCTION update_daily_statistics()
RETURNS VOID AS $$
BEGIN
    INSERT INTO statistics (
        date, 
        total_checks, 
        completed_checks, 
        error_checks, 
        avg_similarity_score, 
        avg_processing_time
    )
    SELECT 
        CURRENT_DATE,
        COUNT(*),
        COUNT(*) FILTER (WHERE status = 'completed'),
        COUNT(*) FILTER (WHERE status = 'error'),
        AVG(similarity_score) FILTER (WHERE status = 'completed'),
        AVG(processing_time) FILTER (WHERE status = 'completed')
    FROM plagiarism_checks 
    WHERE DATE(created_at) = CURRENT_DATE
    ON CONFLICT (date) DO UPDATE SET
        total_checks = EXCLUDED.total_checks,
        completed_checks = EXCLUDED.completed_checks,
        error_checks = EXCLUDED.error_checks,
        avg_similarity_score = EXCLUDED.avg_similarity_score,
        avg_processing_time = EXCLUDED.avg_processing_time;
END;
$$ LANGUAGE plpgsql;

-- 권한 설정
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO postgres;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO postgres;