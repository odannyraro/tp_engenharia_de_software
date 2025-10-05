// src/pages/AdminPage.jsx
import React, { useEffect, useState } from 'react';
import { listEvents, createEvent, updateEvent, deleteEvent, login, setAuthToken } from '../services/api';
import EventForm from '../components/EventForm';

// --- Estilos Consistentes com a HomePage ---

const cardStyle = {
  background: '#2c2c2e',
  borderRadius: '8px',
  padding: '1.5rem',
  boxShadow: '0 4px 12px rgba(0, 0, 0, 0.3)',
  marginBottom: '2rem',
};

const inputStyle = {
  width: '100%',
  padding: '12px 20px',
  margin: '8px 0',
  boxSizing: 'border-box',
  fontSize: '1rem',
  borderRadius: '25px',
  border: '1px solid #555',
  backgroundColor: '#333',
  color: '#fff',
};

const buttonStyle = {
  padding: '12px 30px',
  fontSize: '1rem',
  borderRadius: '25px',
  border: 'none',
  backgroundColor: '#646cff',
  color: '#fff',
  cursor: 'pointer',
  marginTop: '10px',
  transition: 'background-color 0.3s',
};

const eventRowStyle = {
  display: 'grid',
  gridTemplateColumns: '3fr 1fr 2fr 1fr',
  gap: '1rem',
  alignItems: 'center',
  padding: '1rem',
  borderBottom: '1px solid #444',
};

const headerRowStyle = {
  ...eventRowStyle,
  fontWeight: 'bold',
  color: '#aaa',
  borderBottom: '2px solid #646cff',
};

// --- Componente Principal ---

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

  const handleLogin = async (e) => {
    e.preventDefault();
    setError(null);
    try {
      const res = await login({ email: loginEmail, senha: loginPassword });
      const t = res.data.access_token;
      setToken(t);
      setAuthToken(t);
      setLoginEmail('');
      setLoginPassword('');
    } catch (err) {
      setError('Falha no login. Verifique as credenciais e se o usuário é administrador.');
      console.error(err);
    }
  };

  const handleLogout = () => {
    setToken(null);
    setAuthToken(null);
    localStorage.removeItem('access_token');
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
    <div style={{ maxWidth: '1200px', margin: '0 auto' }}>
      <div style={{ textAlign: 'center', marginBottom: '2rem' }}>
        <h1>Painel do Administrador</h1>
      </div>

      {!token ? (
        <div style={cardStyle}>
          <h3 style={{ marginTop: 0 }}>Faça login para continuar</h3>
          {error && <p style={{ color: '#ff6464' }}>{error}</p>}
          <form onSubmit={handleLogin}>
            <input
              placeholder="Email"
              type="email"
              value={loginEmail}
              onChange={(e) => setLoginEmail(e.target.value)}
              style={inputStyle}
              required
            />
            <input
              placeholder="Senha"
              type="password"
              value={loginPassword}
              onChange={(e) => setLoginPassword(e.target.value)}
              style={inputStyle}
              required
            />
            <button type="submit" style={buttonStyle}>Login</button>
          </form>
        </div>
      ) : (
        <div>
          <div style={{ ...cardStyle, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <p style={{ margin: 0 }}>Gerencie eventos: criar, editar e remover.</p>
            <div>
              <button onClick={handleCreate} style={buttonStyle}>Novo Evento</button>
              <button onClick={handleLogout} style={{ ...buttonStyle, marginLeft: 12, backgroundColor: '#555' }}>Logout</button>
            </div>
          </div>
          
          {error && <p style={{ color: 'red', textAlign: 'center' }}>{error}</p>}

          {showForm && (
            <div style={cardStyle}>
              <EventForm initial={editing} onSave={handleSave} onCancel={() => { setShowForm(false); setEditing(null); }} />
            </div>
          )}

          <div style={cardStyle}>
            <div style={headerRowStyle}>
              <div>Nome</div>
              <div>Sigla</div>
              <div>Entidade</div>
              <div>Ações</div>
            </div>
            {loading ? <p>Carregando eventos...</p> : (
              <div>
                {events.map(ev => (
                  <div key={ev.id} style={eventRowStyle}>
                    <div>{ev.nome}</div>
                    <div>{ev.sigla}</div>
                    <div>{ev.entidade_promotora}</div>
                    <div>
                      <button onClick={() => handleEdit(ev)} style={{ ...buttonStyle, padding: '8px 16px', fontSize: '0.9rem' }}>Editar</button>
                      <button onClick={() => handleDelete(ev)} style={{ ...buttonStyle, padding: '8px 16px', fontSize: '0.9rem', marginLeft: 8, backgroundColor: '#ff6464' }}>Remover</button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

export default AdminPage;