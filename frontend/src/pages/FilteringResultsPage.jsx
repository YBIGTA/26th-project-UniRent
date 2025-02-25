import React, { useState, useEffect } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import axios from "axios";
import { AppBar } from "../components/AppBar";
import "./FilteringResultsPage.css";

const API_BASE_URL = "http://13.125.103.24:8000";
const S3_BUCKET_URL = "https://uni-rent-bucket.s3.ap-northeast-2.amazonaws.com";
const defaultImage = "https://via.placeholder.com/300?text=No+Image"; // ✅ 기본 이미지

export const FilteringResultsPage = () => {
  const location = useLocation();
  const navigate = useNavigate();

  const [listings, setListings] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const filters = location.state?.filters || {};

  useEffect(() => {
    console.log("🔹 FilteringResultsPage useEffect 실행됨");
    console.log("🔹 필터 조건:", filters);

    const fetchListings = async () => {
      setLoading(true);
      setError(null);

      try {
        console.log("🔹 API 요청 보냄:", `${API_BASE_URL}/api/properties`);
        console.log("🔹 요청 파라미터:", filters);

        const response = await axios.get(`${API_BASE_URL}/api/properties`, { params: filters });

        console.log("✅ API 응답 받음:", response.data);

        if (!response.data || !response.data.properties) {
          throw new Error("응답 데이터에 properties 키가 없습니다.");
        }

        console.log("🔹 응답 데이터 (매물 개수):", response.data.properties.length);

        const listingsWithImages = response.data.properties.map((listing) => {
          const encodedTitle = encodeURIComponent(listing.title);
          const bucketName = listing.url.includes("yeogi.com") ? "howbouthere" : "threethree";

          // ✅ `.jpg` → `.png` → `.img` 순서로 시도
          return { 
            ...listing, 
            imageUrls: [
              `${S3_BUCKET_URL}/${bucketName}/${encodedTitle}/0.jpg`,
              `${S3_BUCKET_URL}/${bucketName}/${encodedTitle}/0.png`,
              `${S3_BUCKET_URL}/${bucketName}/${encodedTitle}/0.img`
            ]
          };
        });

        setListings(listingsWithImages);
      } catch (err) {
        console.error("❌ API 호출 실패:", err);
        setError("검색 결과를 불러오지 못했습니다.");
      } finally {
        setLoading(false);
      }
    };

    fetchListings();
  }, [filters]);

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
                key={listing.property_id}
                className="property-card"
                onClick={() => navigate(`/details/${listing.property_id}`)}
              >
                {/* ✅ `.jpg` 먼저 로드하고 실패하면 `.png`, 그다음 `.img` 시도 */}
                <img 
                  src={listing.imageUrls[0]} 
                  alt={listing.title} 
                  className="property-image" 
                  onError={(e) => {
                    e.target.onerror = () => {
                      e.target.onerror = () => {
                        e.target.onerror = null;
                        e.target.src = defaultImage; // ✅ 최종 실패 시 기본 이미지 사용
                      };
                      e.target.src = listing.imageUrls[2]; // ✅ `.png`도 실패하면 `.img` 시도
                    };
                    e.target.src = listing.imageUrls[1]; // ✅ `.jpg` 실패 시 `.png` 로드
                  }}
                />

                <div className="property-info">
                  <h3 className="property-name">{listing.title}</h3>
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
