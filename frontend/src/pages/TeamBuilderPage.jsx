// frontend/src/pages/TeamBuilderPage.jsx
import React, { useState, useEffect } from 'react';
import { getAllCharacters, getTeamSuggestions } from '../services/characterService';
import CharacterCard from '../components/CharacterCard';
import SuggestedTeamCard from '../components/SuggestedTeamCard';
import FilterBar from '../components/FilterBar';
import './TeamBuilderPage.css';

const TeamBuilderPage = () => {
    const [allCharacters, setAllCharacters] = useState([]);
    const [selectedCharacters, setSelectedCharacters] = useState(new Set());
    const [isLoading, setIsLoading] = useState(true);
    const [isSuggesting, setIsSuggesting] = useState(false);
    const [error, setError] = useState(null);
    const [suggestedTeams, setSuggestedTeams] = useState([]);
    const [suggestionError, setSuggestionError] = useState(null);

    const [activeFilters, setActiveFilters] = useState({
        element: null,
        weapon: null,
        rarity: null,
    });

    // NOVO ESTADO para a busca por nome
    const [nameSearchQuery, setNameSearchQuery] = useState('');

    useEffect(() => {
        const fetchCharacters = async () => {
            setIsLoading(true);
            setError(null);
            try {
                const characters = await getAllCharacters();
                setAllCharacters(characters);
            } catch (err) {
                console.error("Erro no TeamBuilderPage ao buscar personagens:", err);
                setError("Falha ao carregar personagens. O backend está rodando e acessível?");
            } finally {
                setIsLoading(false);
            }
        };
        fetchCharacters();
    }, []);

    const handleSelectCharacter = (characterId) => {
        setSelectedCharacters(prevSelected => {
            const newSelected = new Set(prevSelected);
            if (newSelected.has(characterId)) {
                newSelected.delete(characterId);
            } else {
                newSelected.add(characterId);
            }
            return newSelected;
        });
    };

    const handleSubmitSelectedCharacters = async () => {
        // ... (lógica existente, sem alterações aqui)
        if (selectedCharacters.size === 0) {
            setSuggestionError("Por favor, selecione ao menos um personagem.");
            setSuggestedTeams([]);
            return;
        }
        setIsSuggesting(true);
        setSuggestionError(null);
        setSuggestedTeams([]);

        try {
            const teams = await getTeamSuggestions(Array.from(selectedCharacters));
            setSuggestedTeams(teams);
        } catch (err) {
            console.error("Erro ao obter sugestões de times:", err);
            setSuggestionError(err.error || err.message || "Falha ao buscar sugestões de times. Tente novamente.");
            setSuggestedTeams([]);
        } finally {
            setIsSuggesting(false);
        }
    };

    const handleFilterChange = (filterType, value) => {
        setActiveFilters(prevFilters => {
            const newFilterValue = prevFilters[filterType] === value ? null : value;
            return { ...prevFilters, [filterType]: newFilterValue };
        });
    };

    // ATUALIZAR LÓGICA DE FILTRAGEM para incluir a busca por nome
    const filteredCharacters = allCharacters.filter(character => {
        const { element, weapon, rarity } = activeFilters;
        if (element && character.element !== element) {
            return false;
        }
        if (weapon && character.weapon !== weapon) {
            return false;
        }
        if (rarity && character.rarity !== rarity) {
            return false;
        }
        // Adiciona o filtro por nome (case-insensitive)
        if (nameSearchQuery && !character.name.toLowerCase().includes(nameSearchQuery.toLowerCase())) {
            return false;
        }
        return true;
    });

    if (isLoading) {
        return <p className="loading-message">Carregando personagens...</p>;
    }

    if (error) {
        return <p className="error-message">{error}</p>;
    }

    return (
        <div className="team-builder-container">
            <h1>Monte seu Time no Genshin Impact</h1>

            <FilterBar
                activeFilters={activeFilters}
                onFilterChange={handleFilterChange}
            />

            {/* NOVO CAMPO DE INPUT PARA BUSCA POR NOME */}
            <div className="name-search-container">
                <input
                    type="text"
                    placeholder="Buscar personagem pelo nome..."
                    className="name-search-input"
                    value={nameSearchQuery}
                    onChange={(e) => setNameSearchQuery(e.target.value)} // Atualiza o estado da busca
                />
            </div>

            <p>Selecione os personagens que você possui ({filteredCharacters.length} exibidos de {allCharacters.length} no total):</p>
            <div className="character-grid">
                {/* ... (renderização dos CharacterCard usando filteredCharacters, sem alterações aqui) ... */}
                {filteredCharacters.length > 0 ? (
                    filteredCharacters.map(character => (
                        <CharacterCard
                            key={character.id}
                            character={character}
                            onSelectCharacter={handleSelectCharacter}
                            isSelected={selectedCharacters.has(character.id)}
                        />
                    ))
                ) : (
                    allCharacters.length > 0 && <p>Nenhum personagem corresponde aos filtros selecionados.</p>
                )}
                {!isLoading && allCharacters.length === 0 && <p>Nenhum personagem encontrado no servidor.</p>}
            </div>

            {/* ... (resto do JSX para botão de sugestão e exibição de times, sem alterações aqui) ... */}
            {allCharacters.length > 0 && (
                <div className="actions-container">
                    <button
                        onClick={handleSubmitSelectedCharacters}
                        className="submit-button"
                        disabled={isSuggesting || selectedCharacters.size === 0} // Desabilitar se não houver personagens selecionados
                    >
                        {isSuggesting ? 'Sugerindo...' : 'Sugerir Times'}
                    </button>
                    <p>Selecionados: {selectedCharacters.size}</p>
                </div>
            )}

            {suggestionError && (
                <div className="suggestion-error-container">
                    <p className="error-message">{suggestionError}</p>
                </div>
            )}

            {!isSuggesting && suggestedTeams.length > 0 && (
                <div className="suggested-teams-container">
                    <h2>Times Sugeridos:</h2>
                    {suggestedTeams.map((team, index) => (
                        <SuggestedTeamCard key={team.name || index} team={team} />
                    ))}
                </div>
            )}
        </div>
    );
};

export default TeamBuilderPage;