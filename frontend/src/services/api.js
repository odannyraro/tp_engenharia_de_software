// src/services/api.js
import axios from 'axios';

const apiClient = axios.create({
  baseURL: 'http://localhost:8000', // Adjust the base URL to your backend's address
  headers: {
    'Content-Type': 'application/json',
  },
});

// Helper to set auth token for subsequent requests
export function setAuthToken(token) {
  if (token) {
    apiClient.defaults.headers.common['Authorization'] = `Bearer ${token}`;
    localStorage.setItem('access_token', token);
  } else {
    delete apiClient.defaults.headers.common['Authorization'];
    localStorage.removeItem('access_token');
  }
}

// store a non-admin user token without setting axios default header
export function storeUserToken(token) {
  if (token) {
    localStorage.setItem('user_access_token', token);
  } else {
    localStorage.removeItem('user_access_token');
  }
}

// Initialize auth header from localStorage if present
const savedToken = localStorage.getItem('access_token');
if (savedToken) {
  setAuthToken(savedToken);
}

export const getRecentArticles = () => {
  return apiClient.get('/artigo/recentes');
};

// generic GET helper used by some pages
export const get = (path) => apiClient.get(path);

export const getRecentEvents = () => {
  return apiClient.get('/evento/recentes');
};

export const searchArticles = (query, field = 'titulo') => {
  return apiClient.get(`/artigo/artigo/search?field=${field}&q=${query}`);
};

export const searchEvents = (query) => {
  return apiClient.get(`/evento/search?q=${query}`);
};

export const getEventByName = (eventName) => {
  return apiClient.get(`/evento/${eventName}`);
};

export const getEventEdition = (eventName, year) => {
  return apiClient.get(`/edicao/${encodeURIComponent(eventName)}/${year}`);
};

// Event CRUD
export const listEvents = () => apiClient.get('/evento/recentes');
export const createEvent = (data) => apiClient.post('/evento', data);
export const updateEvent = (id, data) => apiClient.post(`/evento/editar/${id}`, data);
export const deleteEvent = (nome) => apiClient.post(`/evento/remover/${encodeURIComponent(nome)}`);

// --- NOVAS FUNÇÕES PARA EDIÇÕES ---
export const createEdition = (data) => apiClient.post('/evento/edicao/', data);
export const updateEdition = (id, data) => apiClient.post(`/evento/edicao/editar/${id}`, data);
export const deleteEdition = (id) => apiClient.post(`/evento/edicao/remover/${id}`);

// Auth
export const login = (payload) => apiClient.post('/auth/login', payload);
export const subscribe = (payload) => apiClient.post('/subscriber/', payload);
export const createAccount = (payload) => apiClient.post('/auth/criar_conta', payload);