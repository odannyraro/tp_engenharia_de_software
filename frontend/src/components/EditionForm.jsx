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

export default function EditionForm({ event, initial, onSave, onCancel }) {
  const [ano, setAno] = useState('');
  const [local, setLocal] = useState('');
  const [status, setStatus] = useState(null); // { message, type: 'success' | 'error' }
  const [loading, setLoading] = useState(false);
  const isEditing = !!initial;

  useEffect(() => {
    if (initial) {
      setAno(initial.ano || '');
      setLocal(initial.local || '');
    }
  }, [initial]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setStatus(null);
    const payload = { 
        ano: parseInt(ano), 
        local, 
        id_evento: initial ? initial.id_evento : event.id 
    };
    const result = await onSave(payload);
    setLoading(false);
    if (result.success) {
      setStatus({ message: result.message, type: 'success' });
      if (!isEditing) {
        setAno('');
        setLocal('');
      }
    } else {
      setStatus({ message: result.message, type: 'error' });
    }
  };

  // Impede que o clique dentro do formulário feche o modal
  const handleContentClick = (e) => e.stopPropagation();

  return (
    <div style={modalOverlayStyle} onClick={onCancel}>
      <div style={modalContentStyle} onClick={handleContentClick}>
        <button style={closeButtonStyle} onClick={onCancel}>&times;</button>
        
        <h2 style={{marginTop: 0}}>
            {isEditing ? `Editar Edição ${initial.ano}` : `Criar Nova Edição para ${event.nome}`}
        </h2>

        <form onSubmit={handleSubmit}>
          <div>
            <label>Ano:</label>
            <input 
              type="number"
              value={ano} 
              onChange={(e) => setAno(e.target.value)} 
              required 
              style={inputStyle} 
            />
          </div>
          <div>
            <label>Local:</label>
            <input 
              value={local} 
              onChange={(e) => setLocal(e.target.value)} 
              style={inputStyle} 
            />
          </div>

          {status && (
            <p style={{ 
              marginTop: '1rem', 
              textAlign: 'center',
              color: status.type === 'success' ? '#28a745' : '#ff6464',
              fontWeight: 'bold',
            }}>
              {status.message}
            </p>
          )}

          <div style={{ marginTop: '1rem', display: 'flex', justifyContent: 'flex-end', gap: '10px' }}>
            <button 
              type="button" 
              onClick={onCancel} 
              style={{...buttonStyle, backgroundColor: '#555'}}
            >
              Fechar
            </button>
            <button type="submit" style={buttonStyle} disabled={loading}>
              {loading ? 'Salvando...' : 'Salvar'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}