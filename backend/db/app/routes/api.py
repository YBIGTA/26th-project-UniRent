from fastapi import FastAPI, APIRouter, Depends, Query
from database.mongodb_connection import MongoDB
from typing import Optional, Dict, List
from app.dependencies import get_mongodb
import json
import os

router = APIRouter(prefix="/api")

@router.get("/properties")
async def get_properties(
    region: Optional[str] = Query(None, description="지역 (동 이름)"),
    minPrice: Optional[int] = Query(None, description="최소 가격"),
    maxPrice: Optional[int] = Query(None, description="최대 가격"),
    type: Optional[str] = Query(None, description="모텔/단기임대"),
    db: MongoDB = Depends(get_mongodb)
):
    """매물 목록 조회 (필터링 포함)"""
    filters = {}
    if type:
        filters["type"] = type
    if region:
        filters["region"] = region  # 동(洞) 단위 필터링 적용
    if minPrice is not None and maxPrice is not None:
        filters["price"] = {"$gte": minPrice, "$lte": maxPrice}  # 가격 필터 적용

    properties = db.filter_properties(filters)

    return {"properties": properties}

@router.get("/properties/{property_id}")
async def get_property_by_id(property_id: str, db: MongoDB = Depends(get_mongodb)):
    """특정 매물 상세 조회"""
    property_data = db.get_property_by_id(property_id)
    if property_data:
        return property_data
    return {"message": "해당 매물을 찾을 수 없습니다."}

@router.put("/properties/{property_id}")
async def update_property(property_id: str, update_data: Dict, db: MongoDB = Depends(get_mongodb)):
    """특정 매물 정보 수정"""
    success = db.update_property(property_id, update_data)
    if success:
        return {"message": "매물 정보가 수정되었습니다."}

    return {"message": "해당 매물을 찾을 수 없습니다."}

@router.delete("/properties/{property_id}")
async def delete_property(property_id: str, db: MongoDB = Depends(get_mongodb)):
    """특정 매물 삭제"""
    success = db.delete_property(property_id)
    if success:
        return {"message": "매물이 삭제되었습니다."}

    return {"message": "해당 매물을 찾을 수 없습니다."}

