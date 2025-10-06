// src/pages/EditionPage.jsx
import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { getEventEdition } from '../services/api';
import ArticleList from '../components/ArticleList';

function EditionPage() {
  const { eventName, year } = useParams();
  const [edition, setEdition] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchEdition = async () => {
      setIsLoading(true);
      setError(null);
      try {
        const res = await getEventEdition(eventName, year);
        setEdition(res.data);
      } catch (err) {
        setError('Falha ao buscar os dados da edição.');
        console.error("API Error:", err);
      } finally {
        setIsLoading(false);
      }
    };

    fetchEdition();
  }, [eventName, year]);

  if (isLoading) {
    return <p>Carregando edição...</p>;
  }

  if (error) {
    return <p style={{ color: 'red' }}>{error}</p>;
  }

  if (!edition) {
    return <p>Nenhuma edição encontrada.</p>;
  }

  return (
    <div style={{ fontFamily: 'Arial, sans-serif', margin: '0 auto', maxWidth: '800px', padding: '20px', textAlign: 'left' }}>
      {/* Seção de Detalhes da Edição */}
      <h1>{edition.evento_nome}</h1>
      <div style={{ marginBottom: '30px', paddingBottom: '15px', borderBottom: '1px solid #ccc' }}>
        <h2>Edição de {edition.ano}</h2>
        {edition.local && <p><strong>Local:</strong> {edition.local}</p>}
      </div>

      {/* Seção de Artigos */}
      <h2>Artigos Publicados</h2>
      <ArticleList articles={edition.artigos} />
    </div>
  );
}

export default EditionPage;