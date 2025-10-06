// src/pages/HomePage.jsx
import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { getRecentArticles, getRecentEvents, searchArticles, searchEvents } from '../services/api';

// --- Componentes de Estilo Internos para Organização ---

const cardStyle = {
  background: '#2c2c2e', // Um cinza um pouco mais claro que o fundo
  borderRadius: '8px',
  padding: '1.5rem',
  boxShadow: '0 4px 12px rgba(0, 0, 0, 0.3)',
  flex: 1,
  minWidth: '300px',
  textAlign: 'left',
};

const listHeaderStyle = {
  marginTop: 0,
  borderBottom: '2px solid #646cff',
  paddingBottom: '0.5rem',
  marginBottom: '1rem',
};

const listItemStyle = {
  listStyle: 'none',
  padding: '10px',
  borderRadius: '4px',
  transition: 'background-color 0.2s ease-in-out',
};

// --- Componente Principal ---

function HomePage() {
  const [recentArticles, setRecentArticles] = useState([]);
  const [recentEvents, setRecentEvents] = useState([]);
  const [searchResults, setSearchResults] = useState({ articles: [], events: [] });
  const [searchQuery, setSearchQuery] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchInitialData = async () => {
      setIsLoading(true);
      try {
        const [articlesRes, eventsRes] = await Promise.all([
          getRecentArticles(),
          getRecentEvents(),
        ]);
        setRecentArticles(articlesRes.data);
        setRecentEvents(eventsRes.data);
      } catch (err) {
        setError('Falha ao buscar dados recentes.');
        console.error(err);
      } finally {
        setIsLoading(false);
      }
    };
    fetchInitialData();
  }, []);

  const handleSearch = async (e) => {
    e.preventDefault();
    if (!searchQuery.trim()) {
      setSearchResults({ articles: [], events: [] });
      return;
    }
    setIsLoading(true);
    setError(null);

    try {
      // Usaremos Promise.allSettled para garantir que todas as chamadas terminem,
      // mesmo que algumas falhem. Isso é ideal para depuração.
      const promises = [
        searchArticles(searchQuery, 'titulo'),
        searchArticles(searchQuery, 'autor'),
        searchArticles(searchQuery, 'evento'),
        searchEvents(searchQuery),
      ];

      const results = await Promise.allSettled(promises);

      // Verificando se alguma das chamadas falhou
      const failedPromises = results.filter(result => result.status === 'rejected');

      if (failedPromises.length > 0) {
        // Se houver falhas, criamos uma mensagem de erro detalhada
        let detailedError = "Ocorreram erros durante a busca:\n";
        failedPromises.forEach(failure => {
          const error = failure.reason;
          const config = error.config; // Detalhes da requisição feita pelo axios
          const response = error.response; // Detalhes da resposta do servidor
          
          detailedError += `\n- URL: ${config.method.toUpperCase()} ${config.url}\n`;
          if (response) {
            detailedError += `  - Status: ${response.status} (${response.statusText})\n`;
            detailedError += `  - Detalhe do Servidor: ${JSON.stringify(response.data.detail)}\n`;
          } else {
            detailedError += `  - Erro: Não foi possível conectar ao servidor. Verifique se o backend está rodando e acessível em ${config.baseURL}.\n`;
          }
        });
        throw new Error(detailedError);
      }

      // Se todas as chamadas foram bem-sucedidas, processamos os dados
      const [
        articlesTitleRes,
        articlesAuthorRes,
        articlesEventRes,
        eventsRes
      ] = results.map(result => result.value);

      const allArticles = [
        ...articlesTitleRes.data,
        ...articlesAuthorRes.data,
        ...articlesEventRes.data,
      ];
      const uniqueArticles = allArticles.filter(
        (article, index, self) =>
          index === self.findIndex((a) => a.id === article.id)
      );

      setSearchResults({
        articles: uniqueArticles,
        events: eventsRes.data,
      });

    } catch (err) {
      // Agora, o erro exibido será muito mais informativo
      console.error("ERRO DETALHADO:", err.message);
      setError(err.message); // Exibe o erro detalhado na tela
    } finally {
      setIsLoading(false);
    }
  };

  const hasSearchResults = searchResults.articles.length > 0 || searchResults.events.length > 0;

  return (
    <div style={{ maxWidth: '1200px', margin: '0 auto' }}>
      <div style={{ textAlign: 'center', marginBottom: '2rem' }}>
        <h1>LattesCinius</h1>
        <p style={{ fontSize: '1.2rem', color: '#aaa' }}>
          Seu portal para <em style={{ fontWeight: 'bold' }}>a nata</em> da produção científica.
        </p>
      </div>

      <form onSubmit={handleSearch} style={{ display: 'flex', gap: '10px', marginBottom: '40px' }}>
        <input
          type="text"
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          placeholder="Buscar por título, autor ou nome do evento..."
          style={{
            flexGrow: 1,
            padding: '15px 20px',
            fontSize: '1.1rem',
            borderRadius: '25px',
            border: '1px solid #555',
            backgroundColor: '#333',
            color: '#fff',
          }}
        />
        <button type="submit" disabled={isLoading} style={{
          padding: '15px 30px',
          fontSize: '1.1rem',
          borderRadius: '25px',
          border: 'none',
          backgroundColor: '#646cff',
          color: '#fff',
          cursor: 'pointer',
        }}>
          {isLoading ? 'Buscando...' : 'Buscar'}
        </button>
      </form>

      {error && <p style={{ color: 'red', textAlign: 'center' }}>{error}</p>}

      <div style={{ display: 'flex', gap: '2rem', flexWrap: 'wrap' }}>
        {/* Card de Artigos */}
        <section style={{ ...cardStyle, flex: 2 }}>
          <h2 style={listHeaderStyle}>{hasSearchResults ? 'Resultados de Artigos' : 'Artigos Mais Recentes'}</h2>
          <ul style={{ padding: 0, margin: 0 }}>
            {(hasSearchResults ? searchResults.articles : recentArticles).map(article => (
              <li key={article.id || article.titulo} style={listItemStyle}
                  onMouseOver={(e) => e.currentTarget.style.backgroundColor = '#3c3c3e'}
                  onMouseOut={(e) => e.currentTarget.style.backgroundColor = 'transparent'}>
                {article.id ? (
                  <Link to={`/article/${article.id}`} style={{ textDecoration: 'none', color: 'inherit' }}>
                    <strong style={{ color: '#fff' }}>{article.titulo}</strong>
                    <p style={{ margin: '4px 0', color: '#ccc' }}>{article.ano}</p>
                  </Link>
                ) : (
                  <div>
                    <strong style={{ color: '#fff' }}>{article.titulo}</strong>
                    <p style={{ margin: '4px 0', color: '#ccc' }}>{article.ano}</p>
                  </div>
                )}
              </li>
            ))}
          </ul>
        </section>

        {/* Card de Eventos */}
        <section style={cardStyle}>
          <h2 style={listHeaderStyle}>{hasSearchResults ? 'Resultados de Eventos' : 'Eventos Recentes'}</h2>
          <ul style={{ padding: 0, margin: 0 }}>
            {(hasSearchResults ? searchResults.events : recentEvents).map(event => (
              <li key={event.id} style={listItemStyle}
                  onMouseOver={(e) => e.currentTarget.style.backgroundColor = '#3c3c3e'}
                  onMouseOut={(e) => e.currentTarget.style.backgroundColor = 'transparent'}>
                <Link to={`/events/${event.nome}`} style={{ textDecoration: 'none', color: 'inherit' }}>
                  <strong style={{ color: '#fff' }}>{event.nome}</strong>
                  <p style={{ margin: '4px 0', color: '#aaa' }}>{event.sigla ? event.sigla.toUpperCase() : ''}</p>
                </Link>
              </li>
            ))}
          </ul>
        </section>
      </div>
    </div>
  );
}

export default HomePage;