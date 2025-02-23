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

    def delete_properties_by_titles(self, titles: List[str]) -> int:
        """titles 리스트에 포함된 모든 매물을 삭제"""
        result = self.properties.delete_many({"title": {"$in": titles}})
        return result.deleted_count  # 삭제된 문서 개수 반환


    def add_property(self, property_data: Dict, name: str) -> str:
        """매물 추가 (필터링을 위한 필드 자동 추가)"""
        property_data["property_id"] = str(ObjectId())  # ObjectId 기반 고유 ID 생성

        # 1️⃣ 'region' 필드 자동 추가 (addr에서 동(洞) 추출)
        property_data["region"] = self.extract_region(property_data.get("addr", ""))

        # 2️⃣ 'price' 필드 추가 (정수 변환)
        property_data["price"] = self.convert_price(property_data.get("rent_fee", ""))

        # 3️⃣ 'type' 필드 추가 (name 값 저장)
        property_data["type"] = name

        result = self.properties.insert_one(property_data)
        return property_data["property_id"]

    
    def get_all_titles(self) -> List[str]:
        """전체 매물의 title 필드만 리스트로 반환"""
        titles = self.properties.find({}, {"_id": 0, "title": 1})  # title 필드만 가져오기
        return [doc["title"] for doc in titles if "title" in doc]  # 리스트로 변환

    def get_titles_by_type(self, property_type: str) -> List[str]:
        """특정 type을 가진 매물의 title 필드만 리스트로 반환"""
        titles = self.properties.find({"type": property_type}, {"_id": 0, "title": 1})  # type 필터 적용
        return [doc["title"] for doc in titles if "title" in doc]  # title 리스트 반환


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

        # 1️⃣ 'region' 필터 적용
        if "region" in filters:
            query["region"] = filters["region"]

        # 2️⃣ 'price' 필터 적용 (최소 가격 ~ 최대 가격)
        if "minPrice" in filters:
            query.setdefault("price", {})["$gte"] = filters["minPrice"]
        if "maxPrice" in filters:
            query.setdefault("price", {})["$lte"] = filters["maxPrice"]

        # 3️⃣ 'type' 필터 적용
        if "type" in filters:
            query["type"] = filters["type"]

        # 4️⃣ MongoDB에서 필터링된 결과 조회 (_id 제외)
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
