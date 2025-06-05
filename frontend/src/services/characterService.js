import api from './api'; // <-- Importe a instância 'api' que configuramos



export const getAllCharacters = async () => {
    try {
        // Use a instância 'api' importada, que já tem a baseURL definida
        const response = await api.get('/characters'); // <-- Use 'api' diretamente
        return response.data;
    } catch (error) {
        console.error("Erro ao buscar personagens:", error);
        throw error; // Lançar o erro para o componente tratar
    }
};

export const getTeamSuggestions = async (ownedCharacterIds) => {
    try {
        // Use a instância 'api' importada
        const response = await api.post('/suggest-team', { // <-- Use 'api' diretamente
            owned_characters: ownedCharacterIds
        });
        return response.data;
    } catch (error) {
        console.error("Erro ao buscar sugestões de times:", error);
        if (error.response && error.response.data) {
            throw error.response.data;
        }
        throw error; // Lançar o erro para o componente tratar
    }
};