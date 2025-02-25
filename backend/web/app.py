from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from routes import users
from routes.gateway_routes import gateway_router
from database import get_db
from sqlalchemy import text
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="UniRent API Gateway")

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
    "https://d2t3yinxhatolt.cloudfront.net",
    "https://3.34.99.86:5000",
    "http://3.34.99.86:5000",
    "http://localhost:5173",
    "https://localhost:5173",
    "http://3.34.99.86:5173"
],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 라우터 등록
app.include_router(users.router)
app.include_router(gateway_router, prefix="/gateway")

# DB 연결 확인 API
@app.get("/db-test")
def test_db(db: Session = Depends(get_db)):
    try:
        result = db.execute(text("SELECT NOW()")).fetchone()
        return {"db_connection": "successful", "current_time": result[0]}
    except Exception as e:
        return {"db_connection": "failed", "error": str(e)}

# 홈 API
@app.get("/")
def home():
    return {"message": "Welcome to UniRent API - API Gateway Running with FastAPI!"}