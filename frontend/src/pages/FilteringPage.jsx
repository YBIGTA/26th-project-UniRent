import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";
import { Button } from "../components/Button";
import { AppBar } from "../components/AppBar";
import { Range } from "react-range"; 
import "./FilteringPage.css";

const API_BASE_URL = "http://localhost:8000";

export const FilteringPage = () => {
  const navigate = useNavigate();
  const [priceRange, setPriceRange] = useState([0, 1000000]); // 기본 가격 범위
  const [region, setRegion] = useState("창천동"); // 기본 지역
  const [type, setType] = useState(["원룸단기임대", "호텔(모텔)"]); // 기본 체크된 숙박 유형
  const [loading, setLoading] = useState(false); // API 요청 상태

  const regions = ["창천동", "연희동", "홍제동", "북아현동", "남가좌동", "북가좌동", "신촌동"];

  // ✅ 필터 적용 및 API 호출
  const handleApplyFilters = async () => {
    setLoading(true);

    // ✅ FastAPI와 일치하는 쿼리 파라미터 변환
    const params = {
      region,
      minPrice: priceRange[0],
      maxPrice: priceRange[1],
      type: type.length > 0 ? type.join(",") : undefined, // ✅ FastAPI에서는 문자열로 전달
    };

    try {
      const response = await axios.get(`${API_BASE_URL}/properties`, { params });

      if (response.data.properties) {
        navigate("/filtering-results", { state: { listings: response.data.properties } });
      } else {
        alert("검색된 매물이 없습니다.");
      }
    } catch (error) {
      console.error("필터링 데이터 불러오기 실패:", error);
      alert("서버와 통신 중 오류가 발생했습니다.");
    } finally {
      setLoading(false);
    }
  };

  // ✅ 숙박 유형 체크박스 핸들러
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

        {/* ✅ 지역 필터 */}
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

        {/* ✅ 필터 적용 버튼 (API 요청 중 비활성화) */}
        <Button className="apply-button" onClick={handleApplyFilters} disabled={loading}>
          {loading ? "검색 중..." : "검색"}
        </Button>
      </main>
    </div>
  );
};

export default FilteringPage;
