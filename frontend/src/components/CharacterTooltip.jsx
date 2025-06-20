// frontend/src/components/CharacterTooltip.jsx
import React from 'react';
import '../pages/TierListPage.css';

const CharacterTooltip = ({ originalScoresBySite, characterName, characterRole, characterElement, characterRarity, averageNumericTier, sourcesContributing }) => {
    const hasTierScores = originalScoresBySite && Object.keys(originalScoresBySite).length > 0;
    const hasBasicInfo = (characterRole && characterRole !== "Unknown Role") ||
        (characterElement && characterElement !== "Unknown") ||
        (characterRarity !== null && characterRarity !== undefined);

    // Mapeamento de tiers para classes de cor para a nota agregada
    const getTierClass = (numericTier) => {
        if (numericTier >= 4.5) return "score-SS";
        if (numericTier >= 3.5) return "score-S";
        if (numericTier >= 2.5) return "score-A";
        if (numericTier >= 1.5) return "score-B";
        if (numericTier >= 0.5) return "score-C";
        return "score-D";
    };

    const getTierName = (numericTier) => {
        if (numericTier >= 4.5) return "SS";
        if (numericTier >= 3.5) return "S";
        if (numericTier >= 2.5) return "A";
        if (numericTier >= 1.5) return "B";
        if (numericTier >= 0.5) return "C";
        return "D";
    };

    return (
        <div className="custom-tooltip">
            <div className="tooltip-header">{characterName}</div>

            {/* Informações básicas do personagem - Exibir se existirem */}
            {characterRole && characterRole !== "Unknown Role" && <p className="tooltip-info">Função: {characterRole}</p>}
            {characterElement && characterElement !== "Unknown" && <p className="tooltip-info">Elemento: {characterElement}</p>}
            {characterRarity && <p className="tooltip-info">Raridade: {characterRarity} Estrelas</p>}

            {/* AGORA SÓ A NOTA AGREGADA COM A COR, SEM AS FONTES */}
            {(averageNumericTier !== null && averageNumericTier !== undefined) && (
                <p className="tooltip-info">
                    Nota Agregada: <span className={getTierClass(averageNumericTier)}>{getTierName(averageNumericTier)}</span>
                </p>
            )}

            {hasTierScores && (
                <>
                    <div className="tooltip-section-title">Scores por Site:</div>

                    {Object.entries(originalScoresBySite).map(([site, tier], index) => (
                        <div key={index} className="tooltip-site-score">
                            <span>{site.replace('_', ' ')}:</span>
                            <span className={`score-${tier}`}>{tier}</span>
                        </div>
                    ))}
                </>
            )}
            {!hasTierScores && !hasBasicInfo && (averageNumericTier === null || averageNumericTier === undefined) && (
                <p className="tooltip-info">Detalhes não disponíveis.</p>
            )}
        </div>
    );
};

export default CharacterTooltip;