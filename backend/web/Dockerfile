# Python 3.9 이미지 사용
FROM python:3.9

# 작업 디렉토리 설정
WORKDIR /

# 필수 패키지 설치 (MySQL 클라이언트 포함)
RUN apt-get update && apt-get install -y \
    default-mysql-client \
    python3-dev \
    default-libmysqlclient-dev \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 소스 코드 복사
COPY . .

# 컨테이너 실행 시 실행할 명령어
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "5000", "--reload"]