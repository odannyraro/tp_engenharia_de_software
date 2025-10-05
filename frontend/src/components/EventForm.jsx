import React, { useState, useEffect } from 'react';

// --- Estilos para o Modal ---

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

// --- Componente do Formulário ---

export default function EventForm({ initial, onSave, onCancel }) {
  const [nome, setNome] = useState('');
  const [sigla, setSigla] = useState('');
  const [entidade, setEntidade] = useState('');

  useEffect(() => {
    setNome(initial?.nome || '');
    setSigla(initial?.sigla || '');
    setEntidade(initial?.entidade_promotora || 'Sociedade Brasileira de Computação');
  }, [initial]);

  const handleSubmit = (e) => {
    e.preventDefault();
    onSave({ nome, sigla, entidade_promotora: entidade });
  };

  // Impede que o clique dentro do formulário feche o modal
  const handleContentClick = (e) => e.stopPropagation();

  return (
    <div style={modalOverlayStyle} onClick={onCancel}>
      <div style={modalContentStyle} onClick={handleContentClick}>
        <button style={closeButtonStyle} onClick={onCancel}>&times;</button>
        
        <h2 style={{marginTop: 0}}>{initial ? 'Editar Evento' : 'Criar Novo Evento'}</h2>

        <form onSubmit={handleSubmit}>
          <div>
            <label>Nome:</label>
            <input 
              value={nome} 
              onChange={(e) => setNome(e.target.value)} 
              required 
              style={inputStyle} 
            />
          </div>
          <div>
            <label>Sigla:</label>
            <input 
              value={sigla} 
              onChange={(e) => setSigla(e.target.value)} 
              style={inputStyle} 
            />
          </div>
          <div>
            <label>Entidade promotora:</label>
            <input 
              value={entidade} 
              onChange={(e) => setEntidade(e.target.value)} 
              style={inputStyle} 
            />
          </div>
          <div style={{ marginTop: '1rem', display: 'flex', justifyContent: 'flex-end', gap: '10px' }}>
            <button 
              type="button" 
              onClick={onCancel} 
              style={{...buttonStyle, backgroundColor: '#555'}}
            >
              Cancelar
            </button>
            <button type="submit" style={buttonStyle}>
              Salvar
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}