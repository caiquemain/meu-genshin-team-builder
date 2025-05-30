// frontend/src/components/FilterBar.jsx
import React from 'react';
import './FilterBar.css'; // Certifique-se de que este arquivo CSS existe e está estilizado

// Caminhos dos ícones atualizados para incluir as subpastas
const ELEMENTS = [
    { id: 'Anemo', name: 'Anemo', icon: 'elements/element_anemo.png' },
    { id: 'Geo', name: 'Geo', icon: 'elements/element_geo.png' },
    { id: 'Electro', name: 'Electro', icon: 'elements/element_electro.png' },
    { id: 'Dendro', name: 'Dendro', icon: 'elements/element_dendro.png' },
    { id: 'Hydro', name: 'Hydro', icon: 'elements/element_hydro.png' },
    { id: 'Pyro', name: 'Pyro', icon: 'elements/element_pyro.png' },
    { id: 'Cryo', name: 'Cryo', icon: 'elements/element_cryo.png' },
];

const WEAPONS = [
    { id: 'Sword', name: 'Espada', icon: 'weapons/weapon_sword.png' },
    { id: 'Claymore', name: 'Espadão', icon: 'weapons/weapon_claymore.png' },
    { id: 'Polearm', name: 'Lança', icon: 'weapons/weapon_polearm.png' },
    { id: 'Bow', name: 'Arco', icon: 'weapons/weapon_bow.png' },
    { id: 'Catalyst', name: 'Catalisador', icon: 'weapons/weapon_catalyst.png' },
];

const RARITIES = [
    { id: 5, name: '5 Estrelas', icon: 'rarity/rarity_5.png' },
    { id: 4, name: '4 Estrelas', icon: 'rarity/rarity_4.png' },
];

const FilterButton = ({ filterItem, filterType, isActive, onFilterChange, basePath = '/assets/images/' }) => {
    // basePath é '/assets/images/'
    // filterItem.icon será, por exemplo, 'elements/element_anemo.png'
    // iconPath resultará em '/assets/images/elements/element_anemo.png'
    const iconPath = `${basePath}${filterItem.icon}`;

    const handleClick = () => {
        onFilterChange(filterType, filterItem.id);
    };

    const handleImageError = (e) => {
        console.error(`Erro ao carregar imagem do filtro: ${iconPath} para ${filterItem.name}`, e);
        // Adiciona uma borda para fácil identificação visual do ícone quebrado
        e.target.style.border = '2px solid red';
        e.target.alt = `Falha: ${filterItem.name}`; // Atualiza o alt text para indicar o erro
    };

    return (
        <button
            className={`filter-button ${isActive ? 'active' : ''}`}
            onClick={handleClick}
            title={filterItem.name}
        >
            <img
                src={iconPath}
                alt={filterItem.name}
                onError={handleImageError} // Handler para erros de carregamento da imagem
            />
        </button>
    );
};

const FilterSection = ({ title, items, filterType, activeFilterValue, onFilterChange }) => (
    <div className="filter-section">
        <h4>{title}</h4>
        <div className="filter-buttons-group">
            {items.map(item => (
                <FilterButton
                    key={item.id}
                    filterItem={item}
                    filterType={filterType}
                    isActive={activeFilterValue === item.id}
                    onFilterChange={onFilterChange}
                // basePath é pego do valor default em FilterButton
                />
            ))}
        </div>
    </div>
);

const FilterBar = ({ activeFilters, onFilterChange, currentNameQuery, onNameQueryChange }) => {
    return (
        <div className="filter-bar-container">
            <h3>Filtrar Personagens por:</h3>
            <FilterSection
                title="Elemento"
                items={ELEMENTS}
                filterType="element"
                activeFilterValue={activeFilters.element}
                onFilterChange={onFilterChange}
            />
            <FilterSection
                title="Arma"
                items={WEAPONS}
                filterType="weapon"
                activeFilterValue={activeFilters.weapon}
                onFilterChange={onFilterChange}
            />
            <FilterSection
                title="Raridade"
                items={RARITIES}
                filterType="rarity"
                activeFilterValue={activeFilters.rarity}
                onFilterChange={onFilterChange}
            />

            {/* Envolvendo o input em uma filter-section para consistência de layout e espaçamento */}
            <div className="filter-section">
                <h4>Buscar por Nome</h4> {/* Título opcional para a seção de busca */}
                <input
                    type="text"
                    placeholder="Digite o nome..."
                    className="name-search-input-bar" // A classe principal para o estilo do input
                    value={currentNameQuery}
                    onChange={(e) => onNameQueryChange(e.target.value)}
                />
            </div>
        </div>
    );
};

export default FilterBar;