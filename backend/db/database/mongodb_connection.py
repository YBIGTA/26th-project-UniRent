import os
import re
from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.collection import Collection
from typing import Optional, Dict, List
from bson import ObjectId

# 환경 변수 로드
load_dotenv()
mongo_url = os.getenv("MONGO_URL")

mongo_client = MongoClient(mongo_url)
db_name = "properties"


class MongoDB:
    def __init__(self, uri: str = mongo_url, db_name: str = db_name):
        """MongoDB 연결 설정"""
        self.client = MongoClient(uri)
        self.db = self.client[db_name]
        self.properties: Collection = self.db["properties"]  # 매물 컬렉션

    def add_property(self, property_data: Dict) -> str:
        """매물 추가 (필터링을 위한 필드 자동 추가)"""
        property_data["property_id"] = str(ObjectId())  # ObjectId 기반 고유 ID 생성

        # 1️⃣ 'region' 필드 자동 추가 (addr에서 동(洞) 추출)
        property_data["region"] = self.extract_region(property_data.get("addr", ""))

        # 2️⃣ 'price' 필드 추가 (정수 변환)
        property_data["price"] = self.convert_price(property_data.get("rent_fee", ""))

        result = self.properties.insert_one(property_data)
        return property_data["property_id"]

    def get_all_properties(self) -> List[Dict]:
        """전체 매물 조회"""
        return list(self.properties.find({}, {"_id": 0}))  # _id 제외하고 반환

    def get_property_by_id(self, property_id: str) -> Optional[Dict]:
        """특정 매물 상세 조회"""
        return self.properties.find_one({"property_id": property_id}, {"_id": 0})

    def delete_property(self, property_id: str) -> bool:
        """특정 매물 삭제"""
        result = self.properties.delete_one({"property_id": property_id})
        return result.deleted_count > 0

    def update_property(self, property_id: str, update_data: Dict) -> bool:
        """매물 정보 업데이트"""
        result = self.properties.update_one({"property_id": property_id}, {"$set": update_data})
        return result.modified_count > 0

    def filter_properties(self, filters: Dict) -> List[Dict]:
        """필터링된 매물 조회"""
        query = {}

        if "region" in filters:
            query["region"] = filters["region"]
        if "minPrice" in filters and "maxPrice" in filters:
            query["price"] = {"$gte": filters["minPrice"], "$lte": filters["maxPrice"]}

        return list(self.properties.find(query, {"_id": 0}))

    def close(self):
        """MongoDB 연결 종료"""
        self.client.close()

    ### 🔹 Helper Functions (자동 필드 추가) ###

    def extract_region(self, addr: str) -> str:
        """주소에서 '동' 단위를 추출하여 region 필드 자동 추가"""
        match = re.search(r'([가-힣]+동)', addr)
        return match.group(1) if match else "알 수 없음"

    def convert_price(self, price_str: str) -> int:
        """'50,000원' 형식의 문자열을 정수(int)로 변환"""
        price_str = re.sub(r"[^\d]", "", price_str)  # 숫자 이외 문자 제거
        return int(price_str) if price_str else 0
