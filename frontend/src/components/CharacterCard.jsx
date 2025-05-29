// frontend/src/components/CharacterCard.jsx
import React from 'react';
import { Link } from 'react-router-dom';
import './CharacterCard.css';

const CharacterCard = ({ character, onSelectCharacter, isSelected }) => {
    const imagePath = character.icon_url;
    const elementIconPath = character.element_icon_url;

    const handleCardClick = (e) => {
        if (e.target.closest('.character-profile-link')) {
            return;
        }
        onSelectCharacter(character.id);
    };

    return (
        <div
            className={`character-card ${isSelected ? 'selected' : ''}`}
            onClick={handleCardClick}
            title={`${character.name}\nElemento: ${character.element}\nRaridade: ${character.rarity} estrelas`}
        >
            {/* Container da imagem principal do personagem (sem o ícone do elemento aqui dentro) */}
            <div className="character-image-container">
                {imagePath && (
                    <img
                        src={imagePath}
                        alt={character.name}
                        className={`character-icon rarity-${character.rarity}`}
                        onError={(e) => { e.target.style.display = 'none'; }}
                    />
                )}
            </div>

            {/* Ícone do elemento posicionado em relação ao card principal */}
            {elementIconPath && (
                <img
                    src={elementIconPath}
                    alt={character.element}
                    className="character-element-adornment" // Usaremos esta classe para o posicionamento
                    title={character.element}
                    onError={(e) => { e.target.style.display = 'none'; }}
                />
            )}

            <h3 className="character-name">{character.name}</h3>

            <Link
                to={`/character/${character.id}`}
                className="character-profile-link"
            >
                Ver Perfil
            </Link>
        </div>
    );
};

export default CharacterCard;