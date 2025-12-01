import axios from 'axios'

const API_BASE = 'http://127.0.0.1:8000/api'

const api = axios.create({
    baseURL: API_BASE,
    headers: {
        'Content-Type': 'application/json'
    }
})

export const chatAPI = {
    sendMessage: (data) => api.post('/chat', data),
    getConversations: () => api.get('/conversations'),
    getConversation: (id) => api.get(`/conversation/${id}`),
    createConversation: (data) => api.post('/conversation', data),
    deleteConversation: (id) => api.delete(`/conversation/${id}`),
    updateConversation: (id, data) => api.put(`/conversation/${id}`, data),
    getStats: () => api.get('/stats'),
    health: () => api.get('/health')
}

export default api
