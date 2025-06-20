// frontend/src/services/tierListService.js
import axios from 'axios';

const API_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:3000/api';

export const getTierList = async () => {
    try {
        const response = await axios.get(`${API_URL}/tierlist`);
        return response.data;
    } catch (error) {
        console.error('Erro ao buscar a Tier List:', error);
        throw error; // Rejeitar a promessa para que o componente possa lidar com o erro
    }
};