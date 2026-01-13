# Guia de Deploy: EC2 Ubuntu (Reddit Radar)

Este guia cobre o passo a passo para hospedar o sistema em uma instância EC2 da AWS rodando Ubuntu 22.04+.

## 1. Requisitos da Instância
- **Tipo Recomendado:** `t3.medium` (Mínimo 4GB RAM para processamento de embeddings e ChromaDB).
- **Security Group (Portas):**
    - `80` (HTTP)
    - `443` (HTTPS)
    - `8000` (Somente se quiser testar a API diretamente, opcional se usar Nginx).

## 2. Preparação do Servidor

Conecte-se via SSH e execute:

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3-pip python3-venv nodejs npm git nginx
```

## 3. Deploy do Código

```bash
git clone https://github.com/fDiosc/redditscrapping.git
cd redditscrapping
```

### Backend Setup
```bash
# Criar ambiente virtual
python3 -m venv venv
source venv/bin/activate

# Instalar dependências
pip install --upgrade pip
pip install -e .

# Configurar variáveis de ambiente
cp .env.example .env
nano .env  # Adicione suas chaves (OpenAI, Reddit, Clerk)
```

### Frontend Setup
```bash
cd web
npm install

# Criar arquivo de ambiente do frontend
echo "VITE_API_BASE=https://seu-dominio.com" > .env.production

# Build do projeto
npm run build
```

## 4. Gerenciamento de Processos (pm2 ou systemd)

Recomendamos usar o `pm2` para gerenciar o backend e garantir que ele reinicie sozinho:

```bash
sudo npm install -g pm2
pm2 start "venv/bin/python3 -m uvicorn radar.api.main:app --host 0.0.0.0 --port 8000" --name "radar-api"
pm2 save
pm2 startup
```

## 5. Configuração do Nginx

Crie um novo arquivo de configuração:
`sudo nano /etc/nginx/sites-available/radar`

Cole o seguinte conteúdo (ajustando o `server_name`):

```nginx
server {
    listen 80;
    server_name seu-dominio.com;

    # Frontend
    location / {
        root /home/ubuntu/redditscrapping/web/dist;
        index index.html;
        try_files $uri $uri/ /index.html;
    }

    # Backend API Proxy
    location /api/ {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
}
```

Ative o site e reinicie o Nginx:
```bash
sudo ln -s /etc/nginx/sites-available/radar /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

## 6. SSL (Certbot)

```bash
sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx -d seu-dominio.com
```

## 7. Notas Adicionais
- **Banco de Dados:** O sistema usa SQLite (`data/radar.db`). Certifique-se de que a pasta `data/` tenha permissão de escrita para o usuário que roda o processo.
- **Crontab:** Caso queira agendar o processamento automático:
  `0 * * * * cd /home/ubuntu/redditscrapping && ./venv/bin/python -m radar.cli ingest && ./venv/bin/python -m radar.cli process`
