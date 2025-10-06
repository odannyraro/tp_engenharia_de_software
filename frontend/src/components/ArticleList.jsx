// src/components/ArticleList.jsx
import React from 'react';
import { Link } from 'react-router-dom';

function ArticleList({ articles, onEdit, onDelete }) {
  // Se não houver artigos, exibe uma mensagem
  if (!articles || articles.length === 0) {
    return <p>Nenhum artigo encontrado.</p>;
  }

  // Se houver artigos, exibe a lista
  return (
    <div style={{ textAlign: 'left', marginTop: '20px' }}>
      {articles.map((article) => (
        <div key={article.id || article.titulo} style={{ borderBottom: '1px solid #555', marginBottom: '15px', paddingBottom: '15px', display: 'flex', flexDirection: 'column' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <h3 style={{ marginTop: 0, marginRight: '1rem', wordBreak: 'break-word', maxWidth: '70%' }}>
              {article.id ? (
                <Link to={`/article/${article.id}`}>{article.titulo}</Link>
              ) : (
                article.titulo
              )}
            </h3>
            <div style={{ display: 'flex', gap: '8px' }}>
              <button style={{ background: '#3b82f6', color: '#fff', border: 'none', borderRadius: '8px', padding: '6px 14px', cursor: 'pointer', fontWeight: 600 }}
                onClick={() => onEdit && onEdit(article)}>
                Editar
              </button>
              <button style={{ background: '#ef4444', color: '#fff', border: 'none', borderRadius: '8px', padding: '6px 14px', cursor: 'pointer', fontWeight: 600 }}
                onClick={() => onDelete && onDelete(article)}>
                Deletar
              </button>
            </div>
          </div>
          <p style={{ margin: '5px 0' }}><strong>Autores:</strong> {article.autores || ''}</p>
          <p style={{ margin: '5px 0' }}><strong>Evento:</strong> {article.nome_evento} ({article.ano || 'N/A'})</p>
          {article.caminho_pdf && (
            <a href={article.caminho_pdf} target="_blank" rel="noopener noreferrer">
              Acessar PDF
            </a>
          )}
        </div>
      ))}
    </div>
  );
}

export default ArticleList;