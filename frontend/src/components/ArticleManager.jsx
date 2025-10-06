// src/components/ArticleManager.jsx
import React, { useState } from 'react';

const cardStyle = {
  background: '#2c2c2e',
  borderRadius: '8px',
  padding: '1.5rem',
  boxShadow: '0 4px 12px rgba(0, 0, 0, 0.3)',
  marginBottom: '2rem',
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

function ArticleManager({ onAddArticle, onImportArticles }) {
  return (
    <div style={cardStyle}>
      <h2 style={{ marginTop: 0 }}>Gerenciador de Artigos</h2>
      <div style={{ display: 'flex', gap: '1rem', marginBottom: '1rem' }}>
        <button style={buttonStyle} onClick={() => onAddArticle && onAddArticle()}>Adicionar Artigo</button>
        <button style={buttonStyle} onClick={() => onImportArticles && onImportArticles()}>Importar Pacote de Artigos</button>
      </div>
    </div>
  );
}

export default ArticleManager;
