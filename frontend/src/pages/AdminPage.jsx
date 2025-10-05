// src/pages/AdminPage.jsx
import React, { useEffect, useState } from 'react';
import { listEvents, createEvent, updateEvent, deleteEvent, login, setAuthToken } from '../services/api';
import EventForm from '../components/EventForm';

function AdminPage() {
  const [events, setEvents] = useState([]);
  const [loading, setLoading] = useState(false);
  const [editing, setEditing] = useState(null);
  const [showForm, setShowForm] = useState(false);
  const [error, setError] = useState(null);
  const [token, setToken] = useState(localStorage.getItem('access_token') || null);
  const [loginEmail, setLoginEmail] = useState('');
  const [loginPassword, setLoginPassword] = useState('');

  const load = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await listEvents();
      setEvents(res.data || []);
    } catch (err) {
      setError('Falha ao carregar eventos');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { load(); }, []);

  useEffect(() => {
    if (token) {
      setAuthToken(token);
      load();
    }
  }, [token]);

  const handleCreate = () => {
    setEditing(null);
    setShowForm(true);
  };

  const handleLogin = async () => {
    setError(null);
    try {
      const res = await login({ email: loginEmail, senha: loginPassword });
      const t = res.data.access_token;
      setToken(t);
      setAuthToken(t);
      setLoginEmail('');
      setLoginPassword('');
    } catch (err) {
      setError('Falha no login. Verifique credenciais.');
      console.error(err);
    }
  };

  const handleLogout = () => {
    setToken(null);
    setAuthToken(null);
  };

  const handleSave = async (payload) => {
    try {
      if (editing) {
        await updateEvent(editing.id, payload);
      } else {
        await createEvent(payload);
      }
      setShowForm(false);
      setEditing(null);
      await load();
    } catch (err) {
      setError('Erro ao salvar evento');
      console.error(err);
    }
  };

  const handleEdit = (ev) => {
    setEditing(ev);
    setShowForm(true);
  };

  const handleDelete = async (ev) => {
    if (!window.confirm(`Confirma exclusão do evento '${ev.nome}'?`)) return;
    try {
      await deleteEvent(ev.nome);
      await load();
    } catch (err) {
      setError('Erro ao remover evento');
      console.error(err);
    }
  };

  return (
    <div style={{ maxWidth: 900, margin: '0 auto', padding: 20 }}>
      <h1>Painel do Administrador</h1>
      {!token ? (
        <div>
          <h3>Faça login</h3>
          {error && <p style={{ color: 'red' }}>{error}</p>}
          <div>
            <input placeholder="email" value={loginEmail} onChange={(e) => setLoginEmail(e.target.value)} />
          </div>
          <div>
            <input placeholder="senha" type="password" value={loginPassword} onChange={(e) => setLoginPassword(e.target.value)} />
          </div>
          <div style={{ marginTop: 8 }}>
            <button onClick={handleLogin}>Login</button>
          </div>
        </div>
      ) : (
        <div>
          <p>Gerencie eventos: criar, editar e remover.</p>
          <div style={{ marginBottom: 12 }}>
            <button onClick={handleCreate}>Novo Evento</button>
            <button onClick={handleLogout} style={{ marginLeft: 12 }}>Logout</button>
          </div>
          {error && <p style={{ color: 'red' }}>{error}</p>}
        </div>
      )}
      {/* single 'Novo Evento' button is shown in the authenticated branch above; remove duplicate */}

      {token && showForm && (
        <EventForm initial={editing} onSave={handleSave} onCancel={() => { setShowForm(false); setEditing(null); }} />
      )}

      {loading ? <p>Carregando eventos...</p> : (
        <table style={{ width: '100%', borderCollapse: 'collapse' }}>
          <thead>
            <tr>
              <th style={{ textAlign: 'left', borderBottom: '1px solid #ddd' }}>Nome</th>
              <th style={{ textAlign: 'left', borderBottom: '1px solid #ddd' }}>Sigla</th>
              <th style={{ textAlign: 'left', borderBottom: '1px solid #ddd' }}>Entidade</th>
              <th style={{ textAlign: 'left', borderBottom: '1px solid #ddd' }}>Ações</th>
            </tr>
          </thead>
          <tbody>
            {events.map(ev => (
              <tr key={ev.id}>
                <td style={{ padding: '8px 4px' }}>{ev.nome}</td>
                <td style={{ padding: '8px 4px' }}>{ev.sigla}</td>
                <td style={{ padding: '8px 4px' }}>{ev.entidade_promotora}</td>
                <td style={{ padding: '8px 4px' }}>
                  <button onClick={() => handleEdit(ev)}>Editar</button>
                  <button onClick={() => handleDelete(ev)} style={{ marginLeft: 8 }}>Remover</button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}

export default AdminPage;