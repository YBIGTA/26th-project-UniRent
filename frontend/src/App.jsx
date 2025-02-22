import React, { useState, useEffect } from "react";
import { BrowserRouter as Router, Routes, Route, Navigate } from "react-router-dom";
import MainPage from "./pages/MainPage";
import MainPageTwo from "./pages/MainPageTwo";
import LoginPage from "./pages/LoginPage";
import SignUpPage from "./pages/SignUpPage";
import FilteringPage from "./pages/FilteringPage";
import FilteringResultsPage from "./pages/FilteringResultsPage"; // ✅ 필터링 결과 페이지 추가

function App() {
  // ✅ localStorage에서 로그인 상태 유지
  const [isAuthenticated, setIsAuthenticated] = useState(() => {
    return localStorage.getItem("isAuthenticated") === "true";
  });

  // ✅ 로그인 상태가 변경되면 localStorage에 저장
  useEffect(() => {
    localStorage.setItem("isAuthenticated", isAuthenticated);
  }, [isAuthenticated]);

  console.log("현재 인증 상태:", isAuthenticated); // ✅ 인증 상태 확인용 콘솔 출력

  return (
    <Router>
      <Routes>
        {/*         <Route path="/" element={<MainPage />} /> */}
        <Route
          path="/"
          element={
            isAuthenticated ? <Navigate to="/main-two" /> : <MainPage />
          }
        />

        {/* ✅ 로그인 페이지 (로그인하면 MainPageTwo로 이동) */}
        <Route path="/login" element={<LoginPage setIsAuthenticated={setIsAuthenticated} />} />
        <Route path="/signup" element={<SignUpPage />} />

        {/* ✅ 로그인한 경우에만 MainPageTwo 접근 가능 */}
        <Route 
          path="/main-two" 
          element={isAuthenticated ? <MainPageTwo isAuthenticated={isAuthenticated} setIsAuthenticated={setIsAuthenticated} /> : <Navigate to="/login" />} 
        />

        {/* ✅ FilteringPage는 MainPageTwo에서만 접근 가능 */}
        <Route 
          path="/filtering" 
          element={isAuthenticated ? <FilteringPage /> : <Navigate to="/main-two" />} 
        />

        {/* ✅ 필터링 결과 페이지 */}
        <Route path="/filtering-results" element={<FilteringResultsPage />} />
      </Routes>
    </Router>
  );
}

export default App;
