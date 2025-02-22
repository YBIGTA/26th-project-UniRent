from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os

# 라우터 추가
from app.routes import api

# 환경 변수에서 포트 가져오기 (기본값 8000)
PORT = int(os.getenv("PORT", 8000))

app = FastAPI()

# CORS 설정 추가
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 모든 도메인에서 API 호출 가능 (보안 필요시 특정 도메인만 허용)
    allow_credentials=True,
    allow_methods=["*"],  # 모든 HTTP 메서드 허용 (GET, POST, PUT, DELETE 등)
    allow_headers=["*"],  # 모든 헤더 허용
)

# 라우터 등록
app.include_router(api.router)

@app.get("/")
def root():
    return {"message": "FastAPI is running!"}

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=PORT, reload=True)
