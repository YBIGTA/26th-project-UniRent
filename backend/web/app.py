from fastapi import FastAPI
from routes.user_routes import user_router
from routes.gateway_routes import gateway_router
from database import get_connection

app = FastAPI(title="UniRent API Gateway")

# API Gateway & User Service 라우트 등록
app.include_router(user_router, prefix="/users")
app.include_router(gateway_router, prefix="/gateway")

@app.get("/db-test")
def test_db():
    try:
        conn = get_connection()
        if conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT NOW() AS current_time")
                result = cursor.fetchone()
            conn.close()
            return {"db_connection": "successful", "current_time": result["current_time"]}
        else:
            return {"db_connection": "failed", "error": "Could not connect to database"}
    except Exception as e:
        return {"error": str(e)}

@app.get("/")
def home():
    return {"message": "API Gateway & User Service Running with FastAPI!"}
