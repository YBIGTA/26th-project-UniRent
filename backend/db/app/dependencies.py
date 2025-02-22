from fastapi import Depends
from sqlalchemy.orm import Session
from database.mysql_connection import SessionLocal
from database.mongodb_connection import MongoDB
from app.user.user_repository import UserRepository
from app.user.user_service import UserService
from typing import Generator, Tuple


def get_mysql_db() -> Generator[Session, None, None]:
    """MySQL용 DB 세션을 제공하는 FastAPI 의존성 주입 함수"""
    db = SessionLocal()
    try:
        yield db  # 세션을 반환 (commit/rollback은 호출부에서 결정)
    finally:
        db.close()  # 요청이 끝나면 세션을 닫음

def get_mongodb() -> Generator[MongoDB, None, None]:
    """MongoDB 연결을 제공하는 FastAPI 의존성 주입 함수"""
    db = MongoDB()
    try:
        yield db
    finally:
        db.close()

def get_databases() -> Generator[Tuple[Session, MongoDB], None, None]:
    """MySQL과 MongoDB를 함께 주입"""
    mysql_db = SessionLocal()
    mongodb = MongoDB()
    try:
        yield mysql_db, mongodb  # 두 개의 데이터베이스 객체를 반환
    finally:
        mysql_db.close()
        mongodb.close()


