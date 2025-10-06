// src/components/ArticleList.jsx
import React from 'react';
import { Link } from 'react-router-dom';

function ArticleList({ articles }) {
  // Se não houver artigos, exibe uma mensagem
  if (!articles || articles.length === 0) {
    return <p>Nenhum artigo encontrado.</p>;
  }

  // Se houver artigos, exibe a lista
  return (
    <div style={{ textAlign: 'left', marginTop: '20px' }}>
      {articles.map((article) => (
        <div key={article.id || article.titulo} style={{ borderBottom: '1px solid #555', marginBottom: '15px', paddingBottom: '15px' }}>
          <h3 style={{ marginTop: 0 }}>
            {article.id ? (
              <Link to={`/article/${article.id}`}>{article.titulo}</Link>
            ) : (
              article.titulo
            )}
          </h3>
          <p style={{ margin: '5px 0' }}><strong>Autores:</strong> {article.autores}</p>
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