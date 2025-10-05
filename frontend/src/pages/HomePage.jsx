// src/pages/HomePage.jsx
import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import api from '../services/api';
import SearchBar from '../components/SearchBar'; // Importa o componente real
import ArticleList from '../components/ArticleList'; // Importa o componente real

function HomePage() {
  const [recentArticles, setRecentArticles] = useState([]);
  const [recentEvents, setRecentEvents] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let isMounted = true; 

    const fetchData = async () => {
      setLoading(true);
      try {
        const [articlesResponse, eventsResponse] = await Promise.all([
          api.get('/artigo/search?field=titulo&q='),
          api.get('/evento/list')
        ]);

        if (isMounted) {
          const sortedArticles = articlesResponse.data.sort((a, b) => (b.ano || 0) - (a.ano || 0));
          setRecentArticles(sortedArticles.slice(0, 5));

          const sortedEvents = eventsResponse.data.sort((a, b) => b.id - a.id);
          setRecentEvents(sortedEvents.slice(0, 5));
        }

      } catch (error) {
        console.error("Erro ao buscar dados para a HomePage:", error);
      } finally {
        if (isMounted) {
          setLoading(false);
        }
      }
    };

    fetchData();

    return () => {
      isMounted = false;
    };
  }, []);

  return (
    <div>
      <h1>Biblioteca Digital de Artigos</h1>
      <p>O seu portal para artigos e eventos científicos.</p>
      
      {/* Agora está usando os componentes reais importados */}
      <SearchBar />

      {loading ? (
        <p>Carregando dados...</p>
      ) : (
        <div style={{ display: 'flex', justifyContent: 'space-between', gap: '40px', marginTop: '40px' }}>
          <section style={{ flex: 2 }}>
            <h2>Artigos Mais Recentes</h2>
            <ArticleList articles={recentArticles} />
          </section>

          <section style={{ flex: 1 }}>
            <h2>Eventos Recentes</h2>
            <div style={{ textAlign: 'left' }}>
              {recentEvents.length > 0 ? (
                recentEvents.map(event => (
                  <div key={event.id} style={{ marginBottom: '10px' }}>
                    <Link to={`/events/${event.sigla.toLowerCase()}`}>
                      {event.nome} ({event.sigla.toUpperCase()})
                    </Link>
                  </div>
                ))
              ) : (
                <p>Nenhum evento para exibir.</p>
              )}
            </div>
          </section>
        </div>
      )}
    </div>
  );
}

export default HomePage;