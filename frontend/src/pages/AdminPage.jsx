// src/pages/AdminPage.jsx
import React, { useEffect, useState } from 'react';
import { 
  listEvents, createEvent, updateEvent, deleteEvent, getEventByName,
  createEdition, updateEdition, deleteEdition,
  login, setAuthToken,
  getRecentArticles,
  createArticle
} from '../services/api';
import EventForm from '../components/EventForm';
import EditionForm from '../components/EditionForm';
import ArticleManager from '../components/ArticleManager';
import ArticleList from '../components/ArticleList';
import ArticleForm from '../components/ArticleForm';

// --- Estilos Consistentes ---

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
  gridTemplateColumns: '1fr 8fr 2fr 4fr',
  gap: '1rem',
  alignItems: 'center',
  padding: '1rem',
  borderBottom: '1px solid #444',
};

const actionsCellStyle = {
  display: 'flex',
  gap: '8px',
  alignItems: 'center',
  flexWrap: 'wrap',
};

const headerRowStyle = {
  ...eventRowStyle,
  fontWeight: 'bold',
  color: '#aaa',
  borderBottom: '2px solid #646cff',
};

const editionSectionStyle = {
    padding: '1rem 2rem 1rem 4rem',
    backgroundColor: '#3a3a3c',
};

const editionRowStyle = {
    display: 'grid',
    gridTemplateColumns: '1fr 1fr 1fr',
    gap: '1rem',
    alignItems: 'center',
    padding: '0.75rem',
    borderBottom: '1px solid #555',
}

// --- Componente Principal ---

