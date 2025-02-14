from fastapi import APIRouter

user_router = APIRouter()

@user_router.get("/profile")
def get_user_profile():
    return {"user": "example", "email": "example@example.com"}