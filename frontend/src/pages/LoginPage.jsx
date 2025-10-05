import React, { useState } from 'react';
import { login, storeUserToken } from '../services/api';

// --- Estilos Consistentes ---

const cardStyle = {
  background: '#2c2c2e',
  borderRadius: '8px',
  padding: '2rem',
  boxShadow: '0 4px 12px rgba(0, 0, 0, 0.3)',
  maxWidth: '450px',
  margin: '4rem auto', // Adiciona margem no topo para centralizar melhor verticalmente
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

function LoginPage() {
  const [email, setEmail] = useState('');
  const [senha, setSenha] = useState('');
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleLogin = async (e) => {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      const res = await login({ email, senha });
      const token = res.data.access_token;
      
      // Armazena o token e os dados do usuário no localStorage
      storeUserToken(token);
      localStorage.setItem('user', JSON.stringify(res.data.user || null));
      
      // Dispara um evento para notificar outros componentes (como o Header) sobre a mudança
      window.dispatchEvent(new Event('userChanged'));
      
      // Limpa os campos após o login
      setEmail('');
      setSenha('');

      // Opcional: Redirecionar para a home ou dashboard após o login
      // navigate('/'); 
    } catch (err) {
      console.error(err);
      setError(err?.response?.data?.detail || 'Erro no login. Verifique suas credenciais.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={cardStyle}>
      <h1 style={{ textAlign: 'center', marginTop: 0 }}>Login</h1>
      {error && <p style={{ color: '#ff6464', textAlign: 'center' }}>{error}</p>}
      
      <form onSubmit={handleLogin}>
        <div style={{ marginBottom: 8 }}>
          <label>Email</label>
          <input 
            type="email"
            value={email} 
            onChange={(e) => setEmail(e.target.value)} 
            style={inputStyle}
            required
          />
        </div>
        <div style={{ marginBottom: 8 }}>
          <label>Senha</label>
          <input 
            type="password" 
            value={senha} 
            onChange={(e) => setSenha(e.target.value)} 
            style={inputStyle}
            required
          />
        </div>
        <div>
          <button type="submit" disabled={loading} style={buttonStyle}>
            {loading ? 'Entrando...' : 'Entrar'}
          </button>
        </div>
      </form>
    </div>
  );
}

export default LoginPage;