// Button.jsx
import React from "react";
import "./Button.css";

export const Button = ({ children, className, color, size, onClick }) => {
  return (
    <button 
      className={`btn ${className} ${color} ${size}`}
      onClick={onClick}
    >
      {children}
    </button>
  );
};

export default Button;
