FROM python:3.11-slim

# 작업 디렉토리 설정
WORKDIR /app

# 시스템 의존성 설치
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libpq-dev \
    libmagic1 \
    && rm -rf /var/lib/apt/lists/*

# Python 의존성 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 애플리케이션 코드 복사
COPY . .

# 포트 노출
ENV PORT 8080
EXPOSE 8080

# 애플리케이션 시작
# EXPOSE 8006  <-- 이 줄은 지우거나 주석 처리해도 됩니다. (Cloud Run에선 필수가 아님)

# CMD 부분을 아래와 같이 수정 (8006 대신 8000이나 $PORT를 자동으로 받게 설정)
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port 8080"]