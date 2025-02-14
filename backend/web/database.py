import pymysql
import os
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

# 환경 변수에서 MySQL 연결 정보 가져오기
DB_HOST = os.getenv("DB_HOST")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")
DB_PORT = int(os.getenv("DB_PORT", 3306))  # 기본값 3306 설정

# MySQL 연결 함수
def get_connection():
    try:
        connection = pymysql.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME,
            port=DB_PORT,
            cursorclass=pymysql.cursors.DictCursor  # 결과를 딕셔너리 형태로 반환
        )
        print("✅ MySQL 연결 성공!")
        return connection
    except Exception as e:
        print(f"❌ MySQL 연결 실패: {e}")
        return None
