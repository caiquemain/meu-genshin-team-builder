// frontend/src/components/SuggestedTeamCard.jsx
import React from 'react';
import { useNavigate } from 'react-router-dom'; // Importar useNavigate
import './SuggestedTeamCard.css';

const SuggestedTeamCard = ({ team }) => {
    const navigate = useNavigate(); // Hook para navegação

    if (team.error || team.message) {
        // ... (código de erro existente)
        return (
            <div className="suggested-team-card error-card">
                <h4>{team.error || "Aviso"}</h4>
                <p>{team.message || "Não foi possível gerar um time com esta combinação."}</p>
                {team.characters && team.characters.length > 0 && (
                    <div className="mini-character-list">
                        <p>Personagens selecionados:</p>
                        {/* Ajuste para pegar o nome do personagem corretamente se a estrutura de 'characters' mudou */}
                        {team.characters.map(char_in_list => (
                            <span key={char_in_list.id || char_in_list.character_id} className="mini-char-name">
                                {char_in_list.name || char_in_list.character_id /* Tente encontrar o nome */}
                            </span>
                        ))}
                    </div>
                )}
            </div>
        );
    }

    // Função para lidar com o clique no card
    const handleCardClick = () => {
        // A 'team' aqui deve ser o objeto completo da composição, incluindo 'characters_in_team'
        navigate('/team-detail', { state: { teamData: team } });
    };

    // Ajuste para pegar os personagens da nova estrutura 'characters_in_team'
    // ou da estrutura antiga 'characters' se for um time aleatório simples
    const displayCharacters = team.characters_in_team || team.characters || [];

    return (
        <div className="suggested-team-card" onClick={handleCardClick} style={{ cursor: 'pointer' }}> {/* Adicionar onClick e cursor */}
            <h4>{team.name || "Time Sugerido"}</h4>
            <div className="team-characters">
                {displayCharacters.map(char_item => ( // char_item pode ser um objeto de personagem ou um objeto com character_id
                    <div key={char_item.character_id || char_item.id} className="team-character-display" title={char_item.name || all_chars_map[char_item.character_id]?.name}>
                        <img
                            src={char_item.icon_url || all_chars_map[char_item.character_id]?.icon_url} // Precisa buscar os detalhes do personagem se só tiver ID
                            alt={char_item.name || all_chars_map[char_item.character_id]?.name}
                            className="team-character-icon"
                            onError={(e) => { e.target.style.display = 'none'; }}
                        />
                    </div>
                ))}
            </div>
            {team.strategy && <p className="team-strategy"><strong>Estratégia:</strong> {team.strategy}</p>}
        </div>
    );
};

export default SuggestedTeamCard;