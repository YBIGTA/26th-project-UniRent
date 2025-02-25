from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
import time
import threading
from database.mongodb_connection import MongoDB

# 라우터 추가
from app.routes import api

# 크롤러 추가
from crawler.crawler import ThreeThreeCrawler, HowBoutHereCrawler
from crawler.update import *

import logging

logging.basicConfig(
    level=logging.INFO,  # 출력할 로그 레벨 설정
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',  # 로그 포맷 설정
    handlers=[
        logging.StreamHandler()  # 콘솔 출력 핸들러
        # 필요에 따라 파일 핸들러 추가 가능: logging.FileHandler('app.log')
    ]
)

# 이후 다른 모듈에서도 import logging 후 로그 호출 가능
logging.info("애플리케이션 시작")

# 환경 변수에서 포트 가져오기 (기본값 8000)
PORT = int(os.getenv("PORT", 8000))

app = FastAPI()

# CORS 설정 추가
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"],  
)

output_dir = "./data"
Three = ThreeThreeCrawler(output_dir)
How = HowBoutHereCrawler(output_dir)

CRAWLER_CLASSES = {
    Three,
    How
}

# 라우터 등록
app.include_router(api.router)

@app.get("/")
def root():
    return {"message": "FastAPI is running!"}

def init_db():
    output_dir = "./data"
    db = MongoDB()  # ✅ 명시적으로 MongoDB 객체 생성
    try:
        for crawler in CRAWLER_CLASSES:
            crawler.scrape_reviews()
            logging.info(crawler.data)
            crawler.send_to_db(crawler.data, db)  # ✅ MongoDB 객체 전달
    finally:
        db.close()  # ✅ MongoDB 연결 종료

def init_update():
    db = MongoDB()  # ✅ MongoDB 객체 직접 생성
    try:
        while True:
            update_func(db)  # ✅ MongoDB 객체 전달
            print("업데이트를 완료하였습니다")
            time.sleep(5000)
    finally:
        db.close()  # ✅ MongoDB 연결 종료

def background_tasks():
    # ✅ 크롤링 및 DB 저장이 완료될 때까지 기다림
    # db_thread = threading.Thread(target=init_db)
    # db_thread.start()
    # db_thread.join()  # ✅ init_db()가 완료될 때까지 대기

    # ✅ init_db()가 완료된 후 업데이트 실행
    threading.Thread(target=init_update, daemon=True).start()

✅ FastAPI가 실행될 때 background_tasks() 실행
@app.on_event("startup")
def on_startup():
    background_tasks()


if __name__ == "__main__":
    # ✅ 백그라운드에서 실행
    threading.Thread(target=background_tasks, daemon=True).start()
    uvicorn.run("app.main:app", host="0.0.0.0", port=PORT, reload=True)