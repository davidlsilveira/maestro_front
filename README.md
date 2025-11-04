# Maestro Front - Streamlit Dashboard

Dashboard web para gerenciamento do Maestro WBS.

## 📋 Visão Geral

Aplicação Streamlit para visualização e gerenciamento de:
- Épicos e WBS
- Templates e prompts
- Tags e ações
- Análises e métricas

## 🚀 Início Rápido

### Local Development

```bash
# Instalar dependências
pip install -r requirements.txt

# Configurar .env
cp .env.example .env
# Editar .env com suas credenciais

# Executar aplicação
streamlit run app.py
```

### Docker

```bash
# Build e executar
docker-compose up --build

# Acessar
http://localhost:8501
```

## 🔧 Configuração

### Variáveis de Ambiente (.env)

```bash
# Database
POSTGRES_HOST=your_host
POSTGRES_PORT=5432
POSTGRES_DB=maestro
POSTGRES_USER=your_user
POSTGRES_PASSWORD=your_password
DATABASE_URL=postgresql://user:pass@host:5432/maestro

# Client
DEFAULT_CLIENT_ID=1

# Optional
OPENAI_API_KEY=
AZURE_DEVOPS_TOKEN=
JIRA_API_KEY=
```

## 📦 Deployment para Produção (SaveInCloud)

### 1. Criar Repositório GitHub

```bash
# No GitHub, criar novo repositório: maestro-front
# https://github.com/davidlsilveira/maestro-front

# Configurar remote
cd maestro_front
git remote add origin https://github.com/davidlsilveira/maestro-front.git
git branch -M main
git push -u origin main
```

### 2. Deploy no Servidor

```bash
# SSH no servidor
ssh root@node228157-env-3783466.sp1.br.saveincloud.net.br -p 3022

# Criar diretório e clonar
cd /root
git clone https://github.com/davidlsilveira/maestro-front.git
cd maestro-front

# Configurar .env
nano .env
# Copiar configurações de produção

# Build e iniciar
docker-compose up -d --build

# Verificar status
docker-compose ps
docker-compose logs -f maestro-front
```

### 3. Configurar Acesso Externo

**SaveInCloud PaaS:**
- Acessar painel: https://app.sp1.br.saveincloud.net.br
- Environment: node228157-env-3783466
- Adicionar endpoint: porta 8501 → porta pública
- Obter URL externa: `http://node228157-env-3783466.sp1.br.saveincloud.net.br:XXXX`

**Alternativa com Nginx Reverse Proxy:**
```nginx
server {
    listen 80;
    server_name maestro-front.yourdomain.com;

    location / {
        proxy_pass http://localhost:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## 🔄 Updates

```bash
# No servidor
cd /root/maestro-front
git pull
docker-compose down
docker-compose up -d --build
```

## 🏗️ Estrutura

```
maestro_front/
├── app.py                 # Entry point
├── components/            # UI components
│   ├── table_epicos.py
│   ├── form_epico.py
│   ├── tags_list.py
│   └── ...
├── database/              # Database connection
│   └── connection.py
├── repositories/          # Data access layer
│   ├── epicos_repository.py
│   ├── tags_repository.py
│   └── ...
├── observability/         # Metrics and monitoring
│   └── metrics.py
├── assets/                # Static files (CSS, SVG, images)
│   ├── style.css
│   └── gears...
├── .streamlit/            # Streamlit config
│   └── config.toml
├── Dockerfile
├── docker-compose.yml
└── requirements.txt
```

## 📊 Observability

A aplicação expõe métricas Prometheus em `/metrics` (via prometheus_client).

**Métricas disponíveis:**
- Contadores de páginas visitadas
- Duração de renderização
- Eventos de usuário

**Integração com Prometheus:**
```yaml
# prometheus.yml
scrape_configs:
  - job_name: 'maestro-front'
    static_configs:
      - targets: ['maestro-front:8501']
```

## 🔗 Integração com Backend

O frontend se conecta ao mesmo banco PostgreSQL que o backend Maestro.

**Backend API:** http://localhost:8000 (maestro-api)
**Frontend Dashboard:** http://localhost:8501 (maestro-front)

## 📝 Comandos Úteis

```bash
# Logs
docker-compose logs -f maestro-front

# Reiniciar
docker-compose restart maestro-front

# Rebuild completo
docker-compose down
docker-compose build --no-cache maestro-front
docker-compose up -d maestro-front

# Acessar container
docker-compose exec maestro-front bash

# Verificar conexão com banco
docker-compose exec maestro-front python test_db.py
```

## 🐛 Troubleshooting

### Erro de Conexão com Banco

```bash
# Verificar DATABASE_URL no .env
cat .env | grep DATABASE_URL

# Testar conexão
docker-compose exec maestro-front python test_db.py
```

### Porta 8501 Já em Uso

```bash
# Verificar processo usando a porta
netstat -ano | findstr :8501  # Windows
lsof -i :8501                 # Linux/Mac

# Matar processo
kill -9 <PID>

# Ou alterar porta no docker-compose.yml
ports:
  - "8502:8501"  # Expor na 8502 localmente
```

## 📚 Tecnologias

- **Streamlit** 1.37.0 - Framework web
- **Pandas** 2.2.2 - Manipulação de dados
- **psycopg2** 2.9.9 - PostgreSQL driver
- **prometheus-client** 0.20.0 - Métricas
- **Docker** - Containerização

## 🔒 Segurança

- Nunca commitar `.env` com credenciais reais
- Usar secrets do Docker para produção
- Configurar CORS apropriadamente
- SSL/TLS para acesso externo (nginx)

## 📄 Licença

Proprietário - Sempre IT

---

**Versão:** 1.0.0
**Última Atualização:** 2025-11-04
**Maintainer:** David Silveira
