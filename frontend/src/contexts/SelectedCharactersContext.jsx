// frontend/src/contexts/SelectedCharactersContext.jsx
import React, { createContext, useState, useEffect, useContext } from 'react';

const SelectedCharactersContext = createContext();

export const SelectedCharactersProvider = ({ children }) => {
    const [selectedCharacterIds, setSelectedCharacterIds] = useState(() => {
        // Tenta carregar os IDs dos personagens salvos do localStorage ao iniciar
        const savedCharacterIds = localStorage.getItem('selectedCharacterIds');
        try {
            return savedCharacterIds ? new Set(JSON.parse(savedCharacterIds)) : new Set();
        } catch (error) {
            console.error("Erro ao parsear selectedCharacterIds do localStorage:", error);
            localStorage.removeItem('selectedCharacterIds'); // Remove o item corrompido
            return new Set();
        }
    });

    // Salva os IDs no localStorage sempre que o estado mudar
    useEffect(() => {
        localStorage.setItem('selectedCharacterIds', JSON.stringify(Array.from(selectedCharacterIds)));
    }, [selectedCharacterIds]);

    // Função para adicionar ou remover um ID de personagem do Set
    const toggleCharacterSelection = (characterId) => {
        setSelectedCharacterIds(prevSelectedIds => {
            const newSelectedIds = new Set(prevSelectedIds);
            if (newSelectedIds.has(characterId)) {
                newSelectedIds.delete(characterId);
            } else {
                // Opcional: Adicionar lógica de limite de seleção aqui, se necessário
                // if (newSelectedIds.size < 4) { // Exemplo de limite de 4 personagens
                newSelectedIds.add(characterId);
                // }
            }
            return newSelectedIds;
        });
    };

    // Função para limpar todos os personagens selecionados
    const clearSelectedCharacters = () => {
        setSelectedCharacterIds(new Set());
    };

    return (
        <SelectedCharactersContext.Provider value={{ selectedCharacterIds, toggleCharacterSelection, clearSelectedCharacters }}>
            {children}
        </SelectedCharactersContext.Provider>
    );
};

export const useSelectedCharacters = () => {
    const context = useContext(SelectedCharactersContext);
    if (context === undefined) {
        throw new Error('useSelectedCharacters must be used within a SelectedCharactersProvider');
    }
    return context;
};