import React from "react";
import "./TextField.css"; // 스타일이 필요하면 추가

export const TextField = ({ className, variant, placeholder, value, onChange, type = "text" }) => {
  return (
    <input
      type={type} // type을 받도록 설정 (text, password 등)
      className={`text-field ${variant} ${className}`}
      placeholder={placeholder}
      value={value} // 부모에서 전달한 value 적용
      onChange={onChange} // 부모에서 전달한 onChange 적용
    />
  );
};

export default TextField;
