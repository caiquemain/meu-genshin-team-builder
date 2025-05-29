// frontend/src/components/ArtifactTooltip.jsx
import React from 'react';
import './ArtifactTooltip.css';

// Aceita 'artifactData' (para 4p) ou 'comboArtifactsData' (array para 2p+2p)
const ArtifactTooltip = ({ artifactData, comboArtifactsData }) => {
    if (!artifactData && (!comboArtifactsData || comboArtifactsData.length === 0)) {
        return null;
    }

    if (comboArtifactsData && comboArtifactsData.length > 0) {
        // Tooltip para combo 2p+2p
        return (
            <div className="artifact-tooltip-content">
                {comboArtifactsData.map((comboSet, index) => (
                    <div key={comboSet.id || index} className="combo-set-bonus">
                        <div className="tooltip-header">
                            {comboSet.icon_url && (
                                <img src={comboSet.icon_url} alt={comboSet.name_pt || comboSet.name} className="tooltip-artifact-icon" />
                            )}
                            <strong>{comboSet.name_pt || comboSet.name || comboSet.name}</strong>
                        </div>
                        <div className="tooltip-body">
                            {comboSet.bonus_2pc && (
                                <p><strong>2 Peças:</strong> {comboSet.bonus_2pc}</p>
                            )}
                            {/* Não mostra bônus de 4p para combos */}
                        </div>
                    </div>
                ))}
            </div>
        );
    }

    // Tooltip para conjunto único (4p ou 2p sozinho)
    return (
        <div className="artifact-tooltip-content">
            <div className="tooltip-header">
                {artifactData.icon_url && (
                    <img src={artifactData.icon_url} alt={artifactData.name_pt || artifactData.name} className="tooltip-artifact-icon" />
                )}
                <strong>{artifactData.name_pt || artifactData.name || artifactData.name}</strong>
            </div>
            <div className="tooltip-body">
                {artifactData.bonus_2pc && (
                    <p><strong>2 Peças:</strong> {artifactData.bonus_2pc}</p>
                )}
                {artifactData.bonus_4pc && (
                    <p><strong>4 Peças:</strong> {artifactData.bonus_4pc}</p>
                )}
                {artifactData.bonus_1pc && (
                    <p><strong>1 Peça:</strong> {artifactData.bonus_1pc}</p>
                )}
            </div>
        </div>
    );
};

export default ArtifactTooltip;