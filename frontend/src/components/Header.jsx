// src/components/Header.jsx
import React from 'react';
import { Link } from 'react-router-dom';

function Header() {
  return (
    <header style={{ marginBottom: '20px', padding: '10px', borderBottom: '1px solid #ccc' }}>
      <nav>
        <Link to="/" style={{ marginRight: '15px' }}>Home</Link>
        <Link to="/subscribe" style={{ marginRight: '15px' }}>Login</Link>
      </nav>
    </header>
  );
}

export default Header;