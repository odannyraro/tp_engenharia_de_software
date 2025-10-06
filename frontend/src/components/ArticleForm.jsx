// src/components/ArticleForm.jsx
import React, { useState, useEffect } from 'react';

const modalOverlayStyle = {
  position: 'fixed',
  top: 0,
  left: 0,
  right: 0,
  bottom: 0,
  backgroundColor: 'rgba(0, 0, 0, 0.7)',
  display: 'flex',
  justifyContent: 'center',
  alignItems: 'center',
  zIndex: 1000,
};

const modalContentStyle = {
  background: '#2c2c2e',
  borderRadius: '8px',
  padding: '2rem',
  boxShadow: '0 5px 15px rgba(0, 0, 0, 0.5)',
  width: '90%',
  maxWidth: '500px',
  position: 'relative',
};

const closeButtonStyle = {
  position: 'absolute',
  top: '15px',
  right: '15px',
  background: 'transparent',
  border: 'none',
  fontSize: '1.5rem',
  color: '#aaa',
  cursor: 'pointer',
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
  padding: '12px 30px',
  fontSize: '1rem',
  borderRadius: '25px',
  border: 'none',
  backgroundColor: '#646cff',
  color: '#fff',
  cursor: 'pointer',
  transition: 'background-color 0.3s',
};

export default function ArticleForm({ onSave, onCancel, initial }) {
  const [titulo, setTitulo] = useState(initial?.titulo || '');
  const [autores, setAutores] = useState(initial?.autores || '');
  const [nomeEvento, setNomeEvento] = useState(initial?.nome_evento || '');
  const [ano, setAno] = useState(initial?.ano || '');
  const [paginaInicial, setPaginaInicial] = useState(initial?.pagina_inicial || '');
  const [paginaFinal, setPaginaFinal] = useState(initial?.pagina_final || '');
  const [pdf, setPdf] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (initial) {
      setTitulo(initial.titulo || '');
      setAutores(initial.autores || '');
      setNomeEvento(initial.nome_evento || '');
      setAno(initial.ano || '');
      setPaginaInicial(initial.pagina_inicial || '');
      setPaginaFinal(initial.pagina_final || '');
      setPdf(null); // PDF não é preenchido por padrão
    }
  }, [initial]);

  const handleSubmit = (e) => {
    e.preventDefault();
    const formData = new FormData();
    formData.append('titulo', titulo);
    formData.append('autores', autores);
    formData.append('nome_evento', nomeEvento);
    formData.append('ano', ano);
    formData.append('pagina_inicial', paginaInicial);
    formData.append('pagina_final', paginaFinal);
    // Se for edição, PDF é opcional
    if (pdf) {
      formData.append('pdf_file', pdf);
    }
    // Se for edição, incluir id
    if (initial?.id) {
      formData.append('id', initial.id);
    }
    // Validação: PDF obrigatório só na criação
    if (!initial && !pdf) {
      setError('Selecione um arquivo PDF.');
      return;
    }
    if (onSave) onSave(formData, initial?.id);
  };

  // Garante que o clique no overlay fecha o modal, mas clique dentro do conteúdo não
  const handleOverlayClick = (e) => {
    if (e.target === e.currentTarget && onCancel) {
      onCancel();
    }
  };

  return (
    <div style={modalOverlayStyle} onClick={handleOverlayClick}>
      <div style={modalContentStyle}>
        <button style={closeButtonStyle} type="button" onClick={() => onCancel && onCancel()}>&times;</button>
  <h2 style={{marginTop: 0}}>{initial ? 'Editar Artigo' : 'Criar Novo Artigo'}</h2>
        {error && <p style={{ color: '#ff6464' }}>{error}</p>}
        <form onSubmit={handleSubmit}>
          <div>
            <label>Título:</label>
            <input value={titulo} onChange={e => setTitulo(e.target.value)} required style={inputStyle} />
          </div>
          <div>
            <label>Autores (nome completo de cada um, separados por 'and'):</label>
            <input value={autores} onChange={e => setAutores(e.target.value)} required style={inputStyle} placeholder="Ex: Nome1 and Nome2 and Nome3" />
          </div>
          <div>
            <label>Nome do Evento:</label>
            <input value={nomeEvento} onChange={e => setNomeEvento(e.target.value)} required style={inputStyle} />
          </div>
          <div>
            <label>Ano:</label>
            <input type="number" value={ano} onChange={e => setAno(e.target.value)} required style={inputStyle} min={1950} />
          </div>
          <div style={{ display: 'flex', gap: '1rem' }}>
            <div style={{ flex: 1 }}>
              <label>Página Inicial:</label>
              <input type="number" value={paginaInicial} onChange={e => setPaginaInicial(e.target.value)} style={inputStyle} />
            </div>
            <div style={{ flex: 1 }}>
              <label>Página Final:</label>
              <input type="number" value={paginaFinal} onChange={e => setPaginaFinal(e.target.value)} style={inputStyle} />
            </div>
          </div>
          <div>
            <label>PDF do Artigo:</label>
            <input type="file" accept="application/pdf" onChange={e => setPdf(e.target.files[0])} style={inputStyle} />
            {initial && <span style={{ color: '#aaa', fontSize: '0.9em' }}>(Deixe em branco para manter o PDF atual)</span>}
          </div>
          <div style={{ marginTop: '1rem', display: 'flex', justifyContent: 'flex-end', gap: '10px' }}>
            <button type="button" onClick={() => onCancel && onCancel()} style={{...buttonStyle, backgroundColor: '#555'}}>Cancelar</button>
            <button type="submit" style={buttonStyle}>Salvar</button>
          </div>
        </form>
      </div>
    </div>
  );
}