function AdminPage() {
  const [events, setEvents] = useState([]);
  const [loading, setLoading] = useState(false);
  const [editing, setEditing] = useState(null);
  const [showForm, setShowForm] = useState(false);
  const [showEditionForm, setShowEditionForm] = useState(false);
  const [editingEdition, setEditingEdition] = useState(null);
  const [eventForEdition, setEventForEdition] = useState(null);
  const [expandedEventId, setExpandedEventId] = useState(null);
  const [error, setError] = useState(null);
  const [token, setToken] = useState(localStorage.getItem('access_token') || null);
  const [loginEmail, setLoginEmail] = useState('');
  const [loginPassword, setLoginPassword] = useState('');
  // Artigos
  const [articles, setArticles] = useState([]);
  const [showArticleForm, setShowArticleForm] = useState(false);
  const [editingArticle, setEditingArticle] = useState(null);
  const [notifications, setNotifications] = useState([]);
  const [lastResponse, setLastResponse] = useState(null);
  const [toasts, setToasts] = useState([]);

  const addToast = (text) => {
    const id = `${Date.now()}-${Math.random().toString(36).slice(2,8)}`;
    const item = { id, text };
    setToasts((cur) => [item, ...cur]);
    // auto remove after 5 seconds
    setTimeout(() => {
      setToasts((cur) => cur.filter(t => t.id !== id));
    }, 5000);
  };

  const removeToast = (id) => {
    setToasts((cur) => cur.filter(t => t.id !== id));
  };

  const load = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await listEvents();
      setEvents(res.data.map(ev => ({...ev, edicoes: null})) || []);
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
      // Buscar artigos
      getRecentArticles().then(res => {
        setArticles(res.data || []);
      }).catch(err => {
        setError('Falha ao carregar artigos');
      });
    }
  }, [token]);
  // Função para abrir o formulário de artigo (criação)
  const handleOpenArticleForm = () => {
    setEditingArticle(null);
    setShowArticleForm(true);
  };

  // Função para salvar/criar/editar artigo
  const handleSaveArticle = async (formData, id) => {
    try {
      if (id) {
        // Editar artigo
        const res = await fetch(`http://localhost:8000/artigo/artigo/editar/${id}`, {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('access_token')}`
          },
          body: formData
        });
        let body = {};
        try { body = await res.json(); } catch (e) { body = {}; }
        setLastResponse({ status: res.status, body });
        if (!res.ok) {
          setError(body?.detail || body?.mensagem || 'Erro ao editar artigo');
        }
        if (body.notificacoes && Array.isArray(body.notificacoes) && body.notificacoes.length) {
          setNotifications((cur) => [...body.notificacoes, ...cur]);
          body.notificacoes.forEach(n => addToast(n));
        }
      } else {
        // Criar artigo
        const res = await fetch(`http://localhost:8000/artigo/artigo`, {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('access_token')}`
          },
          body: formData
        });
        // parse response body to capture notificacoes
        let body = {};
        try { body = await res.json(); } catch (e) { body = {}; }
        setLastResponse({ status: res.status, body });
        if (!res.ok) {
          setError(body?.detail || body?.mensagem || 'Erro ao criar artigo');
        }
        if (body.notificacoes && Array.isArray(body.notificacoes) && body.notificacoes.length) {
          setNotifications((cur) => [...body.notificacoes, ...cur]);
          body.notificacoes.forEach(n => addToast(n));
        }
      }
      setShowArticleForm(false);
      setEditingArticle(null);
      // Atualizar lista de artigos
      const res = await getRecentArticles();
      setArticles(res.data || []);
    } catch (err) {
      setError('Erro ao salvar artigo');
    }
  };

  // Handler para importar BibTeX + ZIP via um file picker simples
  const handleImportArticles = async () => {
    try {
      // Cria input temporário para escolher dois arquivos (.bib e .zip)
      const input = document.createElement('input');
      input.type = 'file';
      input.multiple = true;
      input.accept = '.bib,application/zip,application/x-zip-compressed';
      input.onchange = async (e) => {
        const files = Array.from(e.target.files || []);
        const bib = files.find(f => f.name.toLowerCase().endsWith('.bib'));
        const zip = files.find(f => f.name.toLowerCase().endsWith('.zip'));
        if (!bib || !zip) {
          setError('Selecione um arquivo .bib e um .zip contendo os PDFs.');
          return;
        }
        const fd = new FormData();
        fd.append('bibtex_file', bib);
        fd.append('pdf_zip_file', zip);
        try {
          const res = await fetch('http://localhost:8000/artigo/importar-bibtex', {
            method: 'POST',
            headers: {
              'Authorization': `Bearer ${localStorage.getItem('access_token')}`
            },
            body: fd
          });
          const body = await res.json();
          // Backend returns notificacoes: [ { titulo, notificacoes: [..] }, ... ]
          if (body.notificacoes && Array.isArray(body.notificacoes)) {
            const flat = [];
            for (const item of body.notificacoes) {
              if (item.notificacoes && Array.isArray(item.notificacoes)) {
                flat.push(...item.notificacoes);
              }
            }
            if (flat.length) setNotifications((cur) => [...flat, ...cur]);
            if (flat.length) flat.forEach(n => addToast(n));
          }
          // refresh article list
          const res2 = await getRecentArticles();
          setArticles(res2.data || []);
        } catch (err) {
          setError('Falha ao importar pacotes de artigos');
          console.error(err);
        }
      };
      // dispara o diálogo
      input.click();
    } catch (err) {
      setError('Erro ao iniciar importação');
    }
  };

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

  const refreshEditions = async (eventId, eventName) => {
    try {
      const res = await getEventByName(eventName);
      setEvents(currentEvents => {
        const newEvents = [...currentEvents];
        const eventIndex = newEvents.findIndex(ev => ev.id === eventId);
        if (eventIndex !== -1) {
          newEvents[eventIndex].edicoes = res.data.edicoes || [];
        }
        return newEvents;
      });
    } catch (err) {
      setError(`Falha ao recarregar edições do evento ${eventName}`);
    }
  };

  const toggleEditions = async (eventId, eventName) => {
    if (expandedEventId === eventId) {
      setExpandedEventId(null);
    } else {
      setExpandedEventId(eventId);
      const event = events.find(ev => ev.id === eventId);
      if (!event.edicoes) { // Fetch only if not already fetched
        await refreshEditions(eventId, eventName);
      }
    }
  };

  const handleCreateEdition = (ev) => {
    setEventForEdition(ev);
    setEditingEdition(null);
    setShowEditionForm(true);
  };
  
  const handleEditEdition = (edition, event) => {
    setEventForEdition(event);
    setEditingEdition(edition);
    setShowEditionForm(true);
  };

  const handleSaveEdition = async (payload) => {
    try {
      if (editingEdition) {
        await updateEdition(editingEdition.id, payload);
      } else {
        await createEdition(payload);
      }
      await refreshEditions(payload.id_evento, eventForEdition.nome);
      return { success: true, message: `Edição ${editingEdition ? 'atualizada' : 'criada'} com sucesso!` };
    } catch (err) {
      const errorMessage = err?.response?.data?.detail || 'Erro ao salvar edição';
      return { success: false, message: errorMessage };
    }
  };

  const handleDeleteEdition = async (edition, event) => {
    if (!window.confirm(`Confirma exclusão da edição do ano ${edition.ano}?`)) return;
    try {
      await deleteEdition(edition.id);
      await refreshEditions(event.id, event.nome); 
    } catch (err) {
      setError('Erro ao remover edição');
      console.error(err);
    }
  };


  return (
    <>
    <div style={{ maxWidth: '1200px', margin: '0 auto' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem' }}>
        <h1>Painel do Administrador</h1>
        {token && (
          <button onClick={handleLogout} style={{ ...buttonStyle, backgroundColor: '#555', marginLeft: 'auto' }}>Logout</button>
        )}
      </div>

      {!token ? (
        // LOGIN FORM
        <div style={cardStyle}>
          <h3 style={{ marginTop: 0 }}>Faça login para continuar</h3>
          {error && <p style={{ color: '#ff6464' }}>{error}</p>}
          <form onSubmit={handleLogin}>
            <input placeholder="Email" type="email" value={loginEmail} onChange={(e) => setLoginEmail(e.target.value)} style={inputStyle} required />
            <input placeholder="Senha" type="password" value={loginPassword} onChange={(e) => setLoginPassword(e.target.value)} style={inputStyle} required />
            <button type="submit" style={buttonStyle}>Login</button>
          </form>
        </div>
      ) : (
        // ADMIN CONTENT
        <div>
          <div style={{ display: 'flex', gap: '2rem', alignItems: 'flex-start' }}>
            <div style={{ flex: 1 }}>
              <div style={{ ...cardStyle, marginBottom: '2rem' }}>
                <p style={{ margin: 0 }}>Gerencie eventos e suas edições.</p>
                <button onClick={handleCreate} style={buttonStyle}>Novo Evento</button>
              </div>
              {error && <p style={{ color: 'red', textAlign: 'center' }}>{error}</p>}
              {showForm && (
                <EventForm initial={editing} onSave={handleSave} onCancel={() => { setShowForm(false); setEditing(null); }} />
              )}
              {showEditionForm && (
                <EditionForm 
                  event={eventForEdition}
                  initial={editingEdition}
                  onSave={handleSaveEdition} 
                  onCancel={() => { setShowEditionForm(false); setEditingEdition(null); setEventForEdition(null); }} 
                />
              )}
              <div style={cardStyle}>
                <div style={headerRowStyle}>
                  <div></div>
                  <div>Nome</div>
                  <div>Sigla</div>
                  <div>Ações</div>
                </div>
                {loading ? <p>Carregando eventos...</p> : (
                  <div>
                    {events.map(ev => (
                      <React.Fragment key={ev.id}>
                        <div style={eventRowStyle}>
                            <button onClick={() => toggleEditions(ev.id, ev.nome)} style={{...buttonStyle, padding: '8px', width: '40px', fontSize: '1rem', marginTop: 0}}>
                                {expandedEventId === ev.id ? '-' : '+'}
                            </button>
                            <div>{ev.nome}</div>
                            <div>{ev.sigla}</div>
                <div style={actionsCellStyle}>
                  <button onClick={() => handleEdit(ev)} style={{ ...buttonStyle, padding: '8px 16px', fontSize: '0.9rem', marginTop: 0 }}>Editar</button>
                  <button onClick={() => handleCreateEdition(ev)} style={{ ...buttonStyle, padding: '8px 16px', fontSize: '0.9rem', marginTop: 0 }}>Criar Edição</button>
                  <button onClick={() => handleDelete(ev)} style={{ ...buttonStyle, padding: '8px 16px', fontSize: '0.9rem', marginTop: 0, backgroundColor: '#ff6464' }}>Remover</button>
                </div>
                        </div>
                        {expandedEventId === ev.id && (
                            <div style={editionSectionStyle}>
                                {ev.edicoes === null ? <p>Carregando edições...</p> :
                                 ev.edicoes.length === 0 ? <p>Nenhuma edição cadastrada.</p> :
                                 (
                                     <>
                                     <div style={{...editionRowStyle, fontWeight: 'bold'}}>
                                         <div>Ano</div>
                                         <div>Local</div>
                                         <div>Ações</div>
                                     </div>
                                    {ev.edicoes.map(ed => (
                                        <div key={ed.id} style={editionRowStyle}>
                                            <div>{ed.ano}</div>
                                            <div>{ed.local}</div>
                                            <div>
                                                <button onClick={() => handleEditEdition(ed, ev)} style={{ ...buttonStyle, padding: '6px 12px', fontSize: '0.8rem', marginTop: 0 }}>Editar</button>
                                                <button onClick={() => handleDeleteEdition(ed, ev)} style={{ ...buttonStyle, padding: '6px 12px', fontSize: '0.8rem', marginLeft: 8, marginTop: 0, backgroundColor: '#c14242' }}>Deletar</button>
                                            </div>
                                        </div>
                                    ))}
                                    </>
                                 )
                                }
                            </div>
                        )}
                      </React.Fragment>
                    ))}
                  </div>
                )}
              </div>
            </div>
            <div style={{ flex: 1 }}>
              <ArticleManager 
                onAddArticle={handleOpenArticleForm}
                onImportArticles={handleImportArticles}
              />
              {showArticleForm && (
                <ArticleForm 
                  onSave={handleSaveArticle}
                  onCancel={() => {
                    setShowArticleForm(false);
                    setEditingArticle(null);
                  }}
                  initial={editingArticle}
                />
              )}
              <div style={cardStyle}>
                <h2 style={{ marginTop: 0 }}>Lista de Artigos</h2>
                <ArticleList 
                  articles={articles}
                  onEdit={article => {
                    setEditingArticle(article);
                    setShowArticleForm(true);
                  }}
                  onDelete={async article => {
                    if (!window.confirm(`Confirma exclusão do artigo '${article.titulo}'?`)) return;
                    try {
                      await fetch(`http://localhost:8000/artigo/artigo/remover/${article.id}`, {
                        method: 'POST',
                        headers: {
                          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
                        }
                      });
                      // Atualiza lista após deletar
                      const res = await getRecentArticles();
                      setArticles(res.data || []);
                    } catch (err) {
                      setError('Erro ao remover artigo');
                    }
                  }}
                />
              </div>
              {notifications.length > 0 && (
                <div style={{ ...cardStyle, marginTop: '1rem' }}>
                  <h3 style={{ marginTop: 0 }}>Notificações de Subscribers</h3>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
                    {notifications.map((n, i) => (
                      <div key={i} style={{ background: '#111', padding: '8px 12px', borderRadius: '6px', color: '#e6f4ea' }}>
                        {n}
                      </div>
                    ))}
                  </div>
                  <div style={{ marginTop: '8px', display: 'flex', justifyContent: 'flex-end' }}>
                    <button onClick={() => setNotifications([])} style={{ ...buttonStyle, backgroundColor: '#555' }}>Limpar</button>
                  </div>
                </div>
              )}
              {lastResponse && (
                <div style={{ ...cardStyle, marginTop: '1rem' }}>
                  <h3 style={{ marginTop: 0 }}>DEBUG: Última resposta do servidor</h3>
                  <pre style={{ color: '#ddd', whiteSpace: 'pre-wrap', fontSize: '0.9rem' }}>{JSON.stringify(lastResponse, null, 2)}</pre>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
  </div>
  {/* Toast container (fixed top-right) */}
    <div style={{ position: 'fixed', top: 16, right: 16, zIndex: 2000, display: 'flex', flexDirection: 'column', gap: '10px' }}>
      {toasts.map(t => (
        <div key={t.id} style={{ background: 'linear-gradient(180deg,#1f2937,#111827)', color: '#fff', padding: '10px 14px', borderRadius: 8, boxShadow: '0 6px 18px rgba(0,0,0,0.35)', minWidth: 280, maxWidth: 'min(420px,calc(100vw - 40px))' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', gap: 12 }}>
            <div style={{ fontSize: '0.95rem', lineHeight: 1.2 }}>{t.text}</div>
            <button onClick={() => removeToast(t.id)} style={{ marginLeft: 12, background: 'transparent', border: 'none', color: '#9ca3af', cursor: 'pointer' }}>✕</button>
          </div>
        </div>
      ))}
    </div>
    </>
  );
}

export default AdminPage;
