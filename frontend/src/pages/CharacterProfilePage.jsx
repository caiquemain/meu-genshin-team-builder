// frontend/src/pages/CharacterProfilePage.jsx
import React, { useState, useEffect, useRef } from 'react';
import { useParams, Link } from 'react-router-dom';
import axios from 'axios';
import ArtifactTooltip from '../components/ArtifactTooltip';
import WeaponTooltip from '../components/WeaponTooltip';
import './CharacterProfilePage.css';

const ELEMENT_COLORS = {
    Geo: '#FFCB68',
    Pyro: '#FF7755',
    Hydro: '#55DDFF',
    Electro: '#C37BFF',
    Cryo: '#A1E8FF',
    Anemo: '#88FFD5',
    Dendro: '#A2FF55',
    Default: '#777788'
};

const CharacterProfilePage = () => {
    const { characterId } = useParams();
    const [characterData, setCharacterData] = useState(null);
    const [suggestedTeams, setSuggestedTeams] = useState([]);
    const [artifactsDB, setArtifactsDB] = useState({});
    const [weaponsDB, setWeaponsDB] = useState({});
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState(null);
    const [teamsError, setTeamsError] = useState(null);
    const [dbError, setDbError] = useState(null);

    const [menuStyleState, setMenuStyleState] = useState('initial-center-style');
    const menuRef = useRef(null);
    const initialMenuTopOffset = useRef(0);

    const rarityIconBaseUrl = '/assets/images/rarity/';
    const weaponTypeIconBaseUrl = '/assets/images/weapons/';

    useEffect(() => {
        const fetchData = async () => {
            setIsLoading(true);
            setError(null);
            setTeamsError(null);
            setDbError(null);

            setCharacterData(null);
            setSuggestedTeams([]);
            setArtifactsDB({});
            setWeaponsDB({});

            try {
                const characterPromise = axios.get(`/api/character/${characterId}`);
                const teamsPromise = axios.get(`/api/teams-for-character/${characterId}`);
                const artifactsDBPromise = axios.get('/api/artifacts-database');
                const weaponsDBPromise = axios.get('/api/weapons-database');

                const [
                    charResponse,
                    teamsResponse,
                    artifactsResponse,
                    weaponsResponse
                ] = await Promise.all([characterPromise, teamsPromise, artifactsDBPromise, weaponsDBPromise]);

                setCharacterData(charResponse.data);
                setSuggestedTeams(teamsResponse.data || []);

                setArtifactsDB((artifactsResponse.data || []).reduce((acc, art) => { if (art && art.id) acc[art.id] = art; return acc; }, {}));
                setWeaponsDB((weaponsResponse.data || []).reduce((acc, wpn) => { if (wpn && wpn.id) acc[wpn.id] = wpn; return acc; }, {}));

            } catch (err) {
                console.error("Erro ao buscar dados na CharacterProfilePage:", err);
                if (err.config?.url?.includes(`/api/character/${characterId}`)) {
                    setError(err.response?.data?.error || "Falha ao carregar dados do personagem.");
                } else if (err.config?.url?.includes(`/api/teams-for-character/${characterId}`)) {
                    setTeamsError(err.response?.data?.error || "Falha ao carregar times sugeridos.");
                } else if (err.config?.url?.includes('/api/artifacts-database') || err.config?.url?.includes('/api/weapons-database')) {
                    setDbError("Falha ao carregar bancos de dados de artefatos/armas para tooltips.");
                } else {
                    setError("Ocorreu um erro desconhecido ao carregar os dados.");
                }
            } finally {
                setIsLoading(false);
            }
        };

        if (characterId) {
            fetchData();
        }
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [characterId]);

    useEffect(() => {
        if (menuRef.current && !isLoading && characterData) {
            initialMenuTopOffset.current = menuRef.current.offsetTop;
        }

        const handleScroll = () => {
            if (menuRef.current) {
                const shouldBeFixed = window.pageYOffset > initialMenuTopOffset.current;
                const newStyle = shouldBeFixed ? 'fixed-right-style' : 'initial-center-style';
                if (menuStyleState !== newStyle) {
                    setMenuStyleState(newStyle);
                }
            }
        };

        window.addEventListener('scroll', handleScroll, { passive: true });
        handleScroll();

        return () => window.removeEventListener('scroll', handleScroll);
    }, [isLoading, characterData, menuStyleState]);


    const renderStars = (rarity) => {
        let starPath = rarity === 5 ? `${rarityIconBaseUrl}rarity_5.png` : `${rarityIconBaseUrl}rarity_4.png`;
        return <img src={starPath} alt={`${rarity} estrelas`} className="rarity-stars-display" />;
    };

    const getWeaponTypeIcon = (weaponTypeName) => {
        if (!weaponTypeName) return null;
        const formattedName = weaponTypeName.toLowerCase().replace(/\s+/g, '');
        return `${weaponTypeIconBaseUrl}weapon_${formattedName}.png`;
    };

    if (isLoading && !characterData) return <div className="loading-message">Carregando perfil do personagem...</div>;

    if (error && !characterData) {
        return (
            <div className="error-message-container">
                <h1>Erro Crítico</h1>
                <p>{error}</p>
                <Link to="/">Voltar para Seleção de Times</Link>
            </div>
        );
    }

    if (!characterData) {
        return (
            <div className="info-message">
                Personagem com ID "{characterId}" não encontrado ou dados indisponíveis.
                {error && <p>Detalhe do erro: {error}</p>}
                {dbError && <p className="small-error-message">Aviso sobre DBs: {dbError}</p>}
                <Link to="/">Voltar para Seleção de Times</Link>
            </div>
        );
    }

    const accentColor = ELEMENT_COLORS[characterData.element] || ELEMENT_COLORS.Default;

    const profileSections = [
        { id: "general-info-section", label: "Visão Geral", condition: () => characterData.description_bio || characterData.region || characterData.role?.length > 0 },
        { id: "ascension-materials-section", label: "Materiais de Ascensão", condition: () => characterData.total_ascension_materials?.length > 0 },
        { id: "talent-materials-section", label: "Materiais para Talentos", condition: () => characterData.total_talent_materials_one_to_ten?.length > 0 },
        { id: "talents-section", label: "Talentos", condition: () => characterData.talents },
        { id: "constellations-section", label: "Constelações", condition: () => characterData.constellations?.length > 0 },
        { id: "builds-section", label: "Builds", condition: () => characterData.build_options?.length > 0 },
        { id: "references-section", label: "Referências", condition: () => characterData.info_references && ((characterData.info_references.character_details_sources?.length > 0) || (characterData.info_references.build_and_teams_sources?.length > 0)) },
        { id: "teams-section", label: "Times", condition: () => suggestedTeams?.length > 0 }
    ];

    return (
        <div
            className="character-profile-page"
            style={{ '--character-accent-color': accentColor }}
        >
            <header className="character-main-header">
                <div className="character-title-section">
                    <img src={characterData.icon_url} alt={characterData.name} className="character-profile-icon-large" />
                    <div className="character-name-details">
                        <h1>{characterData.name}</h1>
                        {characterData.title && <p className="character-title-subheader">{characterData.title}</p>}
                        <div className="character-meta-info">
                            {renderStars(characterData.rarity)}
                            <div className="character-type-info">
                                {characterData.element_icon_url && <img src={characterData.element_icon_url} alt={characterData.element} className="element-icon-profile" title={characterData.element} />}
                                {characterData.weapon && <img src={getWeaponTypeIcon(characterData.weapon)} alt={characterData.weapon} className="weapon-type-icon-profile" title={characterData.weapon} />}
                            </div>
                        </div>
                    </div>
                </div>
            </header>

            <nav
                ref={menuRef}
                className={`profile-quick-nav ${menuStyleState}`}
            >
                <ul>
                    {profileSections.map(section => (
                        section.condition() && ( // Chama a função de condição
                            <li key={section.id}>
                                <a href={`#${section.id}`}>{section.label}</a>
                            </li>
                        )
                    ))}
                </ul>
            </nav>

            {profileSections.find(s => s.id === "general-info-section")?.condition() && (
                <section id="general-info-section" className="profile-section">
                    <h2 className="section-title-accent">Informações Gerais</h2>
                    {characterData.description_bio && <p className="character-bio">{characterData.description_bio}</p>}
                    <div className="general-info-grid">
                        {characterData.region && <p><strong>Região:</strong> {characterData.region}</p>}
                        {characterData.affiliation?.length > 0 && <p><strong>Afiliação:</strong> {characterData.affiliation.join(', ')}</p>}
                        {characterData.birthday && <p><strong>Aniversário:</strong> {characterData.birthday}</p>}
                        {characterData.constellation_name_official && <p><strong>Constelação:</strong> {characterData.constellation_name_official}</p>}
                        {characterData.special_dish?.name && (
                            <p>
                                <strong>Prato Especial:</strong> {characterData.special_dish.name}
                                {characterData.special_dish.icon_url && <img src={characterData.special_dish.icon_url} alt={characterData.special_dish.name} className="item-icon-inline small-icon" />}
                            </p>
                        )}
                        {characterData.role?.length > 0 && <p><strong>Funções:</strong> {characterData.role.join(', ')}</p>}
                    </div>
                </section>
            )}
            {profileSections.find(s => s.id === "ascension-materials-section")?.condition() && (
                <section id="ascension-materials-section" className="profile-section">
                    <h2 className="section-title-accent">Materiais Totais para Ascensão (Nível 1-90)</h2>
                    {characterData.total_ascension_materials && characterData.total_ascension_materials.length > 0 ? (
                        <div className="materials-grid">
                            {characterData.total_ascension_materials.map((material, index) => (
                                <div key={`${characterId}-asc-mat-${index}`} className="material-card">
                                    <img
                                        src={material.icon_url || '/assets/images/materials/default_material.png'} // Fallback icon
                                        alt={material.name}
                                        className="material-icon"
                                        onError={(e) => { e.target.onerror = null; e.target.src = '/assets/images/materials/default_material.png'; }} // Fallback em caso de erro no ícone
                                    />
                                    <span className="material-name">{material.name}</span>
                                    <span className="material-quantity">
                                        {material.quantity.toLocaleString('pt-BR')} {/* Formata o número para o padrão brasileiro */}
                                    </span>
                                </div>
                            ))}
                        </div>
                    ) : (
                        <p className="info-message">Informações de materiais de ascensão não disponíveis.</p>
                    )}
                </section>
            )}
            {profileSections.find(s => s.id === "talent-materials-section")?.condition() && (
                <section id="talent-materials-section" className="profile-section">
                    <h2 className="section-title-accent">Materiais Totais para Talentos</h2>

                    {/* Sub-seção para 1 Talento */}
                    <div className="talent-materials-subsection">
                        <h3 className="subsection-title-accent">Para 1 Talento (Nível 1 ao 10)</h3>
                        {characterData.total_talent_materials_one_to_ten && characterData.total_talent_materials_one_to_ten.length > 0 ? (
                            <div className="materials-grid">
                                {characterData.total_talent_materials_one_to_ten.map((material, index) => (
                                    <div key={`${characterId}-talent1-mat-${index}`} className="material-card">
                                        <img
                                            src={material.icon_url || '/assets/images/materials/default_material.png'}
                                            alt={material.name}
                                            className="material-icon"
                                            onError={(e) => { e.target.onerror = null; e.target.src = '/assets/images/materials/default_material.png'; }}
                                        />
                                        <span className="material-name">{material.name}</span>
                                        <span className="material-quantity">
                                            {material.quantity.toLocaleString('pt-BR')}
                                        </span>
                                    </div>
                                ))}
                            </div>
                        ) : (
                            <p className="info-message">Informações de materiais para 1 talento não disponíveis.</p>
                        )}
                    </div>

                    {/* Sub-seção para 3 Talentos */}
                    <div className="talent-materials-subsection">
                        <h3 className="subsection-title-accent">Para 3 Talentos (Nível 1 ao 10 cada)</h3>
                        {characterData.total_talent_materials_one_to_ten && characterData.total_talent_materials_one_to_ten.length > 0 ? (
                            <div className="materials-grid">
                                {characterData.total_talent_materials_one_to_ten.map((material, index) => (
                                    <div key={`${characterId}-talent3-mat-${index}`} className="material-card">
                                        <img
                                            src={material.icon_url || '/assets/images/materials/default_material.png'}
                                            alt={material.name}
                                            className="material-icon"
                                            onError={(e) => { e.target.onerror = null; e.target.src = '/assets/images/materials/default_material.png'; }}
                                        />
                                        <span className="material-name">{material.name}</span>
                                        <span className="material-quantity">
                                            {(material.quantity * 3).toLocaleString('pt-BR')}
                                        </span>
                                    </div>
                                ))}
                            </div>
                        ) : (
                            <p className="info-message">Informações de materiais para 3 talentos não disponíveis.</p>
                        )}
                    </div>
                </section>
            )}

            {profileSections.find(s => s.id === "talents-section")?.condition() && (
                <section id="talents-section" className="profile-section">
                    <h2 className="section-title-accent">Talentos</h2>
                    {['normal_attack', 'elemental_skill', 'elemental_burst'].map(talentKey => {
                        const talent = characterData.talents?.[talentKey]; // Optional chaining aqui
                        if (!talent) return null;
                        return (
                            <div key={talentKey} className="talent-block accent-border-left">
                                <div className="talent-header">
                                    {talent.icon_url && <img src={talent.icon_url} alt={talent.name} className="talent-icon" />}
                                    <h3>{talent.name}</h3>
                                </div>
                                <p className="talent-description">{talent.description}</p>
                            </div>
                        );
                    })}
                    {characterData.talents?.passives?.length > 0 && (
                        <div className="passives-block">
                            <h4 className="column-title-accent">Talentos Passivos</h4>
                            {characterData.talents.passives.map((passive, index) => (
                                <div key={index} className="talent-block passive-talent accent-border-left-light">
                                    <div className="talent-header">
                                        {passive.icon_url && <img src={passive.icon_url} alt={passive.name} className="talent-icon small-icon" />}
                                        <h5>{passive.name} <span className="passive-type">({passive.type})</span></h5>
                                    </div>
                                    <p className="talent-description">{passive.description}</p>
                                </div>
                            ))}
                        </div>
                    )}
                </section>
            )}

            {profileSections.find(s => s.id === "constellations-section")?.condition() && (
                <section id="constellations-section" className="profile-section">
                    <h2 className="section-title-accent">Constelações</h2>
                    <div className="constellations-grid">
                        {characterData.constellations.map((constellation) => (
                            <div key={constellation.level} className="constellation-item accent-border-left-light">
                                <div className="constellation-header">
                                    {constellation.icon_url && <img src={constellation.icon_url} alt={constellation.name} className="constellation-icon" />}
                                    <div>
                                        <strong>C{constellation.level}: {constellation.name}</strong>
                                    </div>
                                </div>
                                <p className="constellation-description">{constellation.description}</p>
                            </div>
                        ))}
                    </div>
                </section>
            )}

            {profileSections.find(s => s.id === "builds-section")?.condition() && (
                <section id="builds-section" className="profile-section">
                    <h2 className="section-title-accent">Opções de Build Recomendadas</h2>
                    {dbError && <p className="error-message small-error-message">Aviso: {dbError}. Detalhes nos tooltips podem estar indisponíveis.</p>}

                    {/* Aqui usamos a estrutura ternária correta que foi corrigida antes */}
                    {characterData.build_options && characterData.build_options.length > 0 ? (
                        characterData.build_options.map((build, index) => (
                            <div key={build.key || index} className="build-option-container">
                                <h3 className="build-title-accent">{build.name}</h3>
                                {build.notes_build && <p className="build-notes-full accent-border-left">{build.notes_build}</p>}
                                <div className="build-columns">
                                    <div className="build-column">
                                        <h4 className="column-title-accent">Artefatos</h4>
                                        {build.artifacts?.map((artifactEntry, artIndex) => {
                                            let artifactDataForTooltip = null;
                                            let comboDataForTooltip = null;
                                            let isCombo = artifactEntry.is_combo && artifactEntry.combo_set_ids?.length > 0;

                                            if (isCombo) {
                                                comboDataForTooltip = artifactEntry.combo_set_ids.map(id => artifactsDB[id]).filter(Boolean);
                                            } else if (artifactEntry.set_id && artifactsDB[artifactEntry.set_id]) {
                                                artifactDataForTooltip = artifactsDB[artifactEntry.set_id];
                                            }

                                            const displayPieces = artifactEntry.pieces_display || artifactEntry.pieces;
                                            const displayName = artifactEntry.set_name_display || artifactEntry.set_name;

                                            return (
                                                <div key={artIndex} className="artifact-set-item tooltip-container-hover">
                                                    <img src={artifactEntry.icon_url} alt={displayName} className="item-icon-medium" />
                                                    <div>
                                                        <strong>{displayName} ({displayPieces}p)</strong>
                                                        {artifactEntry.notes && <p className="item-notes"><em>{artifactEntry.notes}</em></p>}
                                                    </div>
                                                    {(artifactDataForTooltip || comboDataForTooltip?.length > 0) && (
                                                        <ArtifactTooltip
                                                            artifactData={!isCombo ? artifactDataForTooltip : null}
                                                            comboArtifactsData={isCombo ? comboDataForTooltip : null}
                                                        />
                                                    )}
                                                </div>
                                            );
                                        })}
                                        <h4 className="column-title-accent">Atributos Principais (Artefatos)</h4>
                                        <ul className="main-stats-list">
                                            {/* Adicionado optional chaining para build.main_stats */}
                                            <li><strong>Areia:</strong> {build.main_stats?.sands}</li>
                                            <li><strong>Cálice:</strong> {build.main_stats?.goblet}</li>
                                            <li><strong>Tiara:</strong> {build.main_stats?.circlet}</li>
                                        </ul>
                                    </div>
                                    <div className="build-column">
                                        <h4 className="column-title-accent">Armas</h4>
                                        {build.weapons?.map((weaponEntry, wepIndex) => {
                                            const weaponDetailsFromDB = weaponsDB[weaponEntry.weapon_id];
                                            return (
                                                <div key={wepIndex} className="weapon-option-item tooltip-container-hover">
                                                    <img src={weaponEntry.icon_url} alt={weaponEntry.name} className="item-icon-medium" />
                                                    <div>
                                                        <strong>{weaponEntry.name} ({weaponEntry.rarity}★ {weaponEntry.type})</strong>
                                                        {weaponEntry.category && <p className="item-category">Categoria: {weaponEntry.category}</p>}
                                                        {weaponEntry.notes && <p className="item-notes"><em>{weaponEntry.notes}</em></p>}
                                                    </div>
                                                    {weaponDetailsFromDB && (
                                                        <WeaponTooltip weaponData={weaponDetailsFromDB} />
                                                    )}
                                                </div>
                                            );
                                        })}
                                    </div>
                                </div>
                                <div className="substats-talents-row">
                                    <div className="substats-priority">
                                        <h4 className="column-title-accent">Prioridade de Sub-Atributos</h4>
                                        <ol>
                                            {build.sub_stats_priority?.map((stat, i) => <li key={i}>{stat}</li>)}
                                        </ol>
                                    </div>
                                    <div className="talent-priority">
                                        <h4 className="column-title-accent">Prioridade de Talentos</h4>
                                        <ol>
                                            {build.talent_priority?.map((talent, i) => <li key={i}>{talent}</li>)}
                                        </ol>
                                    </div>
                                </div>
                            </div>
                        )) // Fim do .map()
                    ) : ( // Else do ternário
                        <p className="info-message">Nenhuma build recomendada encontrada para este personagem.</p>
                    )}
                </section>
            )}

            {profileSections.find(s => s.id === "references-section")?.condition() && (
                <section id="references-section" className="profile-section">
                    <h2 className="section-title-accent">Fontes e Referências</h2>
                    {characterData.info_references?.character_details_sources?.length > 0 && (
                        <div className="reference-subsection">
                            <h4>Informações do Personagem:</h4>
                            <ul className="references-list">
                                {characterData.info_references.character_details_sources.map((ref, index) => (
                                    <li key={`char-ref-${index}`}>
                                        {ref.url ? (
                                            <a href={ref.url.startsWith('http') ? ref.url : `https://${ref.url}`} target="_blank" rel="noopener noreferrer">
                                                {ref.name || ref.url}
                                            </a>
                                        ) : (
                                            ref.name || ref.description
                                        )}
                                        {ref.url && ref.name && ref.description && ` - ${ref.description}`}
                                        {!ref.url && ref.name && ref.description && `: ${ref.description}`}
                                    </li>
                                ))}
                            </ul>
                        </div>
                    )}

                    {characterData.info_references?.build_and_teams_sources?.length > 0 && (
                        <div className="reference-subsection">
                            <h4>Informações de Builds e Times:</h4>
                            <ul className="references-list">
                                {characterData.info_references.build_and_teams_sources.map((ref, index) => (
                                    <li key={`build-ref-${index}`}>
                                        {ref.url ? (
                                            <a href={ref.url.startsWith('http') ? ref.url : `https://${ref.url}`} target="_blank" rel="noopener noreferrer">
                                                {ref.name || ref.url}
                                            </a>
                                        ) : (
                                            ref.name || ref.description
                                        )}
                                        {ref.url && ref.name && ref.description && ` - ${ref.description}`}
                                        {!ref.url && ref.name && ref.description && `: ${ref.description}`}
                                    </li>
                                ))}
                            </ul>
                        </div>
                    )}
                    {/* Mensagem caso nenhuma referência específica seja encontrada mas a seção existe */}
                    {
                        !(characterData.info_references?.character_details_sources?.length > 0) &&
                        !(characterData.info_references?.build_and_teams_sources?.length > 0) &&
                        <p>Nenhuma fonte de referência específica listada para esta seção.</p>
                    }
                </section>
            )}


            {profileSections.find(s => s.id === "teams-section")?.condition() && (
                <section id="teams-section" className="profile-section">
                    <h2 className="section-title-accent">Times Recomendados com {characterData.name}</h2>
                    {teamsError && <p className="error-message">{teamsError}</p>}
                    {/* Se teamsError for null e suggestedTeams estiver vazio */}
                    {!teamsError && suggestedTeams.length === 0 && (
                        <p className="info-message">Nenhum time sugerido encontrado ou disponível no momento.</p>
                    )}
                    {/* Só renderiza o grid se houver times e não houver erro de times */}
                    {!teamsError && suggestedTeams.length > 0 && (
                        <div className="suggested-teams-grid">
                            {suggestedTeams.map((team, index) => (
                                <div key={team.name || index} className="suggested-team-profile-card accent-border-left">
                                    <h4>{team.name}</h4>
                                    <p className="team-notes">{team.notes || 'Sem notas adicionais para este time.'}</p>
                                    <div className="team-characters-profile">
                                        {team.characters_in_team?.map(member => (
                                            <div key={member.id} className="team-member-profile" title={`${member.name}\nFunção: ${member.role_in_team || 'N/A'}`}>
                                                <img src={member.icon_url} alt={member.name} className="team-member-icon-small" />
                                            </div>
                                        ))}
                                    </div>
                                    <Link
                                        to={`/team-detail`}
                                        state={{ teamData: team }}
                                        className="view-team-detail-link button-accent"
                                    >
                                        Ver Detalhes do Time
                                    </Link>
                                </div>
                            ))}
                        </div>
                    )}
                </section>
            )}

            <Link to="/" className="back-link-profile button-accent">Voltar para Seleção de Times</Link>
        </div>
    );
};

export default CharacterProfilePage;