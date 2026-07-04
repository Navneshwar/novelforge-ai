import axios from 'axios';

const api = axios.create({
  baseURL: '/api',
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000, // 30 second timeout for AI operations
});

// Request interceptor
api.interceptors.request.use(
  (config) => {
    // Add any auth tokens here if needed
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor
api.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    if (error.response) {
      // Server responded with error
      console.error('API Error:', error.response.status, error.response.data);
      
      // Handle specific status codes
      if (error.response.status === 401) {
        console.warn('Unauthorized access');
      } else if (error.response.status === 429) {
        console.warn('Rate limit exceeded');
      }
    } else if (error.request) {
      console.error('No response from server:', error.request);
    } else {
      console.error('Request error:', error.message);
    }
    return Promise.reject(error);
  }
);

// API methods for different resources
export const novelApi = {
  getAll: () => api.get('/novels'),
  get: (id) => api.get(`/novels/${id}`),
  create: (data) => api.post('/novels', data),
  update: (id, data) => api.put(`/novels/${id}`, data),
  delete: (id) => api.delete(`/novels/${id}`),
};

export const chapterApi = {
  getAll: (novelId) => api.get(`/novels/${novelId}/chapters`),
  create: (novelId, data) => api.post(`/novels/${novelId}/chapters`, data),
  update: (novelId, chapterId, data) => api.put(`/novels/${novelId}/chapters/${chapterId}`, data),
  delete: (novelId, chapterId) => api.delete(`/novels/${novelId}/chapters/${chapterId}`),
};

export const memoryApi = {
  remember: (novelId, text, metadata) => 
    api.post(`/memory/remember/${novelId}`, { text, metadata }),
  recall: (novelId, query, limit) => 
    api.post(`/memory/recall/${novelId}`, { query, limit }),
  improve: (novelId) => 
    api.post(`/memory/improve/${novelId}`),
  forget: (novelId, itemId) => 
    api.delete(`/memory/forget/${novelId}/${itemId}`),
  stats: (novelId) => 
    api.get(`/memory/stats/${novelId}`),
  graph: (novelId) => 
    api.get(`/memory/graph/${novelId}`),
};

export const consistencyApi = {
  check: (novelId) => 
    api.post(`/consistency/check/${novelId}`),
  getIssues: (novelId) => 
    api.get(`/consistency/issues/${novelId}`),
  resolve: (novelId, issueId) => 
    api.post(`/consistency/resolve/${novelId}/${issueId}`),
};

export const characterApi = {
  getAll: (novelId) => 
    api.get(`/characters/${novelId}`),
  create: (novelId, data) => 
    api.post(`/characters/${novelId}`, data),
  update: (novelId, charId, data) => 
    api.put(`/characters/${novelId}/${charId}`, data),
  delete: (novelId, charId) => 
    api.delete(`/characters/${novelId}/${charId}`),
  generateBackstory: (novelId, charId) =>
    api.post(`/characters/${novelId}/${charId}/generate-backstory`),
  addRelationship: (novelId, charId, data) =>
    api.post(`/characters/${novelId}/${charId}/relationships`, data),
  getRelationships: (novelId, charId) =>
    api.get(`/characters/${novelId}/${charId}/relationships`),
};

export const plotApi = {
  getAll: (novelId) =>
    api.get(`/plots/${novelId}`),
  create: (novelId, data) =>
    api.post(`/plots/${novelId}`, data),
  update: (novelId, plotId, data) =>
    api.put(`/plots/${novelId}/${plotId}`, data),
  delete: (novelId, plotId) =>
    api.delete(`/plots/${novelId}/${plotId}`),
  getArcs: (novelId) =>
    api.get(`/plots/${novelId}/arcs`),
  createArc: (novelId, data) =>
    api.post(`/plots/${novelId}/arcs`, data),
};

export const worldBuildingApi = {
  getAll: (novelId, category) =>
    api.get(`/world/${novelId}`, { params: category ? { category } : {} }),
  create: (novelId, data) =>
    api.post(`/world/${novelId}`, data),
  update: (novelId, elementId, data) =>
    api.put(`/world/${novelId}/${elementId}`, data),
  delete: (novelId, elementId) =>
    api.delete(`/world/${novelId}/${elementId}`),
};

export default api;