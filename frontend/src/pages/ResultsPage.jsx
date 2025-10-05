// src/pages/ResultsPage.jsx
import React, { useState, useEffect } from 'react';
import { useSearchParams, useParams } from 'react-router-dom';
import * as api from '../services/api';
import ArticleList from '../components/ArticleList';

function ResultsPage() {
  const [articles, setArticles] = useState([]);
  const [title, setTitle] = useState('Resultados da Busca');
  const [searchParams] = useSearchParams();
  const { eventName, authorName } = useParams();

  useEffect(() => {
    let endpoint = '';
    const query = searchParams.get('q');
    const field = searchParams.get('field');

    if (eventName) {
      setTitle(`Artigos do Evento: ${eventName.toUpperCase()}`);
      endpoint = `/artigo/artigo/search?field=evento&q=${eventName}`;
    } else if (authorName) {
      setTitle(`Artigos de: ${authorName.replace(/-/g, ' ')}`);
      endpoint = `/artigo/authors/${authorName}`;
    } else if (query && field) {
      setTitle(`Resultados para "${query}" em "${field}"`);
      endpoint = `/artigo/artigo/search?field=${field}&q=${query}`;
    }

    if (endpoint) {
      api.get(endpoint)
        .then(response => {
          if (authorName) {
            // O endpoint de autor tem uma estrutura de resposta diferente
            const allArticles = response.data.articles_by_year.flatMap(yearGroup => yearGroup.articles);
            setArticles(allArticles);
          } else {
            setArticles(response.data);
          }
        })
        .catch(error => {
          console.error("Erro ao buscar artigos:", error);
          setArticles([]);
        });
    }
  }, [searchParams, eventName, authorName]);

  return (
    <div>
      <h1>{title}</h1>
      <ArticleList articles={articles} />
    </div>
  );
}

export default ResultsPage;