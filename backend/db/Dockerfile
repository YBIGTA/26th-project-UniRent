FROM python:3.10
WORKDIR /app

# 1. 필수 패키지 설치
RUN apt-get update && apt-get install -y --no-install-recommends \
    wget curl gnupg ca-certificates apt-transport-https \
    unzip xvfb fonts-liberation libappindicator3-1 libasound2 \
    libgbm-dev xdg-utils libnss3 libx11-xcb1 libxcomposite1 libxcursor1 \
    libxdamage1 libxfixes3 libxi6 libxrandr2 libxrender1 libxss1 libxtst6 \
 && rm -rf /var/lib/apt/lists/*

# 2. GPG 키 등록
RUN mkdir -p /etc/apt/keyrings \
 && curl -fsSL https://dl.google.com/linux/linux_signing_key.pub -o /tmp/google.pub \
 && gpg --dearmor /tmp/google.pub \
 && mv /tmp/google.pub.gpg /etc/apt/keyrings/google.gpg \
 && rm /tmp/google.pub

# 3. Chrome 저장소 등록
RUN echo "deb [arch=amd64 signed-by=/etc/apt/keyrings/google.gpg] http://dl.google.com/linux/chrome/deb/ stable main" \
    > /etc/apt/sources.list.d/google-chrome.list

# 4. 최신 Stable Chrome 설치
RUN apt-get update \
 && apt-get install -y google-chrome-stable \
 && rm -rf /var/lib/apt/lists/*

# 5. '최신' ChromeDriver 설치 (버전 매칭 로직 없음)
RUN CHROMEDRIVER_VERSION=$(curl -sS https://chromedriver.storage.googleapis.com/LATEST_RELEASE) \
 && wget -N https://chromedriver.storage.googleapis.com/$CHROMEDRIVER_VERSION/chromedriver_linux64.zip -P /tmp/ \
 && unzip /tmp/chromedriver_linux64.zip -d /usr/local/bin/ \
 && rm /tmp/chromedriver_linux64.zip

# 6. 가상 디스플레이 설정
ENV DISPLAY=:99

# 7. Python 패키지 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 8. 소스 복사
COPY . .

# 9. FastAPI & Xvfb
CMD ["bash", "-c", "Xvfb :99 -screen 0 1920x1080x24 & uvicorn app.main:app --host 0.0.0.0 --port 8000"]
