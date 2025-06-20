// frontend/src/pages/TierListPage.jsx
import React, { useState, useEffect } from 'react';
import { getTierList } from '../services/tierListService';
import CharacterTooltip from '../components/CharacterTooltip'; // Componente Tooltip
import './TierListPage.css';

const TierListPage = () => {
    const [tierListData, setTierListData] = useState([]);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        const fetchTierList = async () => {
            setIsLoading(true);
            setError(null);
            try {
                const data = await getTierList();
                const tierOrder = { "SS": 5, "S": 4, "A": 3, "B": 2, "C": 1, "D": 0 };
                const sortedData = data.sort((a, b) => {
                    const tierCompare = tierOrder[b.tier_level] - tierOrder[a.tier_level];
                    if (tierCompare !== 0) {
                        return tierCompare;
                    }
                    return a.character_name.localeCompare(b.character_name);
                });
                setTierListData(sortedData);
            } catch (err) {
                console.error("Erro ao carregar a Tier List:", err);
                setError("Falha ao carregar a Tier List. Verifique o backend e tente novamente.");
            } finally {
                setIsLoading(false);
            }
        };

        fetchTierList();
    }, []);

    if (isLoading) {
        return <div className="tierlist-loading">Carregando Tier List...</div>;
    }

    if (error) {
        return <div className="tierlist-error">Erro: {error}</div>;
    }

    const groupedByTier = tierListData.reduce((acc, char) => {
        if (!acc[char.tier_level]) {
            acc[char.tier_level] = [];
        }
        acc[char.tier_level].push(char);
        return acc;
    }, {});

    const tierOrderDisplay = ["SS", "S", "A", "B", "C", "D"];

    return (
        <div className="tierlist-page-container">
            <h1>Genshin Impact Tier List Consolidada</h1>
            <p className="tierlist-description">
                Esta Tier List é uma consolidação de dados de múltiplos sites populares de Genshin Impact,
                oferecendo uma visão abrangente do desempenho dos personagens.
            </p>

            {tierOrderDisplay.map(tier => (
                groupedByTier[tier] && groupedByTier[tier].length > 0 && (
                    <div key={tier} className={`tier-section tier-${tier.toLowerCase()}`}>
                        <h2 className="tier-level-title">Tier {tier}</h2>
                        <div className="tier-characters-grid">
                            {groupedByTier[tier].map(char => (
                                <div key={char.character_id} className={`tier-character-card rarity-${char.rarity}`}>
                                    <div className="card-header">
                                        <img
                                            src={`/assets/images/characters/${char.character_id}.png`}
                                            alt={char.character_name}
                                            className="tier-character-image"
                                            onError={(e) => { e.target.onerror = null; e.target.src = '/assets/images/characters/unknown_character.png'; }}
                                        />
                                        {char.element && char.element !== "Unknown" && ( /* Ícone de Elemento */
                                            <img
                                                src={`/assets/images/elements/element_${char.element.toLowerCase()}.png`}
                                                alt={char.element}
                                                className="tier-character-element-icon"
                                            />
                                        )}
                                    </div>
                                    <div className="card-body">
                                        <h3 className="character-name">{char.character_name}</h3>
                                    </div>
                                    <CharacterTooltip
                                        originalScoresBySite={char.original_scores_by_site}
                                        characterName={char.character_name}
                                        characterRole={char.role}
                                        characterElement={char.element}
                                        characterRarity={char.rarity}
                                        averageNumericTier={char.average_numeric_tier} // <-- AGORA PASSANDO ESTA PROP
                                        sourcesContributing={char.sources_contributing} // <-- AGORA PASSANDO ESTA PROP
                                    />
                                </div>
                            ))}
                        </div>
                    </div>
                )
            ))}
            {tierListData.length === 0 && !isLoading && !error && (
                <p className="no-data-message">Nenhum dado de Tier List disponível. Tente rodar o orquestrador no backend.</p>
            )}
        </div>
    );
};

export default TierListPage;