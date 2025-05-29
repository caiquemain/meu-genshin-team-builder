// frontend/src/components/CharacterCard.jsx
import React from 'react';
import { Link } from 'react-router-dom';
import './CharacterCard.css'; // Certifique-se que este CSS existe e será atualizado

const CharacterCard = ({ character, onSelectCharacter, isSelected }) => {
    const imagePath = character.icon_url;
    const elementIconPath = character.element_icon_url;

    const handleCardClick = (e) => {
        // Impede que o clique no link de "Ver Perfil" também acione a seleção do card
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
            {/* NOVO: Container para a imagem principal e o ícone do elemento */}
            <div className="character-image-container">
                {imagePath && (
                    <img
                        src={imagePath}
                        alt={character.name}
                        className={`character-icon rarity-${character.rarity}`} {/* Imagem principal do personagem */}
                        onError={(e) => { e.target.style.display = 'none'; }}
                    />
                )}
                {elementIconPath && (
                    <img
                        src={elementIconPath}
                        alt={character.element}
                        className="character-element-adornment" {/* Nova classe para o ícone do elemento */}
                        title={character.element} /* Adiciona um title para o nome do elemento no hover */
                        onError={(e) => { e.target.style.display = 'none'; }}
                    />
                )}
            </div>

            <h3 className="character-name">{character.name}</h3>
            
            {/* O ícone de elemento que estava aqui antes foi movido para dentro do character-image-container */}

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