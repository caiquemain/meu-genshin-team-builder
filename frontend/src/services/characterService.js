// frontend/src/services/characterService.js
import axios from 'axios';

const API_URL = 'http://127.0.0.1:5000/api';

export const getAllCharacters = async () => {
    try {
        const response = await axios.get(`${API_URL}/characters`);
        return response.data;
    } catch (error) {
        console.error("Erro ao buscar personagens:", error);
        throw error; // Lançar o erro para o componente tratar
    }
};

export const getTeamSuggestions = async (ownedCharacterIds) => {
    try {
        // O backend espera um objeto com a chave 'owned_characters'
        const response = await axios.post(`${API_URL}/suggest-team`, {
            owned_characters: ownedCharacterIds
        });
        return response.data;
    } catch (error) {
        console.error("Erro ao buscar sugestões de times:", error);
        // Se o backend retornar um erro JSON (ex: 400), error.response.data pode contê-lo
        if (error.response && error.response.data) {
            throw error.response.data;
        }
        throw error; // Lançar o erro para o componente tratar
    }
};