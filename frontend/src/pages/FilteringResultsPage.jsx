import React from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { AppBar } from "../components/AppBar";
import "./FilteringResultsPage.css";

export const FilteringResultsPage = () => {
  const location = useLocation();
  const navigate = useNavigate();

  // FilteringPage에서 넘어온 매물 리스트
  const { listings = [] } = location.state || {};

  return (
    <div className="filtering-results-page">
      <AppBar />
      <main className="results-container">
        <h2>검색 결과</h2>

        {listings.length > 0 ? (
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
