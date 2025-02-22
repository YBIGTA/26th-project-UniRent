import React from "react";
import { useNavigate } from "react-router-dom";
import { motion } from "framer-motion";  // ✅ Framer Motion 추가
import { Button } from "../components/Button";
import "./MainPageTwo.css";

export const MainPageTwo = ({ isAuthenticated, setIsAuthenticated }) => {
  const navigate = useNavigate();

  console.log("MainPageTwo 렌더링됨, isAuthenticated:", isAuthenticated);

  // ✅ 로그아웃 핸들러 (MainPage로 이동)
  const handleLogout = () => {
    setIsAuthenticated(false);
    navigate("/");
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
    <motion.main 
      className="main-page-two"
      initial={{ opacity: 0, y: 30 }}  // ✅ 페이지 로드 시 애니메이션 (페이드 인 + 위에서 아래로)
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6, ease: "easeOut" }}
    >
      <header className="header">
        <nav className="nav">
          <motion.button 
            className="logout-button" 
            onClick={handleLogout}
            whileHover={{ scale: 1.1 }}  // ✅ 버튼에 호버 효과
            whileTap={{ scale: 0.95 }}  
          >
            Logout
          </motion.button>
        </nav>
      </header>

      <section className="content">
        <motion.h1 
          className="title"
          initial={{ opacity: 0, scale: 0.8 }}  // ✅ 타이틀 애니메이션 (페이드 인 + 스케일 업)
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.5, delay: 0.2 }}
        >
          UniRent
        </motion.h1>
        
        <motion.p 
          className="subtitle"
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.3 }}
        >
          🔍 필터를 활용해 원하는 조건의 숙소를 찾아보세요!
        </motion.p>

        <motion.p 
          className="description"
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.4 }}
        >
          해당 사이트는 숙박 및 단기 거주 매물을 쉽게 비교할 수 있도록 제작되었습니다.
          <br />
          매물 정보는 삼삼엠투, 야놀자, 여기어때에서 수집되었으며, 지속적으로 업데이트됩니다.
        </motion.p>
      </section>

      <motion.section 
        className="filter-box"
        initial={{ opacity: 0, scale: 0.9 }}  // ✅ 필터 버튼 영역 애니메이션 (페이드 인 + 스케일 업)
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.5, delay: 0.5 }}
      >
        <p className="filter-text">
          어떤 매물을 찾으시나요? 오른쪽 필터 버튼을 눌러보세요!
        </p>

        <motion.div 
          whileHover={{ scale: 1.1 }}  // ✅ 버튼 호버 효과 추가
          whileTap={{ scale: 0.95 }}
        >
          <Button className="search-button" color="primary" size="medium" onClick={handleFiltering}>
            필터
          </Button>
        </motion.div>
      </motion.section>
    </motion.main>
  );
};

export default MainPageTwo;
