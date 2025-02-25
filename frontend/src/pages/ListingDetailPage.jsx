import React, { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import axios from "axios";
import { AppBar } from "../components/AppBar";
import "./ListingDetailPage.css";

const API_BASE_URL = "http://13.125.103.24:8000";

export const ListingDetailPage = () => {
  const { id } = useParams(); // URL 파라미터(매물 ID)
  const navigate = useNavigate();
  const [listing, setListing] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchListingDetail = async () => {
      try {
        // ✅ 실제 API 사용
        const response = await axios.get(`${API_BASE_URL}/api/properties/${id}`);

        // 데이터가 없으면 에러 처리
        if (!response.data || Object.keys(response.data).length === 0) {
          throw new Error("매물 정보를 찾을 수 없습니다.");
        }

        setListing(response.data);
      } catch (err) {
        console.error("매물 정보 불러오기 오류:", err);
        setError("매물 정보를 불러오는 중 오류가 발생했습니다.");
      } finally {
        setLoading(false);
      }
    };

    fetchListingDetail();
  }, [id]);

  if (loading) return <p className="loading">로딩 중...</p>;
  if (error) return <p className="error">{error}</p>;
  if (!listing) return <p className="no-property">해당 매물을 찾을 수 없습니다.</p>;

  return (
    <div className="listing-detail-page">
      <AppBar />
      <main className="listing-detail-container">
        {/* 🔙 뒤로가기 버튼 */}
        <button className="back-button" onClick={() => navigate(-1)}>
          ← 뒤로가기
        </button>

        {/* 이미지 (기본 이미지 적용) */}
        <img
          src={listing.image || "https://via.placeholder.com/300"}
          alt={listing.name || "매물 이미지"}
          className="listing-image"
        />

        {/* 매물 정보 */}
        <h2>{listing.name}</h2>
        <p>{listing.region}</p>

        {/* 💰 가격 정보 (객체) */}
        {listing.price_table && Object.keys(listing.price_table).length > 0 ? (
          <div className="listing-price-table">
            <h3>가격 정보</h3>
            <ul>
              {Object.entries(listing.price_table).map(([roomType, price]) => (
                <li key={roomType}>
                  <strong>{roomType}</strong>: {Number(price).toLocaleString()}원
                </li>
              ))}
            </ul>
          </div>
        ) : (
          <p className="no-price">가격 정보 없음</p>
        )}

        {/* 🛏️ 옵션 (배열) */}
        {listing.options && listing.options.length > 0 ? (
          <div className="listing-options">
            <h3>옵션</h3>
            <ul>
              {listing.options.map((opt, idx) => (
                <li key={idx}>{opt}</li>
              ))}
            </ul>
          </div>
        ) : (
          <p className="no-options">제공되는 옵션이 없습니다.</p>
        )}

        {/* 🔗 원문 링크 */}
        {listing.originalUrl && (
          <div className="original-url">
            <a
              href={listing.originalUrl}
              target="_blank"
              rel="noopener noreferrer"
              className="detail-link"
            >
              원문 링크 바로가기
            </a>
          </div>
        )}
      </main>
    </div>
  );
};

export default ListingDetailPage;
