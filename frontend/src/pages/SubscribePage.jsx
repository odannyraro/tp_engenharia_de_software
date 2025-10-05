// src/pages/SubscribePage.jsx
import React, { useState } from 'react';
import { createAccount } from '../services/api';

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
      // client-side validation
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

      const res = await createAccount({ nome, email, senha, admin: false });
      setStatus({ ok: true, message: 'Conta criada com sucesso! Você pode agora fazer login.' });
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
    <div style={{ maxWidth: 600, margin: '0 auto', padding: 20 }}>
  <h1>Crie sua conta</h1>
      <form onSubmit={handleSubmit}>
        <div style={{ marginBottom: 8 }}>
          <label>Nome completo</label>
          <br />
          <input value={nome} onChange={(e) => setNome(e.target.value)} required style={{ width: '100%' }} />
        </div>
        <div style={{ marginBottom: 8 }}>
          <label>Email</label>
          <br />
          <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} required style={{ width: '100%' }} />
        </div>
        <div style={{ marginBottom: 8 }}>
          <label>Senha</label>
          <br />
          <input type="password" value={senha} onChange={(e) => setSenha(e.target.value)} required style={{ width: '100%' }} minLength={5} />
        </div>
        <div style={{ marginBottom: 8 }}>
          <label>Confirme a senha</label>
          <br />
          <input type="password" value={senhaConfirm} onChange={(e) => setSenhaConfirm(e.target.value)} required style={{ width: '100%' }} minLength={5} />
        </div>
        <div>
          <button type="submit" disabled={loading}>{loading ? 'Enviando...' : 'Criar conta'}</button>
        </div>
      </form>

      {status && (
        <p style={{ marginTop: 12, color: status.ok ? 'green' : 'red' }}>{status.message}</p>
      )}
    </div>
  );
}

export default SubscribePage;