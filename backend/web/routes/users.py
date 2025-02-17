from fastapi import APIRouter, HTTPException, Depends, status, Header
from sqlalchemy.orm import Session
from database import get_db
from models import User
from schemas import UserCreate, UserResponse, UserLogin
from auth import create_access_token, get_current_user

router = APIRouter(prefix="/api/users", tags=["Users"])

# 회원가입 API
@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    # print("받은 요청 데이터:", user)
    # 필수 입력값 검증
    if not user.username or not user.email or not user.password:
        raise HTTPException(status_code=400, detail="필수 입력값이 누락되었습니다.")

    # 이메일 중복 확인
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=409, detail="이미 존재하는 이메일입니다.")
    
    # 신규 유저 저장
    new_user = User(username=user.username, email=user.email, password=user.password)
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # 응답 데이터 구성
    return {
        "status": 201,
        "success": True,
        "message": "회원가입이 완료되었습니다.",
        "data": {
            "userId": new_user.id,
            "username": new_user.username,
            "email": new_user.email
        }
    }

# 로그인 API
@router.post("/login", status_code=status.HTTP_200_OK)
def login_user(user: UserLogin, db: Session = Depends(get_db)):
    """ 로그인 API """

    # 필수 입력값 확인
    if not user.email or not user.password:
        raise HTTPException(status_code=400, detail={"status": 400, "error": "이메일 또는 비밀번호가 누락되었습니다."})
    
    # 이메일로 사용자 조회
    db_user = db.query(User).filter(User.email == user.email).first()
    if not db_user:
        raise HTTPException(status_code=401, detail="이메일 또는 비밀번호가 올바르지 않습니다.")

    # 비밀번호 검증
    if db_user.password != user.password:
        raise HTTPException(status_code=401, detail="이메일 또는 비밀번호가 올바르지 않습니다.")

    # SQLAlchemy 객체를 dict로 변환
    user_dict = {"id": db_user.id, "email": db_user.email}

    # JWT 토큰 발급
    token = create_access_token(user_dict)

    return {
        "status": 200,
        "success": True,
        "message": "로그인 성공",
        "data": {
            "userId": db_user.id,
            "username": db_user.username,
            "email": db_user.email,
            "token": token
        }
    }

# 회원 탈퇴 API
@router.delete("/{userId}", status_code=status.HTTP_200_OK)
def delete_user(userId: int, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    """ 회원 탈퇴 API """

    db_user = db.query(User).filter(User.id == userId).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="요청한 유저 정보를 찾을 수 없습니다.")

    # 현재 로그인한 사용자의 ID와 삭제 요청한 ID 비교
    if db_user.id != current_user["id"]:
        raise HTTPException(status_code=403, detail="해당 계정을 삭제할 권한이 없습니다.")

    db.delete(db_user)
    db.commit()

    return {
        "status": 200,
        "success": True,
        "message": "회원 탈퇴가 완료되었습니다."
    }