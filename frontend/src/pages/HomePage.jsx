import React, { useState, useEffect } from 'react';
import { getRecentArticles, getRecentEvents, searchArticles, searchEvents } from '../services/api';

function HomePage() {
  const [recentArticles, setRecentArticles] = useState([]);
  const [recentEvents, setRecentEvents] = useState([]);
  const [searchResults, setSearchResults] = useState({ articles: [], events: [] });
  const [searchQuery, setSearchQuery] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchInitialData = async () => {
      try {
        const articlesRes = await getRecentArticles();
        setRecentArticles(articlesRes.data);

        const eventsRes = await getRecentEvents();
        setRecentEvents(eventsRes.data);
      } catch (err) {
        setError('Falha ao buscar dados recentes.');
        console.error(err);
      }
    };

    fetchInitialData();
  }, []);

  const handleSearch = async () => {
    if (!searchQuery.trim()) {
      setSearchResults({ articles: [], events: [] });
      return;
    }

    setIsLoading(true);
    setError(null);
    try {
      const articlesRes = await searchArticles(searchQuery);
      const eventsRes = await searchEvents(searchQuery);
      setSearchResults({
        articles: articlesRes.data,
        events: eventsRes.data,
      });
    } catch (err) {
      setError('Falha ao realizar a busca.');
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div style={{ fontFamily: 'Arial, sans-serif', margin: '0 auto', maxWidth: '800px', padding: '20px' }}>
      <h1>Digital Library</h1>

      <div style={{ marginBottom: '20px' }}>
        <input
          type="text"
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          placeholder="Buscar artigos ou eventos..."
          style={{ width: '300px', padding: '8px' }}
        />
        <button onClick={handleSearch} disabled={isLoading} style={{ padding: '8px 12px', marginLeft: '10px' }}>
          {isLoading ? 'Buscando...' : 'Buscar'}
        </button>
      </div>

      {error && <p style={{ color: 'red' }}>{error}</p>}

      {searchResults.articles.length > 0 || searchResults.events.length > 0 ? (
        <div>
          <h2>Resultados da Busca</h2>
          {searchResults.articles.length > 0 && (
            <div>
              <h3>Artigos</h3>
              <ul>
                {searchResults.articles.map(article => (
                  <li key={article.id}>{article.titulo} ({article.ano})</li>
                ))}
              </ul>
            </div>
          )}
          {searchResults.events.length > 0 && (
            <div>
              <h3>Eventos</h3>
              <ul>
                {searchResults.events.map(event => (
                  <li key={event.id}>{event.nome}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      ) : (
        <div>
          <h2>Últimos Artigos Adicionados</h2>
          <ul>
            {recentArticles.map(article => (
              <li key={article.id}>{article.titulo} ({article.ano})</li>
            ))}
          </ul>

          <h2>Últimos Eventos Adicionados</h2>
          <ul>
            {recentEvents.map(event => (
              <li key={event.id}>{event.nome}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}

export default HomePage;