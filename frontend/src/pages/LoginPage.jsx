import React, { useState } from 'react';
import { login, storeUserToken } from '../services/api';

function LoginPage() {
  const [email, setEmail] = useState('');
  const [senha, setSenha] = useState('');
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleLogin = async () => {
    setError(null);
    setLoading(true);
    try {
      const res = await login({ email, senha });
  const token = res.data.access_token;
  // store only as user token (do not set axios default header used by admin flows)
  storeUserToken(token);
  // store user meta and notify
  localStorage.setItem('user', JSON.stringify(res.data.user || null));
  window.dispatchEvent(new Event('userChanged'));
      setEmail('');
      setSenha('');
    } catch (err) {
      console.error(err);
      setError(err?.response?.data?.detail || 'Erro no login');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ maxWidth: 600, margin: '0 auto', padding: 20 }}>
      <h1>Login</h1>
      {error && <p style={{ color: 'red' }}>{error}</p>}
      <div style={{ marginBottom: 8 }}>
        <label>Email</label>
        <br />
        <input value={email} onChange={(e) => setEmail(e.target.value)} style={{ width: '100%' }} />
      </div>
      <div style={{ marginBottom: 8 }}>
        <label>Senha</label>
        <br />
        <input type="password" value={senha} onChange={(e) => setSenha(e.target.value)} style={{ width: '100%' }} />
      </div>
      <div>
        <button onClick={handleLogin} disabled={loading}>{loading ? 'Entrando...' : 'Entrar'}</button>
      </div>
    </div>
  );
}

export default LoginPage;
