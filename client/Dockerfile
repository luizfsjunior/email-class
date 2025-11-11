# Frontend Dockerfile - React + Vite com build otimizado
# Multi-stage build para produção

FROM node:20-alpine as builder

WORKDIR /app

# Copia package files
COPY package.json package-lock.json* ./

# Instala dependências
RUN npm ci

# Copia código fonte
COPY . .

# Build para produção
RUN npm run build

# Stage 2: Serve com nginx
FROM nginx:alpine

# Copia build do stage anterior
COPY --from=builder /app/dist /usr/share/nginx/html

# Copia configuração customizada do nginx (para SPA routing)
RUN echo 'server { \
    listen 80; \
    location / { \
        root /usr/share/nginx/html; \
        index index.html; \
        try_files $uri $uri/ /index.html; \
    } \
}' > /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
