# 🚀 Deploy VPS - API Consulta v2

Guia para configurar e fazer deploy da API na VPS de produção.

## 📋 Pré-requisitos

### Na VPS (69.62.103.163):
- ✅ Docker instalado
- ✅ Docker Compose instalado
- ✅ Acesso SSH configurado
- ✅ Firewall liberando portas 80, 8000, 9090

### No GitHub:
- 🔑 **VPS_SSH_PRIVATE_KEY**: Chave SSH privada para acesso à VPS
- 🔑 **DOCKER_HUB_USERNAME**: Seu username do Docker Hub
- 🔑 **DOCKER_HUB_PASSWORD**: Token ou senha do Docker Hub

## 🛠️ Configuração Inicial da VPS

### 1. Preparar estrutura de diretórios:
```bash
ssh root@69.62.103.163
mkdir -p /opt/api-consulta-v2/{logs,storage,monitoring}
cd /opt/api-consulta-v2
```

### 2. Criar arquivo .env na VPS:
```bash
# Na VPS, crie o arquivo .env com suas configurações
cat > .env << 'EOF'
# MongoDB Atlas
MONGO_URI=mongodb+srv://seu_usuario:sua_senha@cluster0.wjwnv.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0
DATABASE_NAME=api_consulta_v2_prod

# Segurança  
SECRET_KEY=sua-chave-secreta-muito-forte-para-producao
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

# Docker Hub
DOCKER_HUB_USERNAME=seu_usuario_dockerhub

# API
ENVIRONMENT=production
DEBUG=false
HOST=0.0.0.0
PORT=8000
ENABLE_CORS=true
CORS_ORIGINS=["*"]
ENABLE_METRICS=true
EOF
```

### 3. Configurar firewall (se necessário):
```bash
# Ubuntu/Debian
ufw allow 22    # SSH
ufw allow 80    # HTTP
ufw allow 8000  # API
ufw allow 9090  # Prometheus (opcional)
ufw enable

# CentOS/RHEL
firewall-cmd --permanent --add-port=22/tcp
firewall-cmd --permanent --add-port=80/tcp  
firewall-cmd --permanent --add-port=8000/tcp
firewall-cmd --permanent --add-port=9090/tcp
firewall-cmd --reload
```

## 🚀 Deploy Manual

### Usando o script de deploy:
```bash
# No seu ambiente de desenvolvimento
./deploy-vps.sh latest
```

### Deploy manual passo a passo:
```bash
# 1. Copiar arquivos de configuração
scp docker-compose.vps.yml root@69.62.103.163:/opt/api-consulta-v2/docker-compose.yml
scp nginx.vps.conf root@69.62.103.163:/opt/api-consulta-v2/nginx.conf

# 2. Conectar na VPS e fazer deploy
ssh root@69.62.103.163

cd /opt/api-consulta-v2

# 3. Baixar imagem
docker pull seu_usuario/poc-api-consulta-v2:latest

# 4. Parar containers existentes
docker compose down

# 5. Iniciar novos containers
docker compose up -d

# 6. Verificar status
docker compose ps
curl http://localhost:8000/health
```

## 🤖 Deploy Automatizado (CI/CD)

### 1. Configurar secrets no GitHub:

Vá em: `Settings` → `Secrets and variables` → `Actions`

**Repository secrets necessários:**
```
VPS_SSH_PRIVATE_KEY: -----BEGIN OPENSSH PRIVATE KEY-----
sua_chave_ssh_privada_aqui
-----END OPENSSH PRIVATE KEY-----

DOCKER_HUB_USERNAME: seu_usuario_dockerhub

DOCKER_HUB_PASSWORD: seu_token_dockerhub
```

### 2. Gerar chave SSH (se não tiver):
```bash
# No seu computador local
ssh-keygen -t rsa -b 4096 -C "deploy@api-consulta-v2"

# Copiar chave pública para VPS
ssh-copy-id -i ~/.ssh/id_rsa.pub root@69.62.103.163

# Adicionar chave privada nos secrets do GitHub
cat ~/.ssh/id_rsa
```

### 3. Fazer push para main:
```bash
git add .
git commit -m "feat: Configuração para deploy VPS"
git push origin main
```

O pipeline será executado automaticamente e fará deploy na VPS!

## 📊 Monitoramento

### URLs disponíveis após deploy:
- **API**: http://69.62.103.163:8000
- **Documentação**: http://69.62.103.163:8000/docs
- **Health Check**: http://69.62.103.163:8000/health
- **Métricas**: http://69.62.103.163:8000/metrics
- **Prometheus**: http://69.62.103.163:9090

### Comandos úteis para monitoramento:
```bash
# Status dos containers
ssh root@69.62.103.163 'cd /opt/api-consulta-v2 && docker compose ps'

# Logs da API
ssh root@69.62.103.163 'cd /opt/api-consulta-v2 && docker compose logs api --tail=50'

# Reiniciar API
ssh root@69.62.103.163 'cd /opt/api-consulta-v2 && docker compose restart api'

# Atualizar para nova versão
ssh root@69.62.103.163 'cd /opt/api-consulta-v2 && docker compose pull && docker compose up -d'
```

## 🔧 Troubleshooting

### Problema: API não responde
```bash
# Verificar logs
ssh root@69.62.103.163 'cd /opt/api-consulta-v2 && docker compose logs api'

# Verificar se container está rodando
ssh root@69.62.103.163 'docker ps'

# Reiniciar containers
ssh root@69.62.103.163 'cd /opt/api-consulta-v2 && docker compose restart'
```

### Problema: Erro de conexão SSH no pipeline
1. Verificar se a chave SSH está correta nos secrets
2. Verificar se a chave pública está na VPS: `~/.ssh/authorized_keys`
3. Testar conexão manual: `ssh root@69.62.103.163`

### Problema: Erro ao baixar imagem Docker
1. Verificar se `DOCKER_HUB_USERNAME` e `DOCKER_HUB_PASSWORD` estão corretos
2. Verificar se a imagem existe no Docker Hub
3. Fazer login manual: `docker login`

## 🔒 Segurança

### Recomendações de segurança para produção:
1. **Firewall**: Liberar apenas portas necessárias
2. **SSL/TLS**: Configurar certificado HTTPS
3. **Backup**: Configurar backup regular do MongoDB
4. **Updates**: Manter sistema operacional atualizado
5. **Logs**: Configurar rotação de logs
6. **Monitoring**: Configurar alertas de erro

### Configurar SSL (opcional):
```bash
# Instalar Certbot
sudo apt update
sudo apt install certbot

# Gerar certificado
sudo certbot certonly --standalone -d seu-dominio.com

# Configurar nginx com SSL (editar nginx.conf)
```
