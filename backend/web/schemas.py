from pydantic import BaseModel, EmailStr

# 회원가입 요청 스키마
class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str

# 회원가입 성공 응답 스키마
class UserResponse(BaseModel):
    status: int
    success: bool
    message: str
    data: dict

# 로그인 요청 스키마
class UserLogin(BaseModel):
    email: EmailStr
    password: str