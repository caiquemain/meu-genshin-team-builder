// frontend/src/App.jsx
import React, { useEffect } from 'react'; // Mantenha o useEffect
import { Routes, Route } from 'react-router-dom';
import TeamBuilderPage from './pages/TeamBuilderPage';
import TeamDetailPage from './pages/TeamDetailPage';
import CharacterProfilePage from './pages/CharacterProfilePage';
import LoginPage from './pages/LoginPage'; // Mantenha o import do LoginPage
import TierListPage from './pages/TierListPage'; // <-- Importe a página da TierList
import ThemeToggleButton from './components/ThemeToggleButton';
import './App.css';
import { fetchCsrfToken } from './services/api'; // Mantenha o import do fetchCsrfToken

function App() {
  // UseEffect para buscar o token CSRF quando o componente App for montado
  useEffect(() => {
    fetchCsrfToken()
      .then(() => {
        console.log('CSRF token fetched and Axios interceptor configured.');
      })
      .catch((error) => {
        console.error('Failed to fetch CSRF token on app mount:', error);
        // Trate este erro: mostre uma mensagem ao usuário, desabilite funcionalidades, etc.
      });
  }, []);

  return (
    <div className="App">
      <ThemeToggleButton />

      <Routes>
        <Route path="/" element={<TeamBuilderPage />} />
        <Route path="/team-detail" element={<TeamDetailPage />} />
        <Route path="/character/:characterId" element={<CharacterProfilePage />} />
        <Route path="/login" element={<LoginPage />} /> {/* ROTA PARA LOGIN */}
        <Route path="/tierlist" element={<TierListPage />} /> {/* ROTA PARA TIERLIST */}
      </Routes>
    </div>
  );
}

export default App;