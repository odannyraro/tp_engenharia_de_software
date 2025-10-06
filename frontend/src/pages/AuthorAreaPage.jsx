// src/pages/AuthorAreaPage.jsx
import React, { useState } from 'react';
import { subscribe } from '../services/api';

const cardStyle = {
  background: '#2c2c2e',
  borderRadius: '8px',
  padding: '2rem',
  boxShadow: '0 4px 12px rgba(0, 0, 0, 0.3)',
  maxWidth: '450px',
  margin: '4rem auto',
};

const inputStyle = {
  width: '100%',
  padding: '12px 20px',
  margin: '8px 0 20px',
  boxSizing: 'border-box',
  fontSize: '1rem',
  borderRadius: '25px',
  border: '1px solid #555',
  backgroundColor: '#333',
  color: '#fff',
};

const buttonStyle = {
  width: '100%',
  padding: '12px 30px',
  fontSize: '1.1rem',
  borderRadius: '25px',
  border: 'none',
  backgroundColor: '#646cff',
  color: '#fff',
  cursor: 'pointer',
  marginTop: '10px',
  transition: 'background-color 0.3s',
};

function AuthorAreaPage() {
  const [nome, setNome] = useState('');
  const [email, setEmail] = useState('');
  const [status, setStatus] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setStatus(null);
    setLoading(true);
    try {
      await subscribe({ nome, email });
      setStatus({ ok: true, message: 'Cadastro realizado com sucesso! Você receberá notificações quando artigos seus forem publicados.' });
      setNome('');
      setEmail('');
    } catch (err) {
      let msg = 'Falha ao realizar cadastro';
      if (err?.response?.data) {
        if (typeof err.response.data === 'string') {
          msg = err.response.data;
        } else if (err.response.data.detail) {
          msg = err.response.data.detail;
        } else {
          msg = JSON.stringify(err.response.data);
        }
      } else if (err?.message) {
        msg = err.message;
      }
      setStatus({ ok: false, message: msg });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={cardStyle}>
      <h1 style={{ textAlign: 'center', marginTop: 0 }}>Author Area</h1>
      <p style={{ textAlign: 'center', color: '#888', marginBottom: '2rem' }}>
        Preencha seu nome completo, como usado em seus artigos, e o email por onde deseja receber atualizações.
      </p>
      <form onSubmit={handleSubmit}>
        <div style={{ marginBottom: 8 }}>
          <label>Nome completo</label>
          <input 
            value={nome} 
            onChange={(e) => setNome(e.target.value)} 
            required 
            style={inputStyle}
            placeholder="Ex: Sobrenome, Nome"
          />
        </div>
        <div style={{ marginBottom: 8 }}>
          <label>Email</label>
          <input 
            type="email" 
            value={email} 
            onChange={(e) => setEmail(e.target.value)} 
            required 
            style={inputStyle}
            placeholder="seu@email.com"
          />
        </div>
        <div>
          <button type="submit" disabled={loading} style={buttonStyle}>
            {loading ? 'Cadastrando...' : 'Continuar'}
          </button>
        </div>
      </form>
      {status && (
        <p style={{ 
          marginTop: '1.5rem', 
          textAlign: 'center',
          color: status.ok ? '#28a745' : '#ff6464',
          fontWeight: 'bold',
        }}>
          {status.message}
        </p>
      )}
    </div>
  );
}

export default AuthorAreaPage;
