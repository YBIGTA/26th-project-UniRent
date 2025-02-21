import React from "react";
import "./Button.css"; // 버튼 스타일이 있으면 추가

export const Button = ({ children, className, color, size }) => {
  return (
    <button className={`btn ${className} ${color} ${size}`}>
      {children}
    </button>
  );
};

export default Button;