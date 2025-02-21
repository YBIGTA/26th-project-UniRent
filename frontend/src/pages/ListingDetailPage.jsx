import React, { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { AppBar } from "../components/AppBar";
import "./ListingDetailPage.css";

export const ListingDetailPage = () => {
  const { id } = useParams();
  const [listing, setListing] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    const fetchListingDetail = async () => {
      try {
        const response = await fetch(`http://your-api-url.com/listings/${id}`); // 실제 API 주소로 변경
        const data = await response.json();
        setListing(data);
      } catch (error) {
        console.error("Error fetching listing details:", error);
      }
    };

    fetchListingDetail();
  }, [id]);

  if (!listing) {
    return <p>매물 정보를 불러오는 중...</p>;
  }

  return (
    <div className="listing-detail-page">
      <AppBar />
      <main className="listing-detail-container">
        <button className="back-button" onClick={() => navigate(-1)}>← 뒤로가기</button>
        
        <img src={listing.image} alt={listing.title} className="listing-image" />
        <h2>{listing.title}</h2>
        <p><strong>위치:</strong> {listing.location}</p>
        <p><strong>가격:</strong> {listing.price.toLocaleString()}원</p>
        <p><strong>평점:</strong> {listing.rating} / 5</p>
        <p><strong>설명:</strong> {listing.description}</p>

        <button className="reserve-button">예약하기</button>
      </main>
    </div>
  );
};

export default ListingDetailPage;




