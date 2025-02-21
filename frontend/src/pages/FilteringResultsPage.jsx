import React from "react";
import { useLocation } from "react-router-dom";
import { AppBar } from "../components/AppBar";
import "./FilteringResultsPage.css";

export const FilteringResultsPage = () => {
  const location = useLocation(); // ✅ 이전 페이지에서 전달된 데이터 받기
  const { price, location: selectedLocation, ratings } = location.state || {}; // 기본값 설정

  console.log("필터링된 값:", { price, selectedLocation, ratings });

  return (
    <div className="filtering-results-page">
      <AppBar />
      <main className="results-container">
        <h2>검색 결과</h2>
        <p>위치: {selectedLocation || "모든 지역"}</p>
        <p>최대 가격: {price ? `${price.toLocaleString()}원` : "제한 없음"}</p>
        <p>평점: {ratings && ratings.length > 0 ? ratings.join(", ") : "제한 없음"}</p>

        {/* 실제 필터링된 매물 리스트 추가 예정 */}
        <div className="no-results">
          <p>🔍 해당 조건에 맞는 매물이 없습니다.</p>
        </div>
      </main>
    </div>
  );
};

export default FilteringResultsPage;
