import React, { useState } from 'react';

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
  maxHeight: '90vh',
  overflowY: 'auto',
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
  padding: '12px 24px',
  fontSize: '1rem',
  borderRadius: '20px',
  border: 'none',
  backgroundColor: '#646cff',
  color: '#fff',
  cursor: 'pointer',
  transition: 'background-color 0.15s',
  fontWeight: 600,
};


export default function ImportArticlesForm({ onImport, onCancel }) {
  const [bibtexFile, setBibtexFile] = useState(null);
  const [zipFile, setZipFile] = useState(null);
  const [error, setError] = useState(null);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [showClose, setShowClose] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    setResult(null);
    setShowClose(false);
    if (!bibtexFile || !zipFile) {
      setError('Selecione ambos os arquivos: BibTeX e ZIP de PDFs.');
      return;
    }
    const formData = new FormData();
    formData.append('bibtex_file', bibtexFile);
    formData.append('pdf_zip_file', zipFile);
    setLoading(true);
    try {
      const res = await fetch('http://localhost:8000/artigo/artigo/importar-bibtex', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        },
        body: formData
      });
      let data = null;
      try {
        data = await res.json();
      } catch (jsonErr) {
        // Se não for JSON, pega texto bruto
        const raw = await res.text();
        data = { mensagem: 'Resposta não é JSON', raw };
      }
      console.log('Resposta do backend:', data);
      setResult(data);
      setShowClose(true);
      if (onImport) onImport(data);
    } catch (err) {
      setError('Erro ao importar artigos.');
    } finally {
      setLoading(false);
    }
  };

  const handleOverlayClick = (e) => {
    if (e.target === e.currentTarget && onCancel) {
      onCancel();
    }
  };

  return (
    <div style={modalOverlayStyle} onClick={handleOverlayClick}>
      <div style={modalContentStyle}>
        <button style={closeButtonStyle} type="button" onClick={() => onCancel && onCancel()}>&times;</button>
        <h2 style={{marginTop: 0}}>Importar Pacote de Artigos</h2>
        {!result ? (
          <form onSubmit={handleSubmit}>
            <div>
              <label>Arquivo BibTeX (.bib):</label>
              <input type="file" accept=".bib,text/plain" onChange={e => setBibtexFile(e.target.files[0])} required style={inputStyle} />
            </div>
            <div>
              <label>Arquivo ZIP com PDFs:</label>
              <input type="file" accept=".zip,application/zip" onChange={e => setZipFile(e.target.files[0])} required style={inputStyle} />
            </div>
            <div style={{ marginTop: '1rem', display: 'flex', justifyContent: 'flex-end', gap: '10px' }}>
              <button type="button" onClick={() => onCancel && onCancel()} style={{...buttonStyle, backgroundColor: '#555'}}>Cancelar</button>
              <button type="submit" style={buttonStyle} disabled={loading}>{loading ? 'Importando...' : 'Importar'}</button>
            </div>
          </form>
        ) : (
          <div style={{ marginTop: '2rem', background: '#222', borderRadius: '8px', padding: '1rem' }}>
            <h3>Resumo da Importação</h3>
            <div style={{ marginBottom: '1.5rem' }}>
              <strong style={{ fontSize: '1.1em' }}>Artigos cadastrados ({result.total_cadastrados}):</strong>
              {result.titulos_cadastrados && result.titulos_cadastrados.length > 0 ? (
                <div style={{ marginTop: '0.5rem', display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                  {result.titulos_cadastrados.map((t, i) => (
                    <div key={i} style={{ background: '#223', borderRadius: 6, padding: '0.5rem 1rem', color: '#2ea44f', fontWeight: 'bold' }}>{t}</div>
                  ))}
                </div>
              ) : (
                <p style={{ color: '#aaa', marginTop: '0.5rem' }}>Nenhum artigo foi cadastrado.</p>
              )}
            </div>
            <div style={{ marginBottom: '1.5rem' }}>
              <strong style={{ fontSize: '1.1em' }}>Artigos pulados ({result.total_pulados}):</strong>
              {result.relatorio_erros && result.relatorio_erros.length > 0 ? (
                <div style={{ marginTop: '0.5rem', display: 'flex', flexDirection: 'column', gap: '0.7rem' }}>
                  {result.relatorio_erros.map((msg, i) => (
                    <div key={i} style={{ background: '#331a1a', borderRadius: 6, padding: '0.7rem 1rem' }}>
                      <div style={{ color: '#ff6464', fontWeight: 'bold', fontSize: '1em' }}>
                        {typeof msg === 'string' ? msg : (msg.titulo || msg.identificador || 'Artigo desconhecido')}
                      </div>
                      {typeof msg !== 'string' && msg.motivo && (
                        <div style={{ color: '#ffb3b3', marginTop: 4, fontSize: '0.98em' }}>
                          {msg.motivo}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              ) : (
                <p style={{ color: '#aaa', marginTop: '0.5rem' }}>Nenhum artigo foi pulado.</p>
              )}
            </div>
            <div style={{ marginBottom: '1rem' }}>
              <strong>Mensagem final:</strong>
              <p style={{ color: '#fff', marginTop: '0.5rem' }}>{result.mensagem}</p>
            </div>
            {showClose && (
              <button style={{...buttonStyle, marginTop: '1rem'}} onClick={() => onCancel && onCancel()}>Fechar</button>
            )}
          </div>
        )}
        {error && <p style={{ color: '#ff6464' }}>{error}</p>}
      </div>
    </div>
  );
}
