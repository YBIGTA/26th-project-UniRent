import React, { useState, useEffect } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import axios from "axios";
import { AppBar } from "../components/AppBar";
import "./FilteringResultsPage.css";

const API_BASE_URL = "http://13.125.103.24:8000";

export const FilteringResultsPage = () => {
  const location = useLocation();
  const navigate = useNavigate();

  // 필터링된 매물 목록 (초기값: 빈 배열)
  const [listings, setListings] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // FilteringPage에서 넘어온 필터 조건
  const filters = location.state?.filters || {};

  useEffect(() => {
    // 필터가 없으면 메인 페이지로 리디렉트
    if (!filters) {
      navigate("/");
      return;
    }

    // API에서 필터링된 결과 가져오기
    const fetchListings = async () => {
      setLoading(true);
      setError(null);

      try {
        const response = await axios.get(`${API_BASE_URL}/api/properties`, { params: filters });

        if (response.data.properties) {
          setListings(response.data.properties);
        } else {
          setListings([]);
        }
      } catch (err) {
        console.error("검색 결과 불러오기 실패:", err);
        setError("검색 결과를 불러오지 못했습니다.");
      } finally {
        setLoading(false);
      }
    };

    fetchListings();
  }, [filters, navigate]);

  return (
    <div className="filtering-results-page">
      <AppBar />
      <main className="results-container">
        <h2>검색 결과</h2>

        {loading ? (
          <p className="loading">검색 중...</p>
        ) : error ? (
          <p className="error">{error}</p>
        ) : listings.length > 0 ? (
          <div className="results-grid">
            {listings.map((listing) => (
              <div
                key={listing._id}
                className="property-card"
                onClick={() => navigate(`/details/${listing._id}`)}
              >
                <img
                  src={listing.image || "https://via.placeholder.com/150"}
                  alt={listing.name}
                  className="property-image"
                />
                <div className="property-info">
                  <h3 className="property-name">{listing.name}</h3>
                  <p className="property-price">
                    {Number(listing.price || 0).toLocaleString()}원
                  </p>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <p className="no-results">검색 결과가 없습니다.</p>
        )}
      </main>
    </div>
  );
};

export default FilteringResultsPage;
