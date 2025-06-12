// frontend/src/pages/LoginPage.jsx
import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../services/api'; // Importe a instância do Axios configurada
import './LoginPage.css'; // Crie este arquivo CSS para estilização

const LoginPage = () => {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState(''); // Para exibir mensagens de erro
    const navigate = useNavigate(); // Hook para navegação programática

    const handleSubmit = async (e) => {
        e.preventDefault(); // Previne o comportamento padrão de recarregamento do formulário
        setError(''); // Limpa erros anteriores

        try {
            // Faz a requisição POST para a rota de login do backend
            const response = await api.post('/login', { username, password });

            console.log('Login bem-sucedido:', response.data);
            // Aqui você pode armazenar o estado de login do usuário (ex: em um Context API ou Redux/Zustand)
            // Por enquanto, vamos apenas redirecionar para a página inicial
            navigate('/'); // Redireciona para a página inicial após o login

        } catch (err) {
            console.error('Erro no login:', err);
            if (err.response && err.response.data && err.response.data.message) {
                // Se o backend retornou uma mensagem de erro específica
                setError(err.response.data.message);
            } else {
                // Mensagem de erro genérica
                setError('Falha no login. Verifique suas credenciais e tente novamente.');
            }
        }
    };

    return (
        <div className="login-page">
            <h2>Login</h2>
            <form onSubmit={handleSubmit} className="login-form">
                <div className="form-group">
                    <label htmlFor="username">Usuário:</label>
                    <input
                        type="text"
                        id="username"
                        value={username}
                        onChange={(e) => setUsername(e.target.value)}
                        required
                    />
                </div>
                <div className="form-group">
                    <label htmlFor="password">Senha:</label>
                    <input
                        type="password"
                        id="password"
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        required
                    />
                </div>
                {error && <p className="error-message">{error}</p>}
                <button type="submit">Entrar</button>
            </form>
        </div>
    );
};

export default LoginPage;