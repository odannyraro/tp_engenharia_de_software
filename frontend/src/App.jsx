// src/App.jsx
import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Header from './components/Header';
import HomePage from './pages/HomePage';
import ResultsPage from './pages/ResultsPage';
import SubscribePage from './pages/SubscribePage';
import LoginPage from './pages/LoginPage';
import AdminPage from './pages/AdminPage';
import EventPage from './pages/EventPage';
import EditionPage from './pages/EditionPage';
import ArticleDetail from './pages/ArticleDetail';

function App() {
  return (
    <Router>
      <Header />
      <main>
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/signup" element={<SubscribePage />} />
          <Route path="/login" element={<LoginPage />} />
          <Route path="/admin" element={<AdminPage />} />
          <Route path="/events/:eventName" element={<EventPage />} />
          <Route path="/events/:eventName/:year" element={<EditionPage />} />
          <Route path="/article/:id" element={<ArticleDetail />} />
          {/* Rotas dinâmicas para resultados */}
          <Route path="/search" element={<ResultsPage />} />
          <Route path="/authors/:authorName" element={<ResultsPage />} />
        </Routes>
      </main>
    </Router>
  );
}

export default App;