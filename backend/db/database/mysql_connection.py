from sqlalchemy import create_engine, text, Column, String
from sqlalchemy.orm import sessionmaker, declarative_base
import os       
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

# 환경 변수에서 MySQL 접속 정보 가져오기
user = os.getenv("DB_USER")
passwd = os.getenv("DB_PASSWD")
host = os.getenv("DB_HOST")
port = os.getenv("DB_PORT")
db = os.getenv("DB_NAME")

# MySQL 연결 URL
DB_URL = f'mysql+pymysql://{user}:{passwd}@{host}:{port}/{db}?charset=utf8'

# SQLAlchemy 엔진 및 세션 설정
engine = create_engine(DB_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 데이터베이스 모델 정의
Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    email = Column(String(255), primary_key=True)
    password = Column(String(255), nullable=False)
    username = Column(String(255), nullable=False)

# 데이터베이스 테이블 생성
def init_db():
    Base.metadata.create_all(bind=engine)

# 스크립트 실행 시 테이블 자동 생성
if __name__ == "__main__":
    init_db()
    print("users 테이블 생성 완료")
