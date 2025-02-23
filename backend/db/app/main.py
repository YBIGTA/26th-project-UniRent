from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
import time
import threading

# 라우터 추가
from app.routes import api

# 크롤러 추가
from crawler.crawler import ThreeThreeCrawler, HowBoutHereCrawler
from crawler.update import *

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

CRAWLER_CLASSES = {
    ThreeThreeCrawler,
    HowBoutHereCrawler
}

# 라우터 등록
app.include_router(api.router)

@app.get("/")
def root():
    return {"message": "FastAPI is running!"}

def init_db():
    output_dir = "./data"
    for crawler_class in CRAWLER_CLASSES:
        crawler = crawler_class(output_dir)
        crawler.scrape_reviews()
        crawler.send_to_db(crawler_class.name)

def init_update():
    while True:
        update_func()
        print("업데이트를 완료하였습니다")
        time.sleep(5000)

def background_tasks():
    threading.Thread(target=init_db, daemon=True).start()
    threading.Thread(target=init_update, daemon=True).start()

# ✅ FastAPI가 실행될 때 background_tasks() 실행
@app.on_event("startup")
def on_startup():
    background_tasks()


if __name__ == "__main__":
    # ✅ 백그라운드에서 실행
    threading.Thread(target=background_tasks, daemon=True).start()
    uvicorn.run("app.main:app", host="0.0.0.0", port=PORT, reload=True)