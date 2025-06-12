// frontend/src/components/CharacterCard.jsx
import React from 'react';
import { useNavigate } from 'react-router-dom';
import './CharacterCard.css';

const CharacterCard = ({ character, onSelectCharacter, isSelected }) => {
    const navigate = useNavigate();

    const handleCardClick = () => {
        if (character && character.id) {
            navigate(`/character/${character.id}`);
        }
    };

    const handleCheckboxChange = (e) => {
        e.stopPropagation(); // Impede que o clique no checkbox acione a navegação do card
        if (onSelectCharacter) {
            onSelectCharacter(character.id);
        }
    };

    const getElementIconPath = (elementName) => {
        const formattedElementName = elementName ? elementName.toLowerCase() : 'unknown';
        return `/assets/images/elements/element_${formattedElementName}.png`;
    };

    // Nao precisamos mais de getRarityIconPath aqui, pois a raridade sera via CSS no hover
    // const getRarityIconPath = (rarityNumber) => {
    //   const formattedRarityNumber = rarityNumber || 'unknown';
    //   return `/assets/images/rarity/rarity_${formattedRarityNumber}.png`;
    // };

    // Adiciona uma classe CSS baseada na raridade para o efeito de hover
    const rarityClass = character.rarity === 5 ? 'rarity-5-hover' : 'rarity-4-hover';

    return (
        <div className={`character-card ${rarityClass}`} onClick={handleCardClick}> {/* Adiciona a classe de raridade */}
            {/* Checkbox para seleção múltipla (canto superior esquerdo) */}
            <div className="character-selection-checkbox">
                <input
                    type="checkbox"
                    checked={isSelected}
                    onChange={handleCheckboxChange}
                />
            </div>

            {/* Ícone do Elemento (canto superior direito) */}
            {character.element && (
                <img
                    src={getElementIconPath(character.element)}
                    alt={character.element}
                    className="character-element-icon"
                />
            )}

            <img src={character.icon_url} alt={character.name} className="character-icon" />
            <h3>{character.name}</h3>

        </div>
    );
};

export default CharacterCard;