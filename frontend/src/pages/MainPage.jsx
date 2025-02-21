import React from "react";
import { Link } from "react-router-dom";
import "./MainPage.css";
import { Button } from "../components/Button";

export const MainPage = ({ isAuthenticated }) => {
  return (
    <main className="main-page">
      <header className="header">
        <nav className="nav">
          {isAuthenticated ? (
            <p>로그인됨</p>
          ) : (
            <>
              <Link to="/login" className="nav-link">Login</Link>
              <Link to="/signup" className="nav-link">Sign up</Link>
            </>
          )}
        </nav>
      </header>

      <section className="content">
        <h1 className="title">UniRent</h1>
        <p className="subtitle">
          🔍 필터를 활용해 원하는 숙소를 찾아보세요!
        </p>
        <p className="description">
          해당 사이트는 숙박 및 단기 거주 매물을 쉽게 비교할 수 있도록
          제작되었습니다.
          <br />
          매물 정보는 삼삼엠투, 야놀자, 여기어때에서 수집되었으며, 지속적으로
          업데이트됩니다.
        </p>
      </section>

      <section className="filter-box">
        <p className="filter-text">
          어떤 매물을 찾으시나요? 오른쪽 필터 버튼을 눌러보세요!
        </p>
        <Link to="/filtering">
          <Button className="search-button" color="primary" size="medium">
            필터
          </Button>
        </Link>
      </section>
    </main>
  );
};

export default MainPage;
