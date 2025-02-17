from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from routes import users
from routes.gateway_routes import gateway_router
from database import get_db
from sqlalchemy import text

app = FastAPI(title="UniRent API Gateway")

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