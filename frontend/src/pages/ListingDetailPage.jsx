import React, { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import axios from "axios";
import { AppBar } from "../components/AppBar";
import "./ListingDetailPage.css";

export const ListingDetailPage = () => {
  const { id } = useParams(); // URL 파라미터(매물 ID)를 받는다고 가정
  const navigate = useNavigate();
  const [listing, setListing] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchListingDetail = async () => {
      try {
        // 실제 API 경로로 변경
        const response = await axios.get(`http://localhost:8000/api/properties/${id}`);
        setListing(response.data);
      } catch (err) {
        console.error("Error fetching listing details:", err);
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
        {/* 뒤로가기 버튼 */}
        <button className="back-button" onClick={() => navigate(-1)}>
          ← 뒤로가기
        </button>

        {/* DB에서 넘어온 이미지 그대로 사용 (임시 링크 없음) */}
        <img
          src={listing.image}
          alt={listing.title || "매물 이미지"}
          className="listing-image"
        />

        <h2>{listing.title}</h2>
        <p>{listing.addr}</p>

        {/* price_table (객체) => 키-값 쌍을 반복 렌더링 */}
        {listing.price_table && Object.keys(listing.price_table).length > 0 && (
          <div className="listing-price-table">
            <h3>가격 정보</h3>
            <ul>
              {Object.entries(listing.price_table).map(([roomType, price]) => (
                <li key={roomType}>
                  <strong>{roomType}</strong> : {price}원
                </li>
              ))}
            </ul>
          </div>
        )}

        {/* 옵션 (배열) => 목록 렌더링 */}
        {listing.options && listing.options.length > 0 && (
          <div className="listing-options">
            <h3>옵션</h3>
            <ul>
              {listing.options.map((opt, idx) => (
                <li key={idx}>{opt}</li>
              ))}
            </ul>
          </div>
        )}

        {/* 원문 링크도 그대로 표시 (fallback 없음) */}
        <div className="original-url">
          <a
            href={listing.originalUrl}
            target="_blank"
            rel="noopener noreferrer"
            style={{ textDecoration: "underline", color: "blue" }}
          >
            원문 링크 바로가기
          </a>
        </div>
      </main>
    </div>
  );
};

export default ListingDetailPage;
