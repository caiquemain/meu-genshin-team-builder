// frontend/src/components/ThemeToggleButton.jsx
import React from 'react';
import { useTheme } from '../contexts/ThemeContext'; // Ajuste o caminho se necessário
import './ThemeToggleButton.css'; // Criaremos este CSS

const ThemeToggleButton = () => {
    const { theme, toggleTheme } = useTheme();

    return (
        <button
            onClick={toggleTheme}
            className={`theme-toggle-button ${theme}`}
            aria-label={`Mudar para tema ${theme === 'light' ? 'escuro' : 'claro'}`}
            title={`Mudar para tema ${theme === 'light' ? 'escuro' : 'claro'}`}
        >
            {/* Você pode usar ícones SVG ou texto aqui */}
            {theme === 'light' ? '🌙' : '☀️'}
        </button>
    );
};

export default ThemeToggleButton;