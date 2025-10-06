import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import * as api from '../services/api';

function ArticleDetail() {
  const { id } = useParams();
  const [article, setArticle] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!id) return;
    api.get(`/artigo/${id}`)
      .then(res => setArticle(res.data))
      .catch(err => {
        console.error(err);
        setError(err?.response?.data?.detail || 'Erro ao buscar artigo');
      });
  }, [id]);

  if (error) return <p style={{ color: 'red' }}>{error}</p>;
  if (!article) return <p>Carregando...</p>;

  return (
    <div style={{ maxWidth: 800, margin: '0 auto', padding: 20, textAlign: 'left' }}>
      <h1>{article.titulo}</h1>
      <p><strong>Autores:</strong> {article.autores}</p>
      <p><strong>Evento:</strong> {article.nome_evento} ({article.ano || 'N/A'})</p>
      {article.booktitle && <p><strong>Booktitle:</strong> {article.booktitle}</p>}
      {article.publisher && <p><strong>Publisher:</strong> {article.publisher}</p>}
      {article.location && <p><strong>Location:</strong> {article.location}</p>}
      {article.pagina_inicial != null && <p><strong>Páginas:</strong> {article.pagina_inicial} - {article.pagina_final}</p>}
      {article.caminho_pdf && (
        <p><a href={article.caminho_pdf} target="_blank" rel="noopener noreferrer">Abrir PDF</a></p>
      )}
    </div>
  );
}

export default ArticleDetail;
