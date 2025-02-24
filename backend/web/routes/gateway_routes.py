from fastapi import APIRouter

gateway_router = APIRouter()

@gateway_router.get("/status")
def gateway_status():
    return {"status": "API Gateway Active"}
