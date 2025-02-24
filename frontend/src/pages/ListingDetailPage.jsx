import React, { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import axios from "axios";
import { AppBar } from "../components/AppBar";
import "./ListingDetailPage.css";


export const ListingDetailPage = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [listing, setListing] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchListingDetail = async () => {
      try {
        // 실제 API 주소로 변경
        const response = await axios.get(`http://localhost:8000/properties/${id}`);
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

  if (loading) {
    return <p className="loading">로딩 중...</p>;
  }

  if (error) {
    return <p className="error">{error}</p>;
  }

  if (!listing) {
    return <p className="no-property">해당 매물을 찾을 수 없습니다.</p>;
  }

  return (
    <div className="listing-detail-page">
      <AppBar />
      <main className="listing-detail-container">
        {/* 뒤로가기 버튼 */}
        <button className="back-button" onClick={() => navigate(-1)}>
          ← 뒤로가기
        </button>

        {/* 이미지 */}
        <img
          src={listing.image || "https://via.placeholder.com/300"}
          alt={listing.title || "매물 이미지"}
          className="listing-image"
        />

        {/* 매물 정보 */}
        <h2>{listing.title || listing.name}</h2>
        <p>
          <strong>위치:</strong> {listing.location || listing.region}
        </p>
        <p>
          <strong>가격:</strong> {Number(listing.price || 0).toLocaleString()}원
        </p>
        {/* 평점이나 추가 필드가 있을 경우 */}
        {listing.rating && (
          <p>
            <strong>평점:</strong> {listing.rating} / 5
          </p>
        )}
        {listing.description && (
          <p>
            <strong>설명:</strong> {listing.description}
          </p>
        )}

        {/* 예약하기 등 추가 버튼 */}
        <button className="reserve-button">예약하기</button>
      </main>
    </div>
  );
};

export default ListingDetailPage;
