// src/components/Header.jsx
import React, { useState, useEffect } from 'react';
import { Link, NavLink, useNavigate } from 'react-router-dom';

// --- ESTILOS ---

const headerStyle = {
  display: 'flex',
  justifyContent: 'space-between',
  alignItems: 'center',
  padding: '1rem 2rem',
  borderBottom: '1px solid #444',
  backgroundColor: '#1e1e1e',
};

const logoStyle = {
  textDecoration: 'none',
  color: '#fff',
  fontSize: '1.5rem',
  fontWeight: 'bold',
  display: 'flex',
  alignItems: 'center',
  gap: '10px',
};

const logoImageStyle = {
  width: '32px',
  height: '32px',
  objectFit: 'contain',
};

const navStyle = {
  display: 'flex',
  alignItems: 'center',
  gap: '10px',
};

const navLinkStyle = {
  padding: '8px 16px',
  borderRadius: '20px',
  textDecoration: 'none',
  color: '#ccc',
  backgroundColor: 'transparent',
  border: '1px solid transparent',
  transition: 'all 0.3s ease',
};

const activeLinkStyle = {
  backgroundColor: '#646cff',
  color: '#fff',
  borderColor: '#646cff',
};

const userStyle = {
  color: '#ccc',
  display: 'flex',
  alignItems: 'center',
  gap: '15px'
};

const logoutButtonStyle = {
  padding: '8px 16px',
  borderRadius: '20px',
  border: '1px solid #ff6464',
  backgroundColor: 'transparent',
  color: '#ff6464',
  cursor: 'pointer',
  transition: 'all 0.3s ease',
};


// --- COMPONENTE ---

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
    localStorage.removeItem('user');
    localStorage.removeItem('user_access_token');
    setUser(null);
    window.dispatchEvent(new Event('userChanged'));
    navigate('/');
  };

  return (
    <header style={headerStyle}>
      {/* Lado Esquerdo: Logo */}
      <Link to="/" style={logoStyle}>
        <img src="/lattes-cinius.png" alt="LattesCinius Logo" style={logoImageStyle} />
        <span>LattesCinius</span>
      </Link>

      {/* Lado Direito: Navegação e Usuário */}
      <nav style={navStyle}>
        <NavLink 
          to="/" 
          style={({ isActive }) => ({ ...navLinkStyle, ...(isActive ? activeLinkStyle : {}) })}
        >
          Home
        </NavLink>
        <NavLink 
          to="/admin" 
          style={({ isActive }) => ({ ...navLinkStyle, ...(isActive ? activeLinkStyle : {}) })}
        >
          Admin
        </NavLink>
        
        {/* Seção do Usuário */}
        <NavLink 
          to="/notifications/signup" 
          style={({ isActive }) => ({ ...navLinkStyle, ...(isActive ? activeLinkStyle : {}) })}
        >
          Assinar Notificações
        </NavLink>
        
        {user ? (
          <div style={userStyle}>
            <span>Olá, {user.nome}</span>
            <NavLink 
              to={`/authors/${slugify(user.nome)}`}
              style={({ isActive }) => ({ ...navLinkStyle, ...(isActive ? activeLinkStyle : {}) })}
            >
              Meus Artigos
            </NavLink>
            <button 
              onClick={handleLogout} 
              style={logoutButtonStyle}
              onMouseOver={(e) => { e.target.style.backgroundColor = '#ff6464'; e.target.style.color = '#fff'; }}
              onMouseOut={(e) => { e.target.style.backgroundColor = 'transparent'; e.target.style.color = '#ff6464'; }}
            >
              Logout
            </button>
          </div>
        ) : (
          <>
            <NavLink 
              to="/signup" 
              style={({ isActive }) => ({ ...navLinkStyle, ...(isActive ? activeLinkStyle : {}) })}
            >
              Sign Up
            </NavLink>
            <NavLink 
              to="/login" 
              style={({ isActive }) => ({ ...navLinkStyle, ...(isActive ? activeLinkStyle : {}) })}
            >
              Login
            </NavLink>
          </>
        )}
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