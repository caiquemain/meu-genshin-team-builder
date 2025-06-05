// frontend/src/App.jsx
import React, { useEffect } from 'react'; // <-- Importe useEffect
import { Routes, Route } from 'react-router-dom';
import TeamBuilderPage from './pages/TeamBuilderPage';
import TeamDetailPage from './pages/TeamDetailPage';
import CharacterProfilePage from './pages/CharacterProfilePage';
import ThemeToggleButton from './components/ThemeToggleButton';
import './App.css';
import { fetchCsrfToken } from './services/api'; // <-- Importe fetchCsrfToken

function App() {
  // UseEffect para buscar o token CSRF quando o componente App for montado
  useEffect(() => {
    // É importante notar que este fetchCsrfToken() será chamado uma vez
    // quando o componente App é montado. Se a sua lógica de login envolve
    // um redirecionamento ou uma SPA que não recarrega, e o token expira
    // ou é necessário após o login, você precisaria re-chamar fetchCsrfToken
    // em um contexto de autenticação ou após o evento de login.
    fetchCsrfToken()
      .then(() => {
        console.log('CSRF token fetched and Axios interceptor configured.');
      })
      .catch((error) => {
        console.error('Failed to fetch CSRF token on app mount:', error);
        // Trate este erro: mostre uma mensagem ao usuário, desabilite funcionalidades, etc.
      });
  }, []); // O array vazio [] garante que o useEffect rode apenas uma vez (no mount)

  return (
    <div className="App">
      <ThemeToggleButton />

      <Routes>
        <Route path="/" element={<TeamBuilderPage />} />
        <Route path="/team-detail" element={<TeamDetailPage />} />
        <Route path="/character/:characterId" element={<CharacterProfilePage />} />
      </Routes>
    </div>
  );
}

export default App;