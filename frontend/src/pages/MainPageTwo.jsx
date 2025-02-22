import React from "react";
import { useNavigate } from "react-router-dom";
import { Button } from "../components/Button";
import "./MainPageTwo.css";

export const MainPageTwo = ({ isAuthenticated, setIsAuthenticated }) => {
  const navigate = useNavigate();

  console.log("MainPageTwo 렌더링됨, isAuthenticated:", isAuthenticated); // ✅ 현재 로그인 상태 확인

  // ✅ 로그아웃 핸들러 (MainPage로 이동)
  const handleLogout = () => {
    setIsAuthenticated(false); // 인증 상태 변경
    navigate("/"); // ✅ MainPage로 이동
  };

  // ✅ 필터 버튼 클릭 시 FilteringPage로 이동
  const handleFiltering = () => {
    if (isAuthenticated) {
      console.log("✅ 필터 버튼 클릭됨, FilteringPage로 이동");
      navigate("/filtering");
    } else {
      console.log("🚨 필터 버튼 클릭됨, 하지만 로그인되지 않음");
    }
  };

  return (
    <main className="main-page-two">
      <header className="header">
        <nav className="nav">
          <button className="logout-button" onClick={handleLogout}>
            Logout
          </button>
        </nav>
      </header>

      <section className="content">
        <h1 className="title">UniRent</h1>
        <p className="subtitle">
          🔍 필터를 활용해 원하는 조건의 숙소를 찾아보세요!
        </p>
        <p className="description">
          해당 사이트는 숙박 및 단기 거주 매물을 쉽게 비교할 수 있도록 제작되었습니다.
          <br />
          매물 정보는 삼삼엠투, 야놀자, 여기어때에서 수집되었으며, 지속적으로 업데이트됩니다.
        </p>
      </section>

      <section className="filter-box">
        <p className="filter-text">
          어떤 매물을 찾으시나요? 오른쪽 필터 버튼을 눌러보세요!
        </p>
        {/* ✅ 필터 버튼 클릭 시 FilteringPage로 이동 */}
        <Button className="search-button" color="primary" size="medium" onClick={handleFiltering}>
          필터
        </Button>
      </section>
    </main>
  );
};

export default MainPageTwo;
