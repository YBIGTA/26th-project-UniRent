import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";
import { Button } from "../components/Button";
import { AppBar } from "../components/AppBar";
import { Range } from "react-range"; 
import "./FilteringPage.css";

const API_BASE_URL = "http://13.125.103.24:8000"; // ✅ 실제 API 서버 URL 사용

export const FilteringPage = () => {
  const navigate = useNavigate();

  // 가격 필터
  const [priceRange, setPriceRange] = useState([0, 1000000]);

  // 지역 필터 (초기값 선택 안 함)
  const [region, setRegion] = useState("");

  // 숙박 유형 필터 (초기값 선택 안 함)
  const [type, setType] = useState([]);

  // 로딩 상태
  const [loading, setLoading] = useState(false);

  // 지역 목록
  const regions = ["", "창천동", "연희동", "홍제동", "북아현동", "남가좌동", "북가좌동", "신촌동"];

  // 숙박 유형 필터 (UI 표시용)
  const typeOptions = [
    { apiValue: "단기임대", displayValue: "원룸단기임대" },
    { apiValue: "모텔", displayValue: "모텔/호텔" }
  ];

  // ✅ 필터 적용 및 API 호출
  const handleApplyFilters = async () => {
    setLoading(true);

    // FastAPI 요청 파라미터
    const params = {
      ...(region && { region }), // ✅ 선택한 경우에만 추가
      minPrice: priceRange[0],
      maxPrice: priceRange[1],
      ...(type.length > 0 && { type }) // ✅ 빈 배열이면 추가하지 않음
    };

    try {
      const response = await axios.get(`${API_BASE_URL}/api/properties`, { params });

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
  const handleTypeChange = (apiValue) => {
    setType((prevTypes) =>
      prevTypes.includes(apiValue)
        ? prevTypes.filter((t) => t !== apiValue) // 체크 해제 시 제거
        : [...prevTypes, apiValue] // 체크 시 추가
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
              <option key={reg} value={reg}>{reg || "전체 지역"}</option>
            ))}
          </select>
        </div>

        {/* ✅ 가격 필터 (슬라이더) */}
        <div className="filter-group">
          <label>가격 범위: {priceRange[0].toLocaleString()}원 ~ {priceRange[1].toLocaleString()}원</label>
          <div className="slider-container">
            <Range
              step={10000}
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

        {/* ✅ 숙박 유형 필터 (체크박스) */}
        <div className="filter-group">
          <label>숙박 유형</label>
          <div className="checkbox-group">
            {typeOptions.map(({ apiValue, displayValue }) => (
              <label key={apiValue} className="checkbox-label">
                <input
                  type="checkbox"
                  value={apiValue}
                  checked={type.includes(apiValue)}
                  onChange={() => handleTypeChange(apiValue)}
                />
                {displayValue}
              </label>
            ))}
          </div>
        </div>

        {/* ✅ 필터 적용 버튼 */}
        <Button className="apply-button" onClick={handleApplyFilters} disabled={loading}>
          {loading ? "검색 중..." : "검색"}
        </Button>
      </main>
    </div>
  );
};

export default FilteringPage;

