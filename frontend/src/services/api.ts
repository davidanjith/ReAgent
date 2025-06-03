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
export const getPaper = (id: string) => api.get(`/papers/${id}`);
export const createPaper = (paper: any) => api.post('/papers', paper);
export const updatePaper = (id: string, paper: any) => api.put(`/papers/${id}`, paper);
export const deletePaper = (id: string) => api.delete(`/papers/${id}`);
export const searchPapers = (query: string) => api.get(`/papers/search/${query}`);

// Chat endpoints
export const getChats = () => api.get('/chats');
export const getChat = (id: string) => api.get(`/chats/${id}`);
export const createChat = (chat: any) => api.post('/chats', chat);
export const updateChat = (id: string, chat: any) => api.put(`/chats/${id}`, chat);
export const deleteChat = (id: string) => api.delete(`/chats/${id}`);
export const addMessage = (chatId: string, content: string, paperId?: string) => 
    api.post(`/chats/${chatId}/messages`, { content, paper_id: paperId });

// Cluster endpoints
export const getClusters = () => api.get('/clusters');
export const getCluster = (id: string) => api.get(`/clusters/${id}`);
export const createCluster = (cluster: any) => api.post('/clusters', cluster);
export const updateCluster = (id: string, cluster: any) => api.put(`/clusters/${id}`, cluster);
export const deleteCluster = (id: string) => api.delete(`/clusters/${id}`);

// Error handling
api.interceptors.response.use(
    (response) => response,
    (error) => {
        console.error('API Error:', error.response?.data || error.message);
        return Promise.reject(error);
    }
);

export default api; 