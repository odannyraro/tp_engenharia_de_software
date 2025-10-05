// src/components/Header.jsx
import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { setAuthToken } from '../services/api';

function Header() {
  const [user, setUser] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    const readUser = () => {
      const raw = localStorage.getItem('user');
      if (raw) {
        try {
          setUser(JSON.parse(raw));
        } catch (e) {
          setUser(null);
        }
      } else {
        setUser(null);
      }
    };

    readUser();
    const handler = () => readUser();
    window.addEventListener('userChanged', handler);
    return () => window.removeEventListener('userChanged', handler);
  }, []);

  const handleLogout = () => {
    // remove only user session (do not clear admin token)
    localStorage.removeItem('user');
    localStorage.removeItem('user_access_token');
    setUser(null);
    window.dispatchEvent(new Event('userChanged'));
    navigate('/');
  };

  return (
    <header style={{ marginBottom: '20px', padding: '10px', borderBottom: '1px solid #ccc' }}>
      <nav>
        <Link to="/" style={{ marginRight: '15px' }}>Home</Link>
        <Link to="/signup" style={{ marginRight: '15px' }}>Sign Up</Link>
        <Link to="/login" style={{ marginRight: '15px' }}>Login</Link>
        <Link to="/admin" style={{ marginRight: '15px' }}>Admin</Link>
        {user ? (
          <span style={{ marginLeft: 12 }}>
            Olá, {user.nome}
            <Link to={`/authors/${slugify(user.nome)}`} style={{ marginLeft: 8, marginRight: 8 }}>Meus artigos</Link>
            <button onClick={handleLogout} style={{ marginLeft: 8 }}>Logout</button>
          </span>
        ) : null}
      </nav>
    </header>
  );
}

function slugify(name) {
  if (!name) return '';
  return name
    .replace(/,/g, '')
    .trim()
    .toLowerCase()
    .replace(/\s+/g, '-');
}

export default Header;