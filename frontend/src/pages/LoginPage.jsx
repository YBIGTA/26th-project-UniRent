import React, { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { Button } from "../components/Button";
import { TextField } from "../components/TextField";
import { AppBar } from "../components/AppBar";
import "./LoginPage.css";
import axiosInstance from "../api/axios";

export const LoginPage = ({ setIsAuthenticated }) => {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const navigate = useNavigate();

  const handleLogin = async (e) => {
    e.preventDefault();
    try {
      const response = await axiosInstance.post("/login", {
        email,
        password
      });
      if (response.data.success) {
        localStorage.setItem("token", response.data.data.token);
        setIsAuthenticated(true);
        navigate("/main-two"); // 로그인 후 MainPageTwo로 이동
      }
    } catch (error) {
      console.error("로그인 실패:", error.response.data);
      alert("로그인 실패! 이메일 또는 비밀번호를 확인하세요.");
    }
  };

  return (
    <div className="login-page">
      <AppBar className="app-bar-instance" />
      <main className="login-container">
        <form className="login-form" onSubmit={handleLogin}>
          <div className="input-group">
            <label htmlFor="email">email</label>
            <TextField
              id="email"
              placeholder="email"
              variant="outlined"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
            />
          </div>
          <div className="input-group">
            <label htmlFor="password">password</label>
            <TextField
              id="password"
              type="password"
              placeholder="password"
              variant="outlined"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
            />
          </div>
          <div className="actions">
            <Link to="/signup" className="signup-text">회원가입</Link>
            <Button color="primary" size="medium" type="submit">
              로그인
            </Button>
          </div>
        </form>
      </main>
    </div>
  );
};

export default LoginPage;
