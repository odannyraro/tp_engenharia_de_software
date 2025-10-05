// src/services/api.js
import axios from 'axios';

const apiClient = axios.create({
  baseURL: 'http://localhost:8000', // Adjust the base URL to your backend's address
  headers: {
    'Content-Type': 'application/json',
  },
});

export const getRecentArticles = () => {
  return apiClient.get('/artigo/recentes');
};

export const getRecentEvents = () => {
  return apiClient.get('/evento/recentes');
};

export const searchArticles = (query) => {
  return apiClient.get(`/artigo/artigo/search?field=titulo&q=${query}`);
};

export const searchEvents = (query) => {
  return apiClient.get(`/evento/search?q=${query}`);
};

export const getEventByName = (eventName) => {
  return apiClient.get(`/evento/${eventName}`);
};

export const getEventEdition = (eventName, year) => {
  return apiClient.get(`/edicao/${eventName}/${year}`);
};