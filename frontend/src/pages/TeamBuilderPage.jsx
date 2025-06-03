// frontend/src/pages/TeamBuilderPage.jsx
import React, { useState, useEffect } from 'react';
import { getAllCharacters, getTeamSuggestions } from '../services/characterService';
import CharacterCard from '../components/CharacterCard';
import SuggestedTeamCard from '../components/SuggestedTeamCard';
import FilterBar from '../components/FilterBar';
import { useSelectedCharacters } from '../contexts/SelectedCharactersContext'; // Importar o hook
import './TeamBuilderPage.css';

const TeamBuilderPage = () => {
    const [allCharacters, setAllCharacters] = useState([]);
    const { selectedCharacterIds, toggleCharacterSelection, clearSelectedCharacters } = useSelectedCharacters(); // USAR DO CONTEXTO

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
    const [nameSearchQuery, setNameSearchQuery] = useState('');

    useEffect(() => {
        const fetchCharacters = async () => {
            setIsLoading(true);
            setError(null);
            try {
                const characters = await getAllCharacters();
                setAllCharacters(characters || []);
            } catch (err) {
                console.error("Erro no TeamBuilderPage ao buscar personagens:", err);
                setError("Falha ao carregar personagens. Verifique se o backend está rodando e acessível.");
            } finally {
                setIsLoading(false);
            }
        };
        fetchCharacters();
    }, []);

    const handleSelectCharacter = (characterId) => {
        toggleCharacterSelection(characterId);
    };

    const handleSubmitSelectedCharacters = async () => {
        if (selectedCharacterIds.size === 0) { // Usar selectedCharacterIds.size do contexto
            setSuggestionError("Por favor, selecione ao menos um personagem.");
            setSuggestedTeams([]);
            return;
        }
        setIsSuggesting(true);
        setSuggestionError(null);
        setSuggestedTeams([]);

        try {
            const teams = await getTeamSuggestions(Array.from(selectedCharacterIds)); // Usar Array.from(selectedCharacterIds) do contexto
            setSuggestedTeams(teams || []);
        } catch (err) {
            console.error("Erro ao obter sugestões de times:", err);
            setSuggestionError(err.response?.data?.error || err.message || "Falha ao buscar sugestões de times.");
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

    const handleNameSearchChange = (query) => {
        setNameSearchQuery(query);
    };

    const filteredCharacters = allCharacters.filter(character => {
        if (!character) return false;
        const { element, weapon, rarity } = activeFilters;
        if (element && character.element !== element) return false;
        if (weapon && character.weapon !== weapon) return false;
        if (rarity && character.rarity !== rarity) return false;
        if (nameSearchQuery && (!character.name || !character.name.toLowerCase().includes(nameSearchQuery.toLowerCase()))) {
            return false;
        }
        return true;
    });

    if (isLoading) return <p className="loading-message">Carregando personagens...</p>;
    if (error) return <p className="error-message">{error}</p>;

    return (
        <div className="team-builder-container">
            <h1>Monte seu Time no Genshin Impact</h1>

            <FilterBar
                activeFilters={activeFilters}
                onFilterChange={handleFilterChange}
                currentNameQuery={nameSearchQuery}
                onNameQueryChange={handleNameSearchChange}
            />

            <p className="character-count-display">
                Exibindo {filteredCharacters.length} de {allCharacters.length} personagens.
                Selecionados: {selectedCharacterIds.size} {/* Usar selectedCharacterIds.size do contexto */}
            </p>
            <div className="character-grid">
                {filteredCharacters.length > 0 ? (
                    filteredCharacters.map(character => (
                        character && character.id ? (
                            <CharacterCard
                                key={character.id}
                                character={character}
                                onSelectCharacter={handleSelectCharacter}
                                isSelected={selectedCharacterIds.has(character.id)} // Usar selectedCharacterIds.has do contexto
                            />
                        ) : null
                    ))
                ) : (
                    allCharacters.length > 0 && <p className="info-message">Nenhum personagem corresponde aos filtros selecionados.</p>
                )}
                {!isLoading && allCharacters.length === 0 && !error && (
                    <p className="info-message">Nenhum personagem encontrado no servidor.</p>
                )}
            </div>

            {allCharacters.length > 0 && (
                <div className="actions-container">
                    <button
                        onClick={handleSubmitSelectedCharacters}
                        className="submit-button"
                        disabled={isSuggesting || selectedCharacterIds.size === 0} // Usar selectedCharacterIds.size do contexto
                    >
                        {isSuggesting ? 'Sugerindo...' : 'Sugerir Times'}
                    </button>
                    {selectedCharacterIds.size > 0 && ( // Usar selectedCharacterIds.size do contexto
                        <button onClick={clearSelectedCharacters} className="clear-button">
                            Limpar Seleção
                        </button>
                    )}
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
                    <div className="suggested-teams-grid">
                        {suggestedTeams.map((team, index) => (
                            team ? (
                                <SuggestedTeamCard key={team.name || `team-${index}`} team={team} />
                            ) : null
                        ))}
                    </div>
                </div>
            )}
        </div>
    );
};

export default TeamBuilderPage;