import React, { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import axios from "axios";
import { AppBar } from "../components/AppBar";
import "./ListingDetailPage.css";

const API_BASE_URL = "http://13.125.103.24:8000";
const S3_BUCKET_URL = "https://uni-rent-bucket.s3.ap-northeast-2.amazonaws.com";
const MAX_IMAGE_COUNT = 10; // ✅ 최대 10장
const possibleExtensions = [".jpg", ".png", ".img"]; // ✅ 여러 확장자 지원

export const ListingDetailPage = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [listing, setListing] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [imageUrls, setImageUrls] = useState([]); // ✅ 존재하는 이미지 리스트

  useEffect(() => {
    const fetchListingDetail = async () => {
      try {
        console.log(`🔹 매물 상세 정보 요청: ${API_BASE_URL}/api/properties/${id}`);
        const response = await axios.get(`${API_BASE_URL}/api/properties/${id}`);

        console.log("✅ API 응답 데이터:", response.data);

        if (!response.data || Object.keys(response.data).length === 0) {
          throw new Error("매물 정보를 찾을 수 없습니다.");
        }

        const listingData = response.data;
        setListing(listingData);

        // ✅ 이미지 URL 리스트 생성 (여기어때는 howbouthere, 삼삼엠투는 threethree)
        const encodedTitle = encodeURIComponent(listingData.title);
        const bucketName = listingData.url.includes("yeogi.com") ? "howbouthere" : "threethree";

        const generatedImageUrls = [];
        for (let i = 0; i < MAX_IMAGE_COUNT; i++) {
          possibleExtensions.forEach((ext) => {
            generatedImageUrls.push(`${S3_BUCKET_URL}/${bucketName}/${encodedTitle}/${i}${ext}`);
          });
        }

        setImageUrls(generatedImageUrls);
      } catch (err) {
        console.error("❌ 매물 정보 불러오기 오류:", err);
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
        <button className="back-button" onClick={() => navigate(-1)}>← 뒤로가기</button>

        {/* ✅ 여러 확장자를 시도하며 10장까지 이미지 표시 */}
        {imageUrls.length > 0 && (
          <div className="listing-images">
            {imageUrls.map((url, idx) => (
              <img 
                key={idx} 
                src={url} 
                alt={`매물 이미지 ${idx + 1}`} 
                className="listing-image"
                onError={(e) => e.target.style.display = "none"} // ✅ 이미지 로드 실패 시 숨김
              />
            ))}
          </div>
        )}

        {/* ✅ 매물 정보 */}
        <h2>{listing.title}</h2>
        <p>📍 {listing.addr}</p>

        {/* ✅ 원문 링크 */}
        {listing.url && (
          <div className="original-url">
            <a href={listing.url} target="_blank" rel="noopener noreferrer" className="detail-link">
              🔗 원문 링크 바로가기
            </a>
          </div>
        )}

        {/* ✅ 가격 정보 */}
        <div className="listing-price">
          <h3>💰 가격</h3>
          <p>{Number(listing.price || 0).toLocaleString()}원</p>
        </div>
      </main>
    </div>
  );
};

export default ListingDetailPage;
