import React from "react";
import { Link, useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import "./MainPage.css";
import { Button } from "../components/Button";

export const MainPage = ({ isAuthenticated }) => {
  const navigate = useNavigate();

  const handleFiltering = () => {
    console.log('로그인 안 된 채로 필터 버튼 클릭됨, 로그인 페이지로 이동');
    navigate('/login');
  };

  return (
    <motion.main 
      className="main-page"
      initial={{ opacity: 0, y: 30 }} // 페이지 로드 시 페이드 인 & 위로 올라오는 효과
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6, ease: "easeOut" }}
    >
      <header className="header">
        <nav className="nav">
          {isAuthenticated ? (
            <motion.p 
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ duration: 0.5, delay: 0.3 }}
            >
              로그인됨
            </motion.p>
          ) : (
            <>
              <motion.div whileHover={{ scale: 1.1 }}>
                <Link to="/login" className="nav-link">Login</Link>
              </motion.div>
              <motion.div whileHover={{ scale: 1.1 }}>
                <Link to="/signup" className="nav-link">Sign up</Link>
              </motion.div>
            </>
          )}
        </nav>
      </header>

      <section className="content">
        <motion.h1 
          className="title"
          initial={{ opacity: 0, scale: 0.8 }}
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
          🔍 필터를 활용해 원하는 숙소를 찾아보세요!
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
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.5, delay: 0.5 }}
      >
        <p className="filter-text">
          어떤 매물을 찾으시나요? 오른쪽 필터 버튼을 눌러보세요!
        </p>

        <Link to="/filtering">
          <motion.div 
            whileHover={{ scale: 1.1 }}
            whileTap={{ scale: 0.95 }}
          >
            <Button className="search-button" color="primary" size="medium" onClick={handleFiltering}>
              필터
            </Button>
          </motion.div>
        </Link>
      </motion.section>
    </motion.main>
  );
};

export default MainPage;
