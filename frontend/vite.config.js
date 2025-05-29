// frontend/vite.config.js
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/api': { // Requisições para /api/... serão redirecionadas
        target: 'http://localhost:5000', // URL do seu backend Flask
        changeOrigin: true,
        // rewrite: (path) => path.replace(/^\/api/, '') // Remova /api se o backend não tiver /api no prefixo
      }
    }
  }
})