import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api';

const api = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

// Paper endpoints
export const getPapers = () => api.get('/papers');
export const getPaper = (id) => api.get(`/papers/${id}`);
export const createPaper = (paper) => api.post('/papers', paper);
export const updatePaper = (id, paper) => api.put(`/papers/${id}`, paper);
export const deletePaper = (id) => api.delete(`/papers/${id}`);
export const searchPapers = (query) => api.post('/search', { query });

// Chat endpoints
export const getChats = () => api.get('/chats');
export const getChat = (id) => api.get(`/chats/${id}`);
export const createChat = (chat) => api.post('/chats', chat);
export const updateChat = (id, chat) => api.put(`/chats/${id}`, chat);
export const deleteChat = (id) => api.delete(`/chats/${id}`);
export const addMessage = (chatId, content, paperId) => 
    api.post(`/chats/${chatId}/messages`, { content, paper_id: paperId });

// Cluster endpoints
export const getClusters = () => api.get('/clusters');
export const getCluster = (id) => api.get(`/clusters/${id}`);
export const createCluster = (data) => api.post('/clusters', data);
export const updateCluster = (id, data) => api.put(`/clusters/${id}`, data);
export const deleteCluster = (id) => api.delete(`/clusters/${id}`);

// Paper-specific endpoints
export const askQuestion = (paperId, question) => 
    api.post(`/papers/${paperId}/ask`, { question });
export const getPaperChatHistory = (paperId) => 
    api.get(`/papers/${paperId}/chat-history`);
export const getPaperClusters = (paperId) => 
    api.get(`/papers/${paperId}/clusters`);
export const processPaper = (paperId) => 
    api.post(`/papers/${paperId}/process`);

// Error handling interceptor
api.interceptors.response.use(
    (response) => response,
    (error) => {
        console.error('API Error:', error);
        return Promise.reject(error);
    }
);

export default api; 