import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { getEventEdition } from '../services/api';

function EditionPage() {
  const { eventName, year } = useParams();
  const [edition, setEdition] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchEdition = async () => {
      console.log(`Fetching edition for: ${eventName}, ${year}`);
      setIsLoading(true);
      setError(null);
      try {
        const res = await getEventEdition(eventName, year);
        console.log("API Response:", res);
        setEdition(res.data);
        console.log("Edition state set:", res.data);
      } catch (err) {
        setError('Falha ao buscar a edição.');
        console.error("API Error:", err);
        console.log("Error response:", err.response);
      } finally {
        setIsLoading(false);
        console.log("Finished fetching.");
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
    <div style={{ fontFamily: 'Arial, sans-serif', margin: '0 auto', maxWidth: '800px', padding: '20px' }}>
      <h1>{edition.evento_nome} - {edition.ano}</h1>
      <h2>Artigos</h2>
      <ul>
        {edition.artigos.map(article => (
          <li key={article.id}>
            <h3>{article.titulo}</h3>
            <p><strong>Autores:</strong> {article.autores.join(', ')}</p>
            <p><strong>Resumo:</strong> {article.resumo}</p>
          </li>
        ))}
      </ul>
    </div>
  );
}

export default EditionPage;