import React, { useState } from "react";
import { useNavigate } from "react-router-dom"; // ✅ 페이지 이동을 위한 useNavigate 추가
import { Button } from "../components/Button";
import { AppBar } from "../components/AppBar";
import "./FilteringPage.css";

export const FilteringPage = () => {
  const navigate = useNavigate(); // ✅ 페이지 이동을 위한 훅
  const [price, setPrice] = useState(0);
  const [region, setRegion] = useState("");
  const [accommodationTypes, setAccommodationTypes] = useState([]); // ✅ 숙박 유형 상태 추가

  const regions = [
    "창천동", "연희동", "홍제동", "북아현동", "남가좌동", "북가좌동", "신촌동"
  ];

  const handleApplyFilters = () => {
    console.log("필터 적용:", { price, region, accommodationTypes });

    // ✅ 필터링된 결과가 없어도 결과 페이지로 이동하게 설정
    navigate("/filtering-results", { state: { price, region, accommodationTypes } });
  };

  // ✅ 숙박 유형 체크박스 선택 핸들러
  const handleAccommodationTypeChange = (value) => {
    setAccommodationTypes((prevTypes) =>
      prevTypes.includes(value)
        ? prevTypes.filter((type) => type !== value) // 이미 선택된 값이면 제거
        : [...prevTypes, value] // 선택되지 않은 값이면 추가
    );
  };

  return (
    <div className="filtering-page">
      <AppBar />
      <main className="filter-container">
        <h2>🔍 필터를 활용해 원하는 조건의 숙소를 찾아보세요!</h2>

        {/* 지역 필터 (드롭다운) */}
        <div className="filter-group">
          <label>지역</label>
          <select value={region} onChange={(e) => setRegion(e.target.value)}>
            <option value="">선택하세요</option>
            {regions.map((reg) => (
              <option key={reg} value={reg}>{reg}</option>
            ))}
          </select>
        </div>

        {/* 가격 필터 (슬라이더) */}
        <div className="filter-group">
          <label>최대 가격: {price.toLocaleString()}원 (일 당)</label>
          <input
            type="range"
            min="0"
            max="500000"
            step="5000"
            value={price}
            onChange={(e) => setPrice(Number(e.target.value))}
            className="slider"
          />
        </div>

        {/* ✅ 숙박 유형 필터 (체크박스) */}
        <div className="filter-group">
          <label>숙박 유형</label>
          <div className="checkbox-group">
            {["원룸단기임대", "호텔(모텔)"].map((type) => (
              <label key={type} className="checkbox-label">
                <input
                  type="checkbox"
                  value={type}
                  checked={accommodationTypes.includes(type)}
                  onChange={() => handleAccommodationTypeChange(type)}
                />
                {type}
              </label>
            ))}
          </div>
        </div>

        {/* 필터 적용 버튼 */}
        <Button className="apply-button" onClick={handleApplyFilters}>
          검색
        </Button>
      </main>
    </div>
  );
};

export default FilteringPage;
