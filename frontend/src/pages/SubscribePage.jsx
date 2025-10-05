// src/pages/SubscribePage.jsx
import React, { useState } from 'react';
import { createAccount } from '../services/api';

// --- Estilos Consistentes ---

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

// --- Componente Principal ---

function SubscribePage() {
  const [nome, setNome] = useState('');
  const [email, setEmail] = useState('');
  const [senha, setSenha] = useState('');
  const [senhaConfirm, setSenhaConfirm] = useState('');
  const [status, setStatus] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setStatus(null);
    setLoading(true);
    try {
      // Validações do lado do cliente
      if (senha.length < 5) {
        setStatus({ ok: false, message: 'A senha deve ter ao menos 5 caracteres.' });
        setLoading(false);
        return;
      }
      if (senha !== senhaConfirm) {
        setStatus({ ok: false, message: 'As senhas não coincidem.' });
        setLoading(false);
        return;
      }

      await createAccount({ nome, email, senha, admin: false });
      setStatus({ ok: true, message: 'Conta criada com sucesso! Você pode agora fazer login.' });
      
      // Limpa os campos após o sucesso
      setNome('');
      setEmail('');
      setSenha('');
      setSenhaConfirm('');
    } catch (err) {
      console.error(err);
      const msg = err?.response?.data?.detail || 'Falha ao realizar inscrição';
      setStatus({ ok: false, message: msg });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={cardStyle}>
      <h1 style={{ textAlign: 'center', marginTop: 0 }}>Crie sua Conta</h1>
      
      <form onSubmit={handleSubmit}>
        <div style={{ marginBottom: 8 }}>
          <label>Nome completo</label>
          <input 
            value={nome} 
            onChange={(e) => setNome(e.target.value)} 
            required 
            style={inputStyle} 
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
          />
        </div>
        <div style={{ marginBottom: 8 }}>
          <label>Senha</label>
          <input 
            type="password" 
            value={senha} 
            onChange={(e) => setSenha(e.target.value)} 
            required 
            style={inputStyle} 
            minLength={5} 
          />
        </div>
        <div style={{ marginBottom: 8 }}>
          <label>Confirme a senha</label>
          <input 
            type="password" 
            value={senhaConfirm} 
            onChange={(e) => setSenhaConfirm(e.target.value)} 
            required 
            style={inputStyle} 
            minLength={5} 
          />
        </div>
        <div>
          <button type="submit" disabled={loading} style={buttonStyle}>
            {loading ? 'Criando...' : 'Criar conta'}
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

export default SubscribePage;