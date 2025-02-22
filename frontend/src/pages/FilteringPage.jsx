import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Button } from "../components/Button";
import { AppBar } from "../components/AppBar";
import { Range } from "react-range"; 
import "./FilteringPage.css";

export const FilteringPage = () => {
  const navigate = useNavigate();
  const [priceRange, setPriceRange] = useState([0, 1000000]); // ✅ 최소 0원, 최대 100만원
  const [region, setRegion] = useState("창천동");
  const [type, setType] = useState(["원룸단기임대", "호텔(모텔)"]); // ✅ 기본값: 두 개 다 선택

  const regions = ["창천동", "연희동", "홍제동", "북아현동", "남가좌동", "북가좌동", "신촌동"];

  const handleApplyFilters = () => {
    console.log("필터 적용:", { minPrice: priceRange[0], maxPrice: priceRange[1], region, type });

    navigate("/filtering-results", {
      state: { minPrice: priceRange[0], maxPrice: priceRange[1], region, type },
    });
  };

  const handleTypeChange = (value) => {
    setType((prevTypes) =>
      prevTypes.includes(value) ? prevTypes.filter((t) => t !== value) : [...prevTypes, value]
    );
  };

  return (
    <div className="filtering-page">
      <AppBar />
      <main className="filter-container">
        <h2>🔍 필터를 활용해 원하는 조건의 숙소를 찾아보세요!</h2>

        {/* 지역 필터 */}
        <div className="filter-group">
          <label>지역</label>
          <select value={region} onChange={(e) => setRegion(e.target.value)}>
            {regions.map((reg) => (
              <option key={reg} value={reg}>{reg}</option>
            ))}
          </select>
        </div>

        {/* ✅ 가격 필터 (슬라이더) */}
        <div className="filter-group">
          <label>가격 범위: {priceRange[0].toLocaleString()}원 ~ {priceRange[1].toLocaleString()}원</label>
          <div className="slider-container">
            <Range
              step={10000} // ✅ 10,000원 단위 조정
              min={0}
              max={1000000}
              values={priceRange}
              onChange={(values) => setPriceRange(values)}
              renderTrack={({ props, children }) => (
                <div {...props} className="slider-track">
                  {children}
                </div>
              )}
              renderThumb={({ props, index }) => (
                <div {...props} className="slider-thumb">
                  {index === 0 ? "⬅" : "➡"}
                </div>
              )}
            />
          </div>
        </div>

        {/* ✅ 숙박 유형 필터 (기본 체크 상태) */}
        <div className="filter-group">
          <label>숙박 유형</label>
          <div className="checkbox-group">
            {["원룸단기임대", "호텔(모텔)"].map((option) => (
              <label key={option} className="checkbox-label">
                <input
                  type="checkbox"
                  value={option}
                  checked={type.includes(option)} // ✅ 기본적으로 두 개 다 체크된 상태
                  onChange={() => handleTypeChange(option)}
                />
                {option}
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
