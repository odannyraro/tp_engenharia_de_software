// src/App.jsx
import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Header from './components/Header';
import HomePage from './pages/HomePage';
import ResultsPage from './pages/ResultsPage';
import SubscribePage from './pages/SubscribePage';
import AdminPage from './pages/AdminPage';

function App() {
  return (
    <Router>
      <Header />
      <main>
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/subscribe" element={<SubscribePage />} />
          <Route path="/admin" element={<AdminPage />} />
          {/* Rotas dinâmicas para resultados */}
          <Route path="/search" element={<ResultsPage />} />
          <Route path="/events/:eventName" element={<ResultsPage />} />
          <Route path="/authors/:authorName" element={<ResultsPage />} />
        </Routes>
      </main>
    </Router>
  );
}

export default App;