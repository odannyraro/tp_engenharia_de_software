// src/components/SearchBar.jsx
import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';

function SearchBar() {
  const [query, setQuery] = useState('');
  const [field, setField] = useState('titulo');
  const navigate = useNavigate();

  const handleSearch = (e) => {
    e.preventDefault();
    if (query.trim()) {
      // Navega para a página de resultados com os parâmetros da busca
      navigate(`/search?field=${field}&q=${query}`);
    }
  };

  return (
    <form onSubmit={handleSearch} style={{ margin: '20px 0' }}>
      <input
        type="text"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        placeholder="Pesquisar artigos..."
        style={{ marginRight: '10px', padding: '8px', minWidth: '300px' }}
      />
      <select
        value={field}
        onChange={(e) => setField(e.target.value)}
        style={{ marginRight: '10px', padding: '8px' }}
      >
        <option value="titulo">Título</option>
        <option value="autor">Autor</option>
        <option value="evento">Evento</option>
      </select>
      <button type="submit" style={{ padding: '8px 12px' }}>
        Pesquisar
      </button>
    </form>
  );
}

export default SearchBar;