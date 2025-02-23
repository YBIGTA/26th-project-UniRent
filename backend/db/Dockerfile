# Python 3.10 기반 이미지 사용
FROM python:3.10

# 작업 디렉토리 설정
WORKDIR /app

# 필수 패키지 설치
RUN apt-get update && apt-get install -y --no-install-recommends \
    wget curl gnupg ca-certificates apt-transport-https \
    unzip xvfb fonts-liberation libappindicator3-1 libasound2 \
    libgbm-dev xdg-utils libnss3 libx11-xcb1 libxcomposite1 libxcursor1 \
    libxdamage1 libxfixes3 libxi6 libxrandr2 libxrender1 libxss1 libxtst6 \
 && rm -rf /var/lib/apt/lists/*

# Chrome 133 다운로드 및 설치
RUN wget -O /tmp/chrome-linux64.zip https://storage.googleapis.com/chrome-for-testing-public/133.0.6943.126/linux64/chrome-linux64.zip \
    && unzip /tmp/chrome-linux64.zip -d /opt/chrome/ \
    && rm /tmp/chrome-linux64.zip \
    && chmod +x /opt/chrome/chrome-linux64/chrome  # ✅ 실행 권한 부여

# Chrome 실행 파일 경로 설정
ENV CHROME_BIN=/opt/chrome/chrome-linux64/chrome
ENV PATH="$CHROME_BIN:$PATH"

# ChromeDriver 133 다운로드 및 설치
RUN wget -O /tmp/chromedriver-linux64.zip https://storage.googleapis.com/chrome-for-testing-public/133.0.6943.126/linux64/chromedriver-linux64.zip \
    && unzip /tmp/chromedriver-linux64.zip -d /usr/local/bin/ \
    && rm /tmp/chromedriver-linux64.zip \
    && mv /usr/local/bin/chromedriver-linux64/chromedriver /usr/local/bin/chromedriver \
    && chmod +x /usr/local/bin/chromedriver  # ✅ 실행 권한 부여

# 환경 변수 설정 (Selenium이 Chrome 및 Chromedriver를 찾을 수 있도록 함)
ENV DISPLAY=:99
ENV PATH="/usr/local/bin:$PATH"

# Python 패키지 설치
COPY requirements.txt . 
RUN pip install --no-cache-dir -r requirements.txt

# 소스 코드 복사
COPY . .

# FastAPI & Xvfb 실행
CMD ["bash", "-c", "Xvfb :99 -screen 0 1920x1080x24 & uvicorn app.main:app --host 0.0.0.0 --port 8000"]
