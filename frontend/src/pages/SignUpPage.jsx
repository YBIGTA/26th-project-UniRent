import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Button } from "../components/Button";
import { TextField } from "../components/TextField";
import { AppBar } from "../components/AppBar";
import "./SignUpPage.css";
import axiosInstance from "../axios";

export const SignUpPage = () => {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const navigate = useNavigate();

  const handleSignUp = async (e) => {
    e.preventDefault();
    try {
      const response = await axiosInstance.post("/signup", {
        email,
        password
      });
      if (response.data.success) {
        alert("회원가입이 완료되었습니다! 로그인하세요.");
        navigate("/login");
      }
    } catch (error) {
      console.error("회원가입 실패:", error.response.data);
      alert("회원가입 실패! 이메일 중복 확인 또는 서버 오류입니다.");
    }
  };
  
  return (
    <div className="sign-up-page">
      <AppBar className="app-bar" />
      <main className="sign-up-container">
        <section className="sign-up-box">
          <form className="sign-up-form" onSubmit={handleSignUp}>
            <label htmlFor="email" className="input-label">email</label>
            <TextField
              id="email"
              type="email"
              placeholder="ex) email@email.com"
              variant="standard"
              className="input-field"
              value={email} // ✅ 입력값 반영
              onChange={(e) => setEmail(e.target.value)} // ✅ 입력값 업데이트
            />

            <label htmlFor="password" className="input-label">password</label>
            <TextField
              id="password"
              type="password"
              variant="outlined"
              className="input-field"
              value={password} // ✅ 입력값 반영
              onChange={(e) => setPassword(e.target.value)} // ✅ 입력값 업데이트
            />

            <Button className="submit-button" color="primary" size="medium" type="submit">
              계정 생성
            </Button>
          </form>
        </section>
      </main>
    </div>
  );
};

export default SignUpPage;
