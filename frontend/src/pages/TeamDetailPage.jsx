// frontend/src/pages/TeamDetailPage.jsx
import React, { useState, useEffect } from 'react';
import { useLocation, Link } from 'react-router-dom';
import axios from 'axios';
import ArtifactTooltip from '../components/ArtifactTooltip';
import WeaponTooltip from '../components/WeaponTooltip';
import './TeamDetailPage.css'; // Certifique-se que este CSS existe e tem as regras de tooltip

const TeamDetailPage = () => {
    const location = useLocation();
    const { teamData } = location.state || {}; // Dados do time passados via Link state

    const [artifactsDB, setArtifactsDB] = useState({});
    const [weaponsDB, setWeaponsDB] = useState({});
    const [loadingData, setLoadingData] = useState(true);
    const [dbError, setDbError] = useState(null);

    useEffect(() => {
        const fetchGameData = async () => {
            if (!teamData) { // Se não há teamData, não buscar DBs
                setLoadingData(false);
                return;
            }
            setLoadingData(true);
            setDbError(null);
            try {
                // Usar URLs relativas se tiver proxy, ou absolutas se não.
                // Exemplo com relativas (assumindo proxy no Vite ou mesma origem):
                const artifactsPromise = axios.get('/api/artifacts-database');
                const weaponsPromise = axios.get('/api/weapons-database');

                // Se precisar de URLs absolutas (ex: backend em porta diferente sem proxy):
                // const artifactsPromise = axios.get('http://127.0.0.1:5000/api/artifacts-database');
                // const weaponsPromise = axios.get('http://127.0.0.1:5000/api/weapons-database');

                const [artifactsRes, weaponsRes] = await Promise.all([
                    artifactsPromise,
                    weaponsPromise
                ]);

                const artifactsMap = (artifactsRes.data || []).reduce((acc, artifact) => {
                    if (artifact && artifact.id) acc[artifact.id] = artifact;
                    return acc;
                }, {});
                setArtifactsDB(artifactsMap);
                // console.log("TeamDetailPage - Artifacts DB Mapped:", artifactsMap);

                const weaponsMap = (weaponsRes.data || []).reduce((acc, weapon) => {
                    if (weapon && weapon.id) acc[weapon.id] = weapon;
                    return acc;
                }, {});
                setWeaponsDB(weaponsMap);
                // console.log("TeamDetailPage - Weapons DB Mapped:", weaponsMap);

            } catch (error) {
                console.error("Erro ao buscar dados do jogo (artefatos/armas) na TeamDetailPage:", error);
                setDbError("Falha ao carregar informações de artefatos/armas para tooltips.");
            } finally {
                setLoadingData(false);
            }
        };
        fetchGameData();
    }, [teamData]);

    if (!teamData || !teamData.characters_in_team) {
        return (
            <div className="team-detail-container error-page">
                <h2>Erro na Seleção do Time</h2>
                <p>Os dados do time não foram encontrados ou estão incompletos. Por favor, retorne e selecione um time novamente.</p>
                <Link to="/" className="back-link">‹ Voltar</Link>
            </div>
        );
    }

    if (loadingData) {
        return <p className="loading-message">Carregando detalhes do time...</p>;
    }

    return (
        <div className="team-detail-container">
            <Link to="/" className="back-link">‹ Voltar para Seleção</Link>
            <h2 className="team-name-detail">{teamData.name}</h2>
            {teamData.strategy && <p className="team-strategy-detail"><strong>Estratégia:</strong> {teamData.strategy}</p>}
            {dbError && <p className="error-message small-error-message">{dbError}</p>}


            <div className="characters-builds-grid">
                {teamData.characters_in_team.map((charBuildInfo, index) => (
                    <div key={charBuildInfo.id || `char-${index}`} className="character-build-card">
                        <div className="character-header-detail"> {/* Classe diferente para evitar conflito se houver */}
                            <Link to={`/character/${charBuildInfo.id}`} className="character-icon-link">
                                {charBuildInfo.icon_url && (
                                    <img
                                        src={charBuildInfo.icon_url}
                                        alt={charBuildInfo.name || 'Ícone'}
                                        className="character-build-icon"
                                    />
                                )}
                            </Link>
                            <div className="character-info-detail">
                                <h3>
                                    <Link to={`/character/${charBuildInfo.id}`} className="character-name-link">
                                        {charBuildInfo.name || charBuildInfo.character_id}
                                    </Link>
                                </h3>
                                {charBuildInfo.role_in_team && <p className="character-role">Função: {charBuildInfo.role_in_team}</p>}
                            </div>
                        </div>

                        {charBuildInfo.build_details && Object.keys(charBuildInfo.build_details).length > 0 ? (
                            <div className="build-section-detail">
                                <h4>Build Sugerida:
                                    {charBuildInfo.build_details.name && <span className="build-name-note"> ({charBuildInfo.build_details.name})</span>}
                                </h4>
                                {charBuildInfo.build_details.notes_build && <p className="build-overall-notes">{charBuildInfo.build_details.notes_build}</p>}

                                {/* Seção de Artefatos */}
                                {charBuildInfo.build_details.artifacts?.length > 0 && (
                                    <div className="build-subsection">
                                        <strong>Artefatos:</strong>
                                        <ul>
                                            {charBuildInfo.build_details.artifacts.map((artifactEntry, i) => {
                                                let artifactDataForTooltip = null;
                                                let comboDataForTooltip = null;
                                                let isCombo = artifactEntry.is_combo && artifactEntry.combo_set_ids?.length > 0;

                                                if (isCombo) {
                                                    comboDataForTooltip = artifactEntry.combo_set_ids.map(id => artifactsDB[id]).filter(Boolean);
                                                    // console.log(`TeamDetail - Combo lookup for ${artifactEntry.set_name_display}:`, comboDataForTooltip);
                                                } else if (artifactEntry.set_id && artifactsDB[artifactEntry.set_id]) {
                                                    artifactDataForTooltip = artifactsDB[artifactEntry.set_id];
                                                    // console.log(`TeamDetail - Single artifact lookup for ${artifactEntry.set_name}:`, artifactDataForTooltip);
                                                }

                                                const displayPieces = artifactEntry.pieces_display || artifactEntry.pieces;
                                                const displayName = artifactEntry.set_name_display || artifactEntry.set_name;

                                                return (
                                                    <li key={`${charBuildInfo.id}-art-${i}`} className="artifact-item-container">
                                                        <div className="tooltip-wrapper"> {/* Container para hover */}
                                                            <span className="item-display-content"> {/* Elemento que aciona o tooltip */}
                                                                {artifactEntry.icon_url && (
                                                                    <img src={artifactEntry.icon_url} alt={displayName} className="item-icon-inline" />
                                                                )}
                                                                <span className="artifact-name-text">
                                                                    {displayPieces}-peças: {displayName}
                                                                </span>
                                                            </span>
                                                            {(artifactDataForTooltip || comboDataForTooltip?.length > 0) && (
                                                                <ArtifactTooltip
                                                                    artifactData={!isCombo ? artifactDataForTooltip : null}
                                                                    comboArtifactsData={isCombo ? comboDataForTooltip : null}
                                                                />
                                                            )}
                                                        </div>
                                                        {artifactEntry.notes && <span className="build-notes-inline"> ({artifactEntry.notes})</span>}
                                                    </li>
                                                );
                                            })}
                                        </ul>
                                    </div>
                                )}

                                {/* Seção de Stats Principais */}
                                {charBuildInfo.build_details.main_stats && (
                                    <div className="build-subsection">
                                        <strong>Stats Principais:</strong>
                                        <p><span>Areia:</span> {charBuildInfo.build_details.main_stats.sands}</p>
                                        <p><span>Cálice:</span> {charBuildInfo.build_details.main_stats.goblet}</p>
                                        <p><span>Tiara:</span> {charBuildInfo.build_details.main_stats.circlet}</p>
                                    </div>
                                )}

                                {/* Seção de Prioridade de Substats */}
                                {charBuildInfo.build_details.sub_stats_priority?.length > 0 && (
                                    <div className="build-subsection">
                                        <strong>Prioridade de Substats:</strong>
                                        <p>{charBuildInfo.build_details.sub_stats_priority.join(' > ')}</p> {/* Alterado para > para melhor leitura */}
                                    </div>
                                )}

                                {/* Seção de Armas */}
                                {charBuildInfo.build_details.weapons?.length > 0 && (
                                    <div className="build-subsection">
                                        <strong>Armas Sugeridas:</strong>
                                        <ul>
                                            {charBuildInfo.build_details.weapons.map((weaponEntry, i) => {
                                                const weaponDetailsFromDB = weaponsDB[weaponEntry.weapon_id];
                                                // console.log(`TeamDetail - Weapon lookup for ${weaponEntry.name}:`, weaponDetailsFromDB);
                                                return (
                                                    <li key={`${charBuildInfo.id}-wep-${i}`} className="weapon-item-container">
                                                        <div className="tooltip-wrapper"> {/* Container para hover */}
                                                            <span className="item-display-content"> {/* Elemento que aciona o tooltip */}
                                                                {weaponEntry.icon_url && (
                                                                    <img src={weaponEntry.icon_url} alt={weaponEntry.name} className="item-icon-inline" />
                                                                )}
                                                                <span className="weapon-name-text">
                                                                    {weaponEntry.name}
                                                                    {weaponEntry.rarity && <span className="rarity-indicator"> ({weaponEntry.rarity}★)</span>}
                                                                </span>
                                                            </span>
                                                            {weaponDetailsFromDB && (
                                                                <WeaponTooltip weaponData={weaponDetailsFromDB} />
                                                            )}
                                                        </div>
                                                        {weaponEntry.category && <span className="weapon-category-inline"> [{weaponEntry.category}]</span>}
                                                        {weaponEntry.notes && <span className="build-notes-inline"> - {weaponEntry.notes}</span>}
                                                    </li>
                                                );
                                            })}
                                        </ul>
                                    </div>
                                )}

                                {/* Seção de Prioridade de Talentos */}
                                {charBuildInfo.build_details.talent_priority?.length > 0 && (
                                    <div className="build-subsection">
                                        <strong>Prioridade de Talentos:</strong>
                                        <p>{charBuildInfo.build_details.talent_priority.join(' > ')}</p> {/* Alterado para > */}
                                    </div>
                                )}
                            </div>
                        ) : (
                            <p>Detalhes da build para este personagem nesta equipe não foram especificados.</p>
                        )}
                    </div>
                ))}
            </div>
        </div>
    );
};

export default TeamDetailPage;