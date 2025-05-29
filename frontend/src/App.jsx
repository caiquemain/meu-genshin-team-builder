// frontend/src/App.jsx
import React from 'react';
import { Routes, Route } from 'react-router-dom';
import TeamBuilderPage from './pages/TeamBuilderPage';
import TeamDetailPage from './pages/TeamDetailPage';
import CharacterProfilePage from './pages/CharacterProfilePage'; // <-- Importe a nova página
import ThemeToggleButton from './components/ThemeToggleButton';
import './App.css'; // Seu CSS global para o App

function App() {
  return (
    <div className="App">
      {/* O ThemeToggleButton pode ficar aqui para estar presente em todas as páginas */}
      <ThemeToggleButton />

      <Routes>
        <Route path="/" element={<TeamBuilderPage />} />
        <Route path="/team-detail" element={<TeamDetailPage />} />
        {/* NOVA ROTA para a página de perfil do personagem: */}
        <Route path="/character/:characterId" element={<CharacterProfilePage />} />
      </Routes>
    </div>
  );
}

export default App;