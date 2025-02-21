import React from "react";
import "./Card.css"; 

export const Card = ({ className, cardVariant }) => {
  return (
    <div className={`card ${cardVariant} ${className}`}>
      <p>이곳에 카드 내용을 추가하세요</p>
    </div>
  );
};

export default Card;
