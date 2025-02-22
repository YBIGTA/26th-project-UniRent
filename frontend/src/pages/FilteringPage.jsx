import React, { useState } from "react";
import { useNavigate } from "react-router-dom"; // ✅ 페이지 이동을 위한 useNavigate 추가
import { Button } from "../components/Button";
import { AppBar } from "../components/AppBar";
import "./FilteringPage.css";

export const FilteringPage = () => {
  const navigate = useNavigate(); // ✅ 페이지 이동을 위한 훅
  const [price, setPrice] = useState(0);
  const [location, setLocation] = useState("");
  const [ratings, setRatings] = useState([]); // ✅ 평점 다중 선택

  const locations = [
    "창천동", "연희동", "홍제동", "북아현동", "남가좌동", "북가좌동", "신촌동"
  ];

  const handleApplyFilters = () => {
    console.log("필터 적용:", { price, location, ratings });

    // ✅ 필터링된 결과가 없어도 결과 페이지로 이동하게 설정
    navigate("/filtering-results", { state: { price, location, ratings } });
  };

  const handleRatingChange = (value) => {
    setRatings((prevRatings) =>
      prevRatings.includes(value)
        ? prevRatings.filter((rating) => rating !== value) // 이미 선택된 값이면 제거
        : [...prevRatings, value] // 선택되지 않은 값이면 추가
    );
  };

  return (
    <div className="filtering-page">
      <AppBar />
      <main className="filter-container">
        <h2>필터를 활용해 원하는 조건의 숙소를 찾아보세요!</h2>

        {/* 위치 필터 (드롭다운) */}
        <div className="filter-group">
          <label>위치</label>
          <select value={location} onChange={(e) => setLocation(e.target.value)}>
            <option value="">선택하세요</option>
            {locations.map((loc) => (
              <option key={loc} value={loc}>{loc}</option>
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

        {/* 평점 필터 (다중 선택 체크박스) */}
        <div className="filter-group">
          <label>평점</label>
          <div className="checkbox-group">
            {[0, 1, 2, 3, 4].map((num) => (
              <label key={num} className="checkbox-label">
                <input
                  type="checkbox"
                  value={num}
                  checked={ratings.includes(num)}
                  onChange={() => handleRatingChange(num)}
                />
                {num}-{num + 1}점
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
