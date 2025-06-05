// frontend/src/services/api.js
import axios from 'axios';

// Crie uma instância do Axios para suas requisições de API
const api = axios.create({
    baseURL: 'http://localhost:3000/api', // <-- CORREÇÃO AQUI! Aponta para o Nginx do frontend + /api
    withCredentials: true, // Essencial para que os cookies de sessão sejam enviados com as requisições
});

let csrfToken = null; // Variável para armazenar o token CSRF

// Função para buscar o token CSRF do backend
export async function fetchCsrfToken() {
    try {
        const response = await api.get('/csrf-token'); // Endpoint que criamos no backend
        csrfToken = response.data.csrf_token;
        console.log('CSRF Token fetched:', csrfToken);
        return csrfToken;
    } catch (error) {
        console.error('Error fetching CSRF token:', error);
        throw error;
    }
}

// Interceptor de requisição: Adiciona o cabeçalho X-CSRFToken a cada requisição
api.interceptors.request.use(
    (config) => {
        if (['post', 'put', 'delete', 'patch'].includes(config.method.toLowerCase())) {
            if (csrfToken) {
                config.headers['X-CSRFToken'] = csrfToken;
            } else {
                console.warn('CSRF token not available for state-changing request. Please fetch it first.');
            }
        }
        return config;
    },
    (error) => {
        return Promise.reject(error);
    }
);

// Exporte a instância do Axios configurada para uso em outros componentes
export default api;