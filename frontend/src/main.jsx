// frontend/src/main.jsx
import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App.jsx';
import './index.css'; // Seu CSS global
import { BrowserRouter } from 'react-router-dom';
import { ThemeProvider } from './contexts/ThemeContext.jsx'; // <-- Seu import existente 
import { SelectedCharactersProvider } from './contexts/SelectedCharactersContext.jsx'; // <-- Importar o novo Provider

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <BrowserRouter>
      <ThemeProvider> {/* // <-- Seu ThemeProvider existente  */}
        <SelectedCharactersProvider> {/* // <-- Envolver com SelectedCharactersProvider AQUI */}
          <App />
        </SelectedCharactersProvider>
      </ThemeProvider>
    </BrowserRouter>
  </React.StrictMode>,
);