from fastapi import FastAPI, APIRouter, Depends, Query
from database.mongodb_connection import MongoDB
from typing import Optional, Dict, List
import json
import os

router = APIRouter()

@router.post("/properties")
async def add_property(property_data: Dict, db: MongoDB = Depends()):
    """MongoDB에 매물 추가 (자동 필드 추가)"""
    property_id = db.add_property(property_data)
    return {"message": "매물이 추가되었습니다.", "property_id": property_id}

@router.get("/properties")
async def get_properties(
    region: Optional[str] = Query(None, description="지역 (동 이름)"),
    minPrice: Optional[int] = Query(None, description="최소 가격"),
    maxPrice: Optional[int] = Query(None, description="최대 가격"),
    db: MongoDB = Depends()
):
    """매물 목록 조회 (필터링 포함)"""
    filters = {}
    if region:
        filters["region"] = region  # 동(洞) 단위 필터링 적용
    if minPrice is not None and maxPrice is not None:
        filters["price"] = {"$gte": minPrice, "$lte": maxPrice}  # 가격 필터 적용

    properties = db.filter_properties(filters)
    return {"properties": properties}

@router.get("/properties/{property_id}")
async def get_property_by_id(property_id: str, db: MongoDB = Depends()):
    """특정 매물 상세 조회"""
    property_data = db.get_property_by_id(property_id)
    if property_data:
        return property_data
    return {"message": "해당 매물을 찾을 수 없습니다."}

@router.put("/properties/{property_id}")
async def update_property(property_id: str, update_data: Dict, db: MongoDB = Depends()):
    """특정 매물 정보 수정"""
    success = db.update_property(property_id, update_data)
    if success:
        return {"message": "매물 정보가 수정되었습니다."}
    return {"message": "해당 매물을 찾을 수 없습니다."}

@router.delete("/properties/{property_id}")
async def delete_property(property_id: str, db: MongoDB = Depends()):
    """특정 매물 삭제"""
    success = db.delete_property(property_id)
    if success:
        return {"message": "매물이 삭제되었습니다."}
    return {"message": "해당 매물을 찾을 수 없습니다."}

@router.post("/scraped-data/import")
async def import_scraped_data(db: MongoDB = Depends()):
    """크롤링된 JSON 데이터를 MongoDB에 저장 (자동 필드 추가)"""
    scraped_data_path = "scraped_properties.json"

    if not os.path.exists(scraped_data_path):
        return {"message": "크롤링된 데이터 파일이 존재하지 않습니다."}

    with open(scraped_data_path, "r", encoding="utf-8") as f:
        properties = json.load(f)

    inserted_ids = []
    for property_data in properties:
        # MongoDB에 저장 시, 자동으로 region (동)과 price (숫자) 변환 적용
        property_id = db.add_property(property_data)
        inserted_ids.append(property_id)

    return {"message": "크롤링된 데이터가 DB에 저장되었습니다.", "inserted_ids": inserted_ids}
