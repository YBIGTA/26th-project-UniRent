import React, { useState, useEffect } from "react";
import { BrowserRouter as Router, Routes, Route, Navigate } from "react-router-dom";
import axiosInstance from "./axios"; // ✅ axiosInstance 가져오기
import MainPage from "./pages/MainPage";
import MainPageTwo from "./pages/MainPageTwo";
import LoginPage from "./pages/LoginPage";
import SignUpPage from "./pages/SignUpPage";
import FilteringPage from "./pages/FilteringPage";
import FilteringResultsPage from "./pages/FilteringResultsPage"; 
import ListingDetailPage from "./pages/ListingDetailPage";

function App() {
  // ✅ localStorage에서 JWT 토큰 확인하여 로그인 상태 유지
  const [isAuthenticated, setIsAuthenticated] = useState(() => {
    return !!localStorage.getItem("token");
  });

  // ✅ 로그인 상태 변경 시 localStorage 업데이트
  useEffect(() => {
    if (isAuthenticated) {
      localStorage.setItem("isAuthenticated", "true");
    } else {
      localStorage.removeItem("isAuthenticated");
      localStorage.removeItem("token");
    }
  }, [isAuthenticated]);

  // ✅ 로그인 요청 함수
  const handleLogin = async (email, password) => {
    try {
      const response = await axiosInstance.post('/api/users/login', {
        email,
        password
      });
      if (response.data.success) {
        localStorage.setItem("token", response.data.data.token);
        setIsAuthenticated(true);
      }
    } catch (error) {
      console.error("로그인 실패:", error.response.data);
    }
  };

  // ✅ 로그아웃 함수
  const handleLogout = () => {
    localStorage.removeItem("token");
    setIsAuthenticated(false);
  };

  // ✅ 회원가입 요청 함수
  const handleSignUp = async (email, password) => {
    try {
      const response = await axiosInstance.post('/api/users/signup', {
        email,
        password
      });
      console.log("회원가입 성공:", response.data);
    } catch (error) {
      console.error("회원가입 실패:", error.response.data);
    }
  };

  return (
    <Router>
      <Routes>
        <Route
          path="/"
          element={
            isAuthenticated ? <Navigate to="/main-two" /> : <MainPage />
          }
        />
        <Route
          path="/login"
          element={
            <LoginPage
              setIsAuthenticated={setIsAuthenticated}
              handleLogin={handleLogin} // ✅ 로그인 함수 전달
            />
          }
        />
        <Route
          path="/signup"
          element={
            <SignUpPage handleSignUp={handleSignUp} /> // ✅ 회원가입 함수 전달
          }
        />
        <Route 
          path="/main-two" 
          element={
            isAuthenticated ? (
              <MainPageTwo 
                isAuthenticated={isAuthenticated} 
                setIsAuthenticated={setIsAuthenticated} 
                handleLogout={handleLogout}  // ✅ 로그아웃 함수 전달
              />
            ) : (
              <Navigate to="/login" />
            )
          }
        />
        <Route 
          path="/filtering" 
          element={isAuthenticated ? <FilteringPage /> : <Navigate to="/main-two" />} 
        />
        <Route path="/filtering-results" element={<FilteringResultsPage />} />
        <Route path="/details/:id" element={<ListingDetailPage />} />
      </Routes>
    </Router>
  );
}

export default App;
