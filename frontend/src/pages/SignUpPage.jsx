// import React from "react";
// import { Button } from "../components/Button";
// import { TextField } from "../components/TextField";
// import { AppBar } from "../components/AppBar";
// import "./SignUpPage.css";

// export const SignUpPage = () => {
//   return (
//     <div className="sign-up-page">
//       <AppBar className="app-bar" />
//       <main className="sign-up-container">
//         <section className="sign-up-box">
//           <form className="sign-up-form">
//             <label htmlFor="email" className="input-label">email</label>
//             <TextField 
//               id="email" 
//               type="email" 
//               placeholder="ex) email@email.com" 
//               variant="standard"
//               className="input-field" 
//             />

//             <label htmlFor="password" className="input-label">password</label>
//             <TextField 
//               id="password" 
//               type="password" 
//               variant="outlined"
//               className="input-field" 
//             />

//             <Button className="submit-button" color="primary" size="medium">
//               계정 생성
//             </Button>
//           </form>
//         </section>
//       </main>
//     </div>
//   );
// };

// export default SignUpPage;


import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Button } from "../components/Button";
import { TextField } from "../components/TextField";
import { AppBar } from "../components/AppBar";
import "./SignUpPage.css";

export const SignUpPage = () => {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const navigate = useNavigate();

  const handleSignUp = (e) => {
    e.preventDefault();
    console.log("입력된 이메일:", email);
    console.log("입력된 비밀번호:", password);

    if (email.trim() !== "" && password.trim() !== "") {
      alert("계정이 생성되었습니다! 로그인하세요.");
      navigate("/login");
    } else {
      alert("이메일과 비밀번호를 입력해주세요.");
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
