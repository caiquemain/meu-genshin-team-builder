// frontend/src/components/WeaponTooltip.jsx
import React from 'react';
import './WeaponTooltip.css'; // Criaremos este CSS

const WeaponTooltip = ({ weaponData }) => {
    if (!weaponData) return null;

    return (
        <div className="weapon-tooltip-content">
            <div className="tooltip-header">
                {weaponData.icon_url && (
                    <img src={weaponData.icon_url} alt={weaponData.name} className="tooltip-weapon-icon" />
                )}
                <strong>{weaponData.name}</strong>
            </div>
            <div className="tooltip-body">
                <p><strong>Tipo:</strong> {weaponData.type} - <strong>Raridade:</strong> {weaponData.rarity}★</p>
                {weaponData.base_atk_lv90 && <p><strong>ATK Base (Nível 90):</strong> {weaponData.base_atk_lv90}</p>}
                {weaponData.secondary_stat_type && weaponData.secondary_stat_lv90 && (
                    <p><strong>Sub-Stat (Nível 90):</strong> {weaponData.secondary_stat_lv90} {weaponData.secondary_stat_type}</p>
                )}
                {weaponData.passive_name && <p><strong>Passiva:</strong> {weaponData.passive_name}</p>}
                {weaponData.passive_description_r1 && <p>{weaponData.passive_description_r1}</p>}
                {weaponData.source_category && <p><small>Fonte: {weaponData.source_category} {weaponData.source_category_obtainable === false ? "(Não obtenível)" : ""}</small></p>}
            </div>
        </div>
    );
};

export default WeaponTooltip;