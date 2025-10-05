import React, { useState, useEffect } from 'react';

export default function EventForm({ initial, onSave, onCancel }) {
  const [nome, setNome] = useState(initial?.nome || '');
  const [sigla, setSigla] = useState(initial?.sigla || '');
  const [entidade, setEntidade] = useState(initial?.entidade_promotora || 'Sociedade Brasileira de Computação');

  useEffect(() => {
    setNome(initial?.nome || '');
    setSigla(initial?.sigla || '');
    setEntidade(initial?.entidade_promotora || 'Sociedade Brasileira de Computação');
  }, [initial]);

  const handleSubmit = (e) => {
    e.preventDefault();
    onSave({ nome, sigla, entidade_promotora: entidade });
  };

  return (
    <form onSubmit={handleSubmit} style={{ marginBottom: 20 }}>
      <div>
        <label>Nome:</label><br />
        <input value={nome} onChange={(e) => setNome(e.target.value)} required style={{ width: '100%' }} />
      </div>
      <div>
        <label>Sigla:</label><br />
        <input value={sigla} onChange={(e) => setSigla(e.target.value)} style={{ width: '200px' }} />
      </div>
      <div>
        <label>Entidade promotora:</label><br />
        <input value={entidade} onChange={(e) => setEntidade(e.target.value)} style={{ width: '100%' }} />
      </div>
      <div style={{ marginTop: 8 }}>
        <button type="submit">Salvar</button>
        <button type="button" onClick={onCancel} style={{ marginLeft: 8 }}>Cancelar</button>
      </div>
    </form>
  );
}
