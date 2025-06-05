# Usa uma imagem oficial do Node.js como base (versão LTS recomendada)
FROM node:20-alpine

# Define o diretório de trabalho dentro do contêiner
WORKDIR /app

# Copia os arquivos package.json e package-lock.json e instala as dependências
COPY package*.json ./
RUN npm install

# Copia o restante do código da sua aplicação React
COPY . .

# Constrói a aplicação React para produção
# 'build' é o comando padrão do Vite para criar a versão de produção
RUN npm run build

# Expõe a porta que o servidor de arquivos estáticos (Nginx ou outro) usará
EXPOSE 80

# Comando para servir os arquivos estáticos com Nginx (servidor web leve e eficiente)
# Primeiro, uma imagem de Nginx é mais adequada para servir arquivos estáticos de produção.
# Vamos fazer isso em um Dockerfile multi-stage.

# --- Stage 2: Servir a aplicação construída com Nginx ---
FROM nginx:alpine

# Copia a saída da build do estágio anterior para o diretório de serviço do Nginx
COPY --from=0 /app/dist /usr/share/nginx/html

# Copia a configuração personalizada do Nginx (opcional, mas recomendado)
# Se você tiver um arquivo nginx.conf personalizado, coloque-o na pasta frontend/
# COPY nginx.conf /etc/nginx/conf.d/default.conf

# Expõe a porta 80
EXPOSE 80

# Inicia o Nginx em primeiro plano
CMD ["nginx", "-g", "daemon off;"]