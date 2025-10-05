// src/pages/ResultsPage.jsx
import React, { useState, useEffect } from 'react';
import { useSearchParams, useParams } from 'react-router-dom';
import * as api from '../services/api';
import ArticleList from '../components/ArticleList';

function ResultsPage() {
  const [articles, setArticles] = useState([]);
  const [articlesByYear, setArticlesByYear] = useState([]);
  const [title, setTitle] = useState('Resultados da Busca');
  const [searchParams] = useSearchParams();
  const { eventName, authorName } = useParams();

  useEffect(() => {
    let endpoint = '';
    const query = searchParams.get('q');
    const field = searchParams.get('field');

    if (eventName) {
      setTitle(`Artigos do Evento: ${eventName.toUpperCase()}`);
      endpoint = `/artigo/search?field=evento&q=${eventName}`;
    } else if (authorName) {
      setTitle(`Artigos de: ${authorName.replace(/-/g, ' ')}`);
      endpoint = `/artigo/authors/${authorName}`;
    } else if (query && field) {
      setTitle(`Resultados para "${query}" em "${field}"`);
      endpoint = `/artigo/search?field=${field}&q=${query}`;
    }

    if (endpoint) {
      api.get(endpoint)
        .then(response => {
          if (authorName) {
            // Expected response: { articles_by_year: [{ year: 2023, articles: [...] }, ...] }
            const groups = response.data.articles_by_year || [];
            setArticlesByYear(groups);
            // also set flat list for compatibility
            const flat = groups.flatMap(g => g.articles || []);
            setArticles(flat);
          } else {
            setArticles(response.data);
            setArticlesByYear([]);
          }
        })
        .catch(error => {
          console.error("Erro ao buscar artigos:", error);
          setArticles([]);
          setArticlesByYear([]);
        });
    }
  }, [searchParams, eventName, authorName]);

  return (
    <div>
      <h1>{title}</h1>
      {authorName ? (
        <div style={{ textAlign: 'left' }}>
          {articlesByYear.length === 0 ? (
            <p>Nenhum artigo encontrado para este autor.</p>
          ) : (
            articlesByYear.map(group => (
              <div key={group.year} style={{ marginBottom: 20 }}>
                <h2>{group.year}</h2>
                <ArticleList articles={group.articles} />
              </div>
            ))
          )}
        </div>
      ) : (
        <ArticleList articles={articles} />
      )}
    </div>
  );
}

export default ResultsPage;