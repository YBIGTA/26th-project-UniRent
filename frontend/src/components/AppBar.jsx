import React from "react";
import { Link } from "react-router-dom";
import "./AppBar.css";

export const AppBar = () => {
  return (
    <header className="app-bar">
      <h1 className="logo">UniRent</h1>
      <div className="nav-container">
        <Link to="/" className="nav-link">Go Back to Main Page</Link>
      </div>
    </header>
  );
};

export default AppBar;
