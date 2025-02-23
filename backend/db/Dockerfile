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

# GPG 키 등록
RUN mkdir -p /etc/apt/keyrings \
 && curl -fsSL https://dl.google.com/linux/linux_signing_key.pub -o /tmp/google.pub \
 && gpg --dearmor /tmp/google.pub \
 && mv /tmp/google.pub.gpg /etc/apt/keyrings/google.gpg \
 && rm /tmp/google.pub

# Chrome 저장소 등록
RUN echo "deb [arch=amd64 signed-by=/etc/apt/keyrings/google.gpg] http://dl.google.com/linux/chrome/deb/ stable main" \
    > /etc/apt/sources.list.d/google-chrome.list

# 최신 Stable Chrome 설치
RUN apt-get update \
 && apt-get install -y google-chrome-stable \
 && rm -rf /var/lib/apt/lists/*

# 최신 ChromeDriver 설치
RUN CHROMEDRIVER_VERSION=$(curl -sS https://chromedriver.storage.googleapis.com/LATEST_RELEASE) \
 && wget -N https://chromedriver.storage.googleapis.com/$CHROMEDRIVER_VERSION/chromedriver_linux64.zip -P /tmp/ \
 && unzip /tmp/chromedriver_linux64.zip -d /usr/local/bin/ \
 && rm /tmp/chromedriver_linux64.zip

# 가상 디스플레이 설정
ENV DISPLAY=:99

# Python 패키지 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 소스 복사
COPY . .

# FastAPI & Xvfb 실행
CMD ["bash", "-c", "Xvfb :99 -screen 0 1920x1080x24 & uvicorn app.main:app --host 0.0.0.0 --port 8000"]
