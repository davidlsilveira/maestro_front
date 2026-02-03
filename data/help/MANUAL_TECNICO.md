# Manual Técnico - Maestro WBS

**Versão:** 4.2.0
**Atualizado:** Fevereiro 2026

---

## Pergunta: O que o MCP faz no sistema?

**Resposta Rápida:**

O **MCP Server** (Model Context Protocol Server) é um servidor REST API na porta 8100 que permite que Inteligências Artificiais (como Claude e GPT-4) interajam com o Maestro automaticamente.

**O que o MCP faz especificamente:**

1. **Permite que IAs leiam dados do Azure DevOps/Jira** - A IA pode buscar Epics, Features, Stories e Tasks automaticamente
2. **Permite que IAs criem work items** - A IA pode criar Features, Stories e Tasks no Azure DevOps sem intervenção humana
3. **Permite que IAs busquem conhecimento** - A IA pode fazer busca semântica na base de conhecimento para encontrar projetos similares
4. **Permite que IAs consultem templates** - A IA pode obter templates de WBS e configurações de clientes
5. **Automatiza geração completa de WBS** - Agentes de IA podem gerar backlog completo de forma autônoma, aprendendo com projetos anteriores

**Em resumo:** O MCP Server transforma o Maestro em uma plataforma que agentes de IA podem usar como "ferramenta", permitindo automação inteligente e autônoma de todo o ciclo de geração de WBS.

**Porta:** 8100 (HTTP REST API)
**Ferramentas disponíveis:** 10 tools (Azure DevOps, Knowledge Base, Database)
**Versão MCP:** 1.0.0

---

## Índice

1. [Visão Geral da Arquitetura](#1-visão-geral-da-arquitetura)
2. [Estrutura do Projeto](#2-estrutura-do-projeto)
3. [Componentes Principais](#3-componentes-principais)
4. [Banco de Dados](#4-banco-de-dados)
5. [Sistema de Tags e Ações](#5-sistema-de-tags-e-ações)
6. [Fluxo de Processamento](#6-fluxo-de-processamento)
7. [Integrações Externas](#7-integrações-externas)
8. [Sistema de Prompts](#8-sistema-de-prompts)
9. [Base de Conhecimento](#9-base-de-conhecimento)
10. [Code Review](#10-code-review)
11. [Geração de Testes](#11-geração-de-testes)
12. [Multi-Tenancy](#12-multi-tenancy)
13. [Configuração e Deploy](#13-configuração-e-deploy)
14. [Troubleshooting](#14-troubleshooting)
15. [API Reference](#15-api-reference)

---

## 1. Visão Geral da Arquitetura

### 1.1 Arquitetura de Alto Nível

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           AZURE DEVOPS / JIRA                            │
│                                                                          │
│   Epic ──► Webhook ──► [Tag Detectada] ──► Resultado postado            │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                              MAESTRO API                                 │
│                           (FastAPI - Port 8000)                          │
│                                                                          │
│   ┌─────────────┐    ┌─────────────┐    ┌─────────────┐                 │
│   │  /webhook/  │    │   /health   │    │  /metrics   │                 │
│   │    azure    │    │             │    │             │                 │
│   └──────┬──────┘    └─────────────┘    └─────────────┘                 │
│          │                                                               │
│          ▼                                                               │
│   ┌─────────────────────────────────────────────────────────────────┐   │
│   │                      Redis Streams (Event Bus)                   │   │
│   │                      Stream: maestro_events                      │   │
│   └─────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                           EVENT CONSUMER                                 │
│                     (apps/worker/event_consumer.py)                      │
│                                                                          │
│   ┌─────────────────────────────────────────────────────────────────┐   │
│   │                       Tag Detector                               │   │
│   │                 (apps/worker/tasks/tag_detector.py)              │   │
│   │                                                                  │   │
│   │   ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │   │
│   │   │ WBS Generator│  │ Code Reviewer│  │Test Generator│          │   │
│   │   └──────────────┘  └──────────────┘  └──────────────┘          │   │
│   └─────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                           PERSISTÊNCIA                                   │
│                                                                          │
│   ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐    │
│   │   PostgreSQL    │    │     Redis       │    │    OpenAI       │    │
│   │   + pgvector    │    │    (Cache)      │    │   (GPT-4)       │    │
│   └─────────────────┘    └─────────────────┘    └─────────────────┘    │
└─────────────────────────────────────────────────────────────────────────┘
```

### 1.2 Padrão de Comunicação

O sistema usa **Event-Driven Architecture** com Redis Streams:

1. **Webhook** recebe evento do Azure DevOps
2. **API** publica evento no Redis Stream `maestro_events`
3. **Event Consumer** consome eventos e processa
4. **Tag Detector** identifica ações e executa workflows
5. **Resultados** são postados de volta no Azure DevOps

### 1.3 Tecnologias Utilizadas

| Componente | Tecnologia | Versão |
|------------|------------|--------|
| API | FastAPI | 0.104.1 |
| Worker | Python asyncio | 3.11+ |
| Banco de Dados | PostgreSQL + pgvector | 15+ |
| Cache/Events | Redis | 7.0+ |
| IA | OpenAI GPT-4 | API |
| Containers | Docker Compose | 2.0+ |

---

## 2. Estrutura do Projeto

### 2.1 Organização de Diretórios

```
maestro/
├── apps/
│   ├── api/                          # FastAPI Application
│   │   ├── main.py                   # Entry point da API
│   │   ├── routers/
│   │   │   ├── webhook.py            # Endpoints de webhook
│   │   │   ├── automation.py         # Endpoints de automação
│   │   │   └── health.py             # Health checks
│   │   └── middleware/
│   │       ├── cors_security.py      # CORS configuration
│   │       └── rate_limiting.py      # Rate limiting
│   │
│   ├── worker/                       # Background Workers
│   │   ├── event_consumer.py         # Redis Stream consumer
│   │   ├── main_enterprise.py        # Worker entry point
│   │   └── tasks/
│   │       ├── tag_detector.py       # Detecção de tags e routing
│   │       ├── wbs_generator.py      # Geração de WBS
│   │       ├── code_reviewer.py      # Code Review
│   │       ├── test_case_generator.py    # Geração de Test Cases
│   │       ├── test_automation_generator.py  # Scripts de automação
│   │       ├── publish.py            # Azure DevOps Client
│   │       └── dlp.py                # Data Loss Prevention
│   │
│   └── backoffice/                   # Streamlit Frontend
│       └── main.py
│
├── packages/
│   ├── common/                       # Shared utilities
│   │   ├── logging.py                # Logging configurado
│   │   ├── key_vault.py              # Azure Key Vault
│   │   ├── prompt_manager.py         # Gestão de prompts
│   │   ├── security.py               # Segurança
│   │   └── storage.py                # Blob storage
│   │
│   └── db/                           # Database
│       ├── base.py                   # Connection pool
│       ├── models.py                 # SQLAlchemy models
│       └── migrations/               # SQL migrations
│
├── tests/
│   ├── unit/                         # Unit tests
│   ├── integration/                  # Integration tests
│   ├── performance/                  # Load tests
│   └── security/                     # Security tests
│
├── help/                             # Documentação
│   ├── MANUAL_USUARIO.md
│   └── MANUAL_TECNICO.md
│
├── docker-compose.local.yml          # Docker para desenvolvimento
├── requirements.txt                  # Dependências Python
├── .env                              # Variáveis de ambiente (não commitar)
└── CLAUDE.md                         # Instruções para Claude Code
```

### 2.2 Arquivos Críticos

| Arquivo | Função | Criticidade |
|---------|--------|-------------|
| `apps/api/main.py` | Entry point da API | Alta |
| `apps/worker/event_consumer.py` | Consumidor de eventos | Alta |
| `apps/worker/tasks/tag_detector.py` | Roteamento de ações | Crítica |
| `packages/db/base.py` | Pool de conexões | Alta |
| `packages/common/logging.py` | Sistema de logs | Média |

---

## 3. Componentes Principais

### 3.1 FastAPI Application (apps/api/main.py)

```python
# Estrutura principal da API
from fastapi import FastAPI
from apps.api.routers import webhook, automation, health
from apps.api.middleware.cors_security import setup_cors
from apps.api.middleware.rate_limiting import RateLimitMiddleware

app = FastAPI(
    title="Maestro WBS API",
    version="4.0.0",
    description="API de automação de Work Breakdown Structure"
)

# Middlewares
setup_cors(app)
app.add_middleware(RateLimitMiddleware)

# Routers
app.include_router(webhook.router, prefix="/webhook", tags=["Webhooks"])
app.include_router(automation.router, prefix="/automation", tags=["Automation"])
app.include_router(health.router, tags=["Health"])
```

**Endpoints principais:**

| Endpoint | Método | Descrição |
|----------|--------|-----------|
| `/webhook/azure` | POST | Recebe webhooks do Azure DevOps |
| `/webhook/jira` | POST | Recebe webhooks do Jira |
| `/health` | GET | Health check |
| `/metrics` | GET | Métricas Prometheus |
| `/automation/code-review` | POST | Trigger manual de code review |

### 3.2 Event Consumer (apps/worker/event_consumer.py)

O Event Consumer usa Redis Streams para processamento assíncrono:

```python
class MaestroEventConsumer:
    """Consumidor de eventos do Redis Stream."""

    def __init__(self):
        self.redis = redis.Redis(host=REDIS_HOST, port=REDIS_PORT)
        self.stream_name = "maestro_events"
        self.consumer_group = "maestro_workers"
        self.consumer_name = f"worker_{os.getpid()}"

    async def consume_events(self):
        """Loop principal de consumo de eventos."""
        while True:
            events = self.redis.xreadgroup(
                groupname=self.consumer_group,
                consumername=self.consumer_name,
                streams={self.stream_name: '>'},
                count=10,
                block=5000
            )

            for stream, messages in events:
                for msg_id, data in messages:
                    await self.process_event(data)
                    self.redis.xack(self.stream_name, self.consumer_group, msg_id)
```

**Formato do evento:**

```json
{
    "event_type": "workitem.updated",
    "work_item_id": 12345,
    "work_item_type": "Epic",
    "tags": "Maestro Executar;Priority High",
    "id_cliente": 1,
    "integracao_config": {
        "organization": "my-org",
        "project": "my-project",
        "pat": "***"
    },
    "timestamp": "2026-01-12T10:30:00Z"
}
```

### 3.3 Tag Detector (apps/worker/tasks/tag_detector.py)

O Tag Detector é o **coração do sistema**. Ele:
1. Identifica tags Maestro no work item
2. Busca a ação correspondente no banco
3. Executa o workflow apropriado
4. Posta resultados no Azure DevOps

```python
class TagDetector:
    """Detecta tags e executa ações correspondentes."""

    def __init__(self, id_cliente: int, integracao_config: Dict = None):
        self.id_cliente = id_cliente
        self.integracao_config = integracao_config

    async def processar_work_item(self, work_item_id: int, tags: str) -> Dict:
        """
        Processa um work item baseado em suas tags.

        Args:
            work_item_id: ID do work item no Azure DevOps
            tags: String de tags separadas por ";"

        Returns:
            Dict com resultado do processamento
        """
        # 1. Parsear tags
        tag_list = [t.strip() for t in tags.split(";") if t.strip()]

        # 2. Buscar tags Maestro no banco
        tags_maestro = self._buscar_tags_maestro(tag_list)

        # 3. Para cada tag, executar ação
        for tag in tags_maestro:
            acao = self._buscar_acao_para_tag(tag["id_tag"])
            if acao:
                await self._executar_acao(work_item_id, acao)

        return {"sucesso": True}
```

**Ações suportadas:**

| Código Ação | Handler | Descrição |
|-------------|---------|-----------|
| `full_execution` | `_executar_wbs_completa()` | WBS completa |
| `pre_analise` | `_executar_pre_analise()` | Pré-análise |
| `code_review` | `_executar_code_review()` | Code Review |
| `test_case_generation` | `_executar_geracao_testes()` | Gerar Test Cases |
| `test_automation_selenium` | `_executar_automacao()` | Script Selenium |
| `test_automation_playwright` | `_executar_automacao()` | Script Playwright |

---

## 4. Banco de Dados

### 4.1 Diagrama ER (Simplificado)

```
┌─────────────┐      ┌─────────────┐      ┌─────────────┐
│  clientes   │──────│   epicos    │──────│ wbs_geradas │
└─────────────┘      └─────────────┘      └─────────────┘
       │                    │
       │                    │
       ▼                    ▼
┌─────────────┐      ┌─────────────────┐
│    tags     │      │  code_reviews   │
└─────────────┘      └─────────────────┘
       │
       ▼
┌─────────────┐      ┌─────────────┐
│  tag_acoes  │──────│    acoes    │
└─────────────┘      └─────────────┘
       │
       ▼
┌─────────────┐
│   prompts   │
└─────────────┘
```

### 4.2 Tabelas Principais

#### clientes
```sql
CREATE TABLE clientes (
    id_cliente SERIAL PRIMARY KEY,
    nome VARCHAR(255) NOT NULL,
    codigo VARCHAR(50) UNIQUE NOT NULL,
    config JSONB DEFAULT '{}',      -- Configurações específicas
    ativo BOOLEAN DEFAULT TRUE,
    criado_em TIMESTAMP DEFAULT NOW()
);

-- Exemplo de config:
{
    "azure_devops": {
        "organization": "my-org",
        "project": "my-project",
        "pat": "encrypted_pat"
    },
    "openai": {
        "model": "gpt-4-turbo",
        "max_tokens": 4000
    }
}
```

#### tags
```sql
CREATE TABLE tags (
    id_tag SERIAL PRIMARY KEY,
    id_cliente INT REFERENCES clientes(id_cliente),
    nome VARCHAR(100) NOT NULL,           -- "Maestro Executar"
    descricao TEXT,
    cor_hex VARCHAR(7),                   -- "#3498db"
    ativo BOOLEAN DEFAULT TRUE,
    UNIQUE(id_cliente, nome)
);
```

#### acoes
```sql
CREATE TABLE acoes (
    id_acao SERIAL PRIMARY KEY,
    codigo VARCHAR(50) UNIQUE NOT NULL,   -- "full_execution", "code_review"
    nome VARCHAR(100) NOT NULL,
    descricao TEXT,
    tipo VARCHAR(50),                     -- "wbs", "ai_analysis", "automation"
    ativo BOOLEAN DEFAULT TRUE
);
```

#### tag_acoes (Associação Tag ↔ Ação)
```sql
CREATE TABLE tag_acoes (
    id_tag_acao SERIAL PRIMARY KEY,
    id_tag INT REFERENCES tags(id_tag),
    id_acao INT REFERENCES acoes(id_acao),
    id_prompt INT REFERENCES prompts(id_prompt),
    prioridade INT DEFAULT 1,
    parametros JSONB DEFAULT '{}',
    ativo BOOLEAN DEFAULT TRUE,
    UNIQUE(id_tag, id_acao)
);
```

#### epicos
```sql
CREATE TABLE epicos (
    id_epico SERIAL PRIMARY KEY,
    id_cliente INT REFERENCES clientes(id_cliente),
    azure_id INT NOT NULL,                -- ID no Azure DevOps
    titulo VARCHAR(500),
    descricao_inicial TEXT,               -- Descrição original
    discussao TEXT,                       -- Pré-análise gerada pela IA
    origem VARCHAR(50) CHECK (origem IN ('Epic', 'Feature')),
    status VARCHAR(50) DEFAULT 'novo',
    criado_em TIMESTAMP DEFAULT NOW(),
    atualizado_em TIMESTAMP DEFAULT NOW(),
    UNIQUE(id_cliente, azure_id)
);
```

#### code_reviews
```sql
CREATE TABLE code_reviews (
    id_review SERIAL PRIMARY KEY,
    id_cliente INT REFERENCES clientes(id_cliente),

    -- Work Item
    work_item_id INT NOT NULL,
    work_item_type VARCHAR(50),           -- Task, Story, Bug
    work_item_title TEXT,

    -- Código
    codigo_original TEXT NOT NULL,
    linguagem VARCHAR(50),
    linhas_codigo INT,

    -- Scores (0-10)
    score_geral DECIMAL(3,1),
    score_seguranca DECIMAL(3,1),
    score_performance DECIMAL(3,1),
    score_qualidade DECIMAL(3,1),
    score_manutencao DECIMAL(3,1),

    -- Análises (JSONB)
    analise_seguranca JSONB,
    analise_performance JSONB,
    analise_qualidade JSONB,
    analise_stress JSONB,
    sugestoes_melhoria JSONB,

    -- Vulnerabilidades
    vulnerabilidades_criticas INT DEFAULT 0,
    vulnerabilidades_altas INT DEFAULT 0,
    vulnerabilidades_medias INT DEFAULT 0,
    vulnerabilidades_baixas INT DEFAULT 0,

    -- Métricas IA
    tokens_input INT,
    tokens_output INT,
    custo_estimado DECIMAL(10,6),
    modelo_usado VARCHAR(50),

    -- Status
    status VARCHAR(50) DEFAULT 'processando',
    postado_work_item BOOLEAN DEFAULT FALSE,

    criado_em TIMESTAMP DEFAULT NOW()
);

-- Índices para performance
CREATE INDEX idx_code_reviews_cliente ON code_reviews(id_cliente);
CREATE INDEX idx_code_reviews_work_item ON code_reviews(work_item_id);
CREATE INDEX idx_code_reviews_status ON code_reviews(status);
```

#### prompts
```sql
CREATE TABLE prompts (
    id_prompt SERIAL PRIMARY KEY,
    id_cliente INT REFERENCES clientes(id_cliente),
    contexto VARCHAR(50) NOT NULL,        -- "wbs_geracao", "code_review"
    nome VARCHAR(255) NOT NULL,
    template_prompt TEXT NOT NULL,
    variaveis_esperadas JSONB,
    versao VARCHAR(20) DEFAULT '1.0.0',
    ativo BOOLEAN DEFAULT TRUE,
    temperatura DECIMAL(2,1) DEFAULT 0.7,
    max_tokens INT DEFAULT 4000,
    UNIQUE(id_cliente, contexto, versao)
);

-- Contextos válidos:
CHECK (contexto IN (
    'epico_criacao', 'epico_revisao',
    'feature_criacao', 'feature_revisao',
    'full_execution', 'pre_analise',
    'story_criacao', 'task_criacao',
    'wbs_geracao', 'wbs_requisitos',
    'test_case_generation', 'test_automation_selenium',
    'test_automation_playwright', 'test_automation_cypress',
    'code_review'
))
```

### 4.3 Base de Conhecimento (pgvector)

```sql
-- Extensão para busca vetorial
CREATE EXTENSION IF NOT EXISTS vector;

-- Embeddings para similaridade
CREATE TABLE embeddings (
    id_embedding SERIAL PRIMARY KEY,
    id_cliente INT REFERENCES clientes(id_cliente),
    tipo VARCHAR(50),                     -- "wbs_contexto", "epic_descricao"
    referencia_id INT,                    -- ID do objeto relacionado
    embedding vector(1536),               -- OpenAI ada-002 = 1536 dimensões
    texto_original TEXT,
    criado_em TIMESTAMP DEFAULT NOW()
);

-- Índice para busca por similaridade
CREATE INDEX idx_embeddings_vector ON embeddings
    USING ivfflat (embedding vector_cosine_ops)
    WITH (lists = 100);

-- Busca por similaridade
SELECT
    referencia_id,
    texto_original,
    1 - (embedding <=> query_embedding) as similaridade
FROM embeddings
WHERE tipo = 'wbs_contexto'
  AND id_cliente = 1
ORDER BY embedding <=> query_embedding
LIMIT 5;
```

### 4.4 Connection Pool

```python
# packages/db/base.py
from contextlib import contextmanager
import psycopg2
from psycopg2.pool import ThreadedConnectionPool
from psycopg2.extras import RealDictCursor

# Pool de conexões (singleton)
_pool = None

def get_pool():
    global _pool
    if _pool is None:
        _pool = ThreadedConnectionPool(
            minconn=2,
            maxconn=20,
            host=os.getenv("DB_HOST", "localhost"),
            port=os.getenv("DB_PORT", 5432),
            database=os.getenv("DB_NAME", "maestro"),
            user=os.getenv("DB_USER", "maestro"),
            password=os.getenv("DB_PASSWORD"),
            cursor_factory=RealDictCursor
        )
    return _pool

@contextmanager
def get_db_connection():
    """Context manager para conexão do pool."""
    pool = get_pool()
    conn = pool.getconn()
    try:
        yield conn
    finally:
        pool.putconn(conn)

# Uso
with get_db_connection() as db:
    with db.cursor() as cur:
        cur.execute("SELECT * FROM clientes WHERE id_cliente = %s", (1,))
        cliente = cur.fetchone()
```

---

## 5. Sistema de Tags e Ações

### 5.1 Fluxo de Detecção

```
Work Item com Tags
       │
       ▼
┌──────────────────┐
│ Parsear tags do  │
│ campo "Tags"     │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ Buscar tags no   │
│ banco (tabela    │
│ tags)            │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ Para cada tag    │
│ encontrada:      │
│ buscar ação em   │
│ tag_acoes        │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ Executar ação    │
│ correspondente   │
└──────────────────┘
```

### 5.2 Configuração de Tags

```sql
-- Exemplo: Configurar tag "Maestro Code Review"

-- 1. Criar a tag
INSERT INTO tags (id_cliente, nome, descricao, cor_hex)
VALUES (1, 'Maestro Code Review', 'Análise automática de código', '#e74c3c');

-- 2. Verificar se ação existe
SELECT * FROM acoes WHERE codigo = 'code_review';

-- 3. Associar tag com ação
INSERT INTO tag_acoes (id_tag, id_acao, id_prompt, parametros)
SELECT
    t.id_tag,
    a.id_acao,
    p.id_prompt,
    '{"dimensoes": ["seguranca", "performance", "qualidade"]}'::jsonb
FROM tags t, acoes a, prompts p
WHERE t.nome = 'Maestro Code Review'
  AND a.codigo = 'code_review'
  AND p.contexto = 'code_review';
```

### 5.3 Adicionar Nova Tag/Ação

**Passo 1: Criar a ação (se não existir)**
```sql
INSERT INTO acoes (codigo, nome, descricao, tipo)
VALUES (
    'minha_nova_acao',
    'Minha Nova Ação',
    'Descrição da ação',
    'ai_analysis'
);
```

**Passo 2: Criar o prompt**
```sql
INSERT INTO prompts (id_cliente, contexto, nome, template_prompt, variaveis_esperadas)
VALUES (
    1,
    'minha_nova_acao',
    'Prompt para Minha Ação',
    'Você é um especialista em... {variavel1}... {variavel2}',
    '{"variavel1": "string", "variavel2": "string"}'::jsonb
);
```

**Passo 3: Criar a tag**
```sql
INSERT INTO tags (id_cliente, nome, descricao)
VALUES (1, 'Maestro Minha Acao', 'Descrição para usuário');
```

**Passo 4: Associar**
```sql
INSERT INTO tag_acoes (id_tag, id_acao, id_prompt)
SELECT t.id_tag, a.id_acao, p.id_prompt
FROM tags t, acoes a, prompts p
WHERE t.nome = 'Maestro Minha Acao'
  AND a.codigo = 'minha_nova_acao'
  AND p.contexto = 'minha_nova_acao';
```

**Passo 5: Implementar handler no tag_detector.py**
```python
async def _executar_minha_acao(self, work_item_id: int, work_item_data: Dict) -> Dict:
    """Handler para minha nova ação."""
    # Implementação
    pass
```

---

## 6. Fluxo de Processamento

### 6.1 Webhook → Processamento

```python
# apps/api/routers/webhook.py

@router.post("/azure")
async def webhook_azure(request: Request):
    """Recebe webhook do Azure DevOps."""

    # 1. Validar payload
    payload = await request.json()

    # 2. Extrair dados
    resource = payload.get("resource", {})
    work_item_id = resource.get("id")
    fields = resource.get("fields", {})

    # 3. Anti-loop: ignorar mudanças do próprio sistema
    changed_by = fields.get("System.ChangedBy", "")
    if any(bot in changed_by.lower() for bot in ["maestro", "automation", "bot"]):
        return {"status": "ignored", "reason": "system_change"}

    # 4. Publicar no Redis Stream
    event_data = {
        "event_type": "workitem.updated",
        "work_item_id": work_item_id,
        "work_item_type": fields.get("System.WorkItemType"),
        "tags": fields.get("System.Tags", ""),
        "id_cliente": detect_cliente(payload),
        "timestamp": datetime.utcnow().isoformat()
    }

    redis_client.xadd("maestro_events", event_data)

    return {"status": "accepted", "work_item_id": work_item_id}
```

### 6.2 Event Consumer → Tag Detector

```python
# apps/worker/event_consumer.py

async def process_event(self, event_data: Dict):
    """Processa evento do stream."""

    event_type = event_data.get("event_type")

    if event_type == "workitem.updated":
        # Instanciar TagDetector com contexto multi-tenant
        detector = TagDetector(
            id_cliente=event_data.get("id_cliente", 1),
            integracao_config=event_data.get("integracao_config")
        )

        # Processar work item
        result = await detector.processar_work_item(
            work_item_id=event_data.get("work_item_id"),
            tags=event_data.get("tags", "")
        )

        logger.info(f"Processamento concluído: {result}")
```

### 6.3 Tag Detector → Ações

```python
# apps/worker/tasks/tag_detector.py

async def _executar_acao(self, work_item_id: int, acao: Dict) -> Dict:
    """Executa ação baseada no código."""

    codigo = acao.get("codigo")

    # Router de ações
    handlers = {
        "full_execution": self._executar_wbs_completa,
        "pre_analise": self._executar_pre_analise,
        "code_review": self._executar_code_review,
        "test_case_generation": self._executar_geracao_testes,
        "test_automation_selenium": self._executar_automacao,
        "test_automation_playwright": self._executar_automacao,
        "test_automation_cypress": self._executar_automacao,
    }

    handler = handlers.get(codigo)
    if handler:
        return await handler(work_item_id, acao)
    else:
        logger.warning(f"Ação desconhecida: {codigo}")
        return {"sucesso": False, "erro": f"Ação {codigo} não implementada"}
```

---

## 7. Integrações Externas

### 7.1 Azure DevOps Client

```python
# apps/worker/tasks/publish.py

class AzureDevOpsClient:
    """Cliente para Azure DevOps REST API."""

    def __init__(self, org: str = None, project: str = None, pat: str = None):
        self.org = org or os.getenv("AZURE_ORG")
        self.project = project or os.getenv("AZURE_PROJECT")
        self.pat = pat or os.getenv("AZURE_PAT")
        self.base_url = f"https://dev.azure.com/{self.org}/{self.project}/_apis"
        self.headers = {
            "Content-Type": "application/json-patch+json",
            "Authorization": f"Basic {base64.b64encode(f':{self.pat}'.encode()).decode()}"
        }

    def obter_work_item(self, work_item_id: int, expand: str = None) -> Dict:
        """Obtém detalhes de um work item."""
        url = f"{self.base_url}/wit/workitems/{work_item_id}"
        params = {"api-version": "7.1"}
        if expand:
            params["$expand"] = expand

        response = requests.get(url, headers=self.headers, params=params)
        response.raise_for_status()
        return response.json()

    def criar_work_item(self, tipo: str, campos: Dict, parent_id: int = None) -> Dict:
        """Cria um novo work item."""
        url = f"{self.base_url}/wit/workitems/${tipo}"

        # Montar payload JSON Patch
        operations = []
        for campo, valor in campos.items():
            operations.append({
                "op": "add",
                "path": f"/fields/{campo}",
                "value": valor
            })

        # Adicionar parent se informado
        if parent_id:
            operations.append({
                "op": "add",
                "path": "/relations/-",
                "value": {
                    "rel": "System.LinkTypes.Hierarchy-Reverse",
                    "url": f"{self.base_url}/wit/workitems/{parent_id}"
                }
            })

        response = requests.post(
            url,
            headers=self.headers,
            params={"api-version": "7.1"},
            json=operations
        )
        response.raise_for_status()
        return response.json()

    def adicionar_comentario(self, work_item_id: int, comentario: str) -> Dict:
        """Adiciona comentário na Discussion."""
        url = f"{self.base_url}/wit/workitems/{work_item_id}/comments"

        response = requests.post(
            url,
            headers={**self.headers, "Content-Type": "application/json"},
            params={"api-version": "7.1-preview.4"},
            json={"text": comentario}
        )
        response.raise_for_status()
        return response.json()

    def adicionar_tag(self, work_item_id: int, nova_tag: str) -> Dict:
        """Adiciona tag ao work item."""
        # Primeiro, obter tags atuais
        work_item = self.obter_work_item(work_item_id)
        tags_atuais = work_item.get("fields", {}).get("System.Tags", "")

        # Adicionar nova tag
        if tags_atuais:
            novas_tags = f"{tags_atuais}; {nova_tag}"
        else:
            novas_tags = nova_tag

        # Atualizar
        return self.atualizar_work_item(work_item_id, {"System.Tags": novas_tags})
```

### 7.2 OpenAI Integration

```python
# packages/common/prompt_manager.py

class PromptManager:
    """Gerencia prompts e chamadas à IA."""

    def __init__(self, id_cliente: int):
        self.id_cliente = id_cliente
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    def buscar_prompt(self, contexto: str) -> Dict:
        """Busca prompt ativo do banco."""
        with get_db_connection() as db:
            with db.cursor() as cur:
                cur.execute("""
                    SELECT template_prompt, temperatura, max_tokens, variaveis_esperadas
                    FROM prompts
                    WHERE id_cliente = %s AND contexto = %s AND ativo = true
                    ORDER BY versao DESC LIMIT 1
                """, (self.id_cliente, contexto))
                return cur.fetchone()

    async def executar_prompt(
        self,
        contexto: str,
        variaveis: Dict,
        modelo: str = "gpt-4-turbo"
    ) -> Dict:
        """Executa prompt e retorna resultado."""

        # Buscar template
        prompt_config = self.buscar_prompt(contexto)
        if not prompt_config:
            raise ValueError(f"Prompt não encontrado: {contexto}")

        # Substituir variáveis
        template = prompt_config["template_prompt"]
        for var, valor in variaveis.items():
            template = template.replace(f"{{{var}}}", str(valor))

        # Chamar OpenAI
        response = self.client.chat.completions.create(
            model=modelo,
            messages=[
                {"role": "system", "content": "Você é um assistente especializado."},
                {"role": "user", "content": template}
            ],
            temperature=float(prompt_config.get("temperatura", 0.7)),
            max_tokens=prompt_config.get("max_tokens", 4000)
        )

        # Métricas
        return {
            "conteudo": response.choices[0].message.content,
            "tokens_input": response.usage.prompt_tokens,
            "tokens_output": response.usage.completion_tokens,
            "tokens_total": response.usage.total_tokens,
            "custo_estimado": self._calcular_custo(response.usage, modelo)
        }

    def _calcular_custo(self, usage, modelo: str) -> float:
        """Calcula custo estimado da chamada."""
        precos = {
            "gpt-4-turbo": {"input": 0.01, "output": 0.03},  # por 1K tokens
            "gpt-4o": {"input": 0.005, "output": 0.015},
            "gpt-3.5-turbo": {"input": 0.0005, "output": 0.0015}
        }
        preco = precos.get(modelo, precos["gpt-4-turbo"])
        return (
            (usage.prompt_tokens / 1000) * preco["input"] +
            (usage.completion_tokens / 1000) * preco["output"]
        )
```

### 7.3 Jira Integration

```python
# apps/worker/tasks/jira_provider.py

class JiraProvider:
    """Cliente para Jira REST API."""

    def __init__(self, url: str, email: str, token: str):
        self.base_url = url.rstrip("/")
        self.auth = (email, token)
        self.headers = {"Content-Type": "application/json"}

    def obter_issue(self, issue_key: str) -> Dict:
        """Obtém detalhes de uma issue."""
        url = f"{self.base_url}/rest/api/3/issue/{issue_key}"
        response = requests.get(url, auth=self.auth, headers=self.headers)
        response.raise_for_status()
        return response.json()

    def criar_issue(self, project_key: str, tipo: str, campos: Dict) -> Dict:
        """Cria nova issue no Jira."""
        url = f"{self.base_url}/rest/api/3/issue"
        payload = {
            "fields": {
                "project": {"key": project_key},
                "issuetype": {"name": tipo},
                **campos
            }
        }
        response = requests.post(url, auth=self.auth, headers=self.headers, json=payload)
        response.raise_for_status()
        return response.json()

    def adicionar_comentario(self, issue_key: str, comentario: str) -> Dict:
        """Adiciona comentário à issue."""
        url = f"{self.base_url}/rest/api/3/issue/{issue_key}/comment"
        payload = {
            "body": {
                "type": "doc",
                "version": 1,
                "content": [{"type": "paragraph", "content": [{"type": "text", "text": comentario}]}]
            }
        }
        response = requests.post(url, auth=self.auth, headers=self.headers, json=payload)
        response.raise_for_status()
        return response.json()
```

---

## 8. Sistema de Prompts

### 8.1 Estrutura de Prompts

Os prompts são armazenados no banco e podem ser customizados por cliente:

```sql
-- Exemplo de prompt para Code Review
INSERT INTO prompts (id_cliente, contexto, nome, template_prompt, variaveis_esperadas, temperatura)
VALUES (
    1,
    'code_review',
    'Code Review Completo',
    '# Code Review Request

## Contexto:
- Work Item: {work_item_title}
- Linguagem: {linguagem}

## Código para análise:
```{linguagem}
{codigo}
```

## Critérios de Aceite:
{criterios_aceite}

Analise o código considerando:
1. **Segurança (OWASP Top 10)**
2. **Performance**
3. **Qualidade (Clean Code, SOLID)**
4. **Stress/Carga**

Responda em JSON:
{
    "score_geral": 0-10,
    "score_seguranca": 0-10,
    "score_performance": 0-10,
    "score_qualidade": 0-10,
    "score_manutencao": 0-10,
    "vulnerabilidades": [...],
    "sugestoes": [...]
}',
    '{"codigo": "string", "linguagem": "string", "work_item_title": "string", "criterios_aceite": "array"}'::jsonb,
    0.3
);
```

### 8.2 Variáveis Disponíveis

| Contexto | Variáveis |
|----------|-----------|
| `wbs_geracao` | `descricao`, `tipo_projeto`, `exemplos_similares` |
| `code_review` | `codigo`, `linguagem`, `work_item_title`, `criterios_aceite`, `contexto_hierarquico` |
| `test_case_generation` | `story_titulo`, `story_descricao`, `criterios_aceite` |
| `test_automation_*` | `test_case_steps`, `framework`, `linguagem` |

### 8.3 Versionamento de Prompts

```sql
-- Criar nova versão de prompt
INSERT INTO prompts (id_cliente, contexto, nome, template_prompt, versao)
SELECT
    id_cliente,
    contexto,
    nome,
    'Novo template melhorado...',
    '1.1.0'
FROM prompts
WHERE contexto = 'code_review' AND versao = '1.0.0';

-- Desativar versão antiga
UPDATE prompts SET ativo = false
WHERE contexto = 'code_review' AND versao = '1.0.0';
```

---

## 9. Base de Conhecimento

### 9.1 Como Funciona

A base de conhecimento usa **embeddings vetoriais** para encontrar WBS similares:

```python
# packages/common/knowledge_base.py

class KnowledgeBase:
    """Base de conhecimento com busca semântica."""

    def __init__(self, id_cliente: int):
        self.id_cliente = id_cliente
        self.openai = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    def gerar_embedding(self, texto: str) -> List[float]:
        """Gera embedding para texto."""
        response = self.openai.embeddings.create(
            model="text-embedding-ada-002",
            input=texto[:8000]  # Limite de tokens
        )
        return response.data[0].embedding

    def salvar_wbs(self, id_wbs: int, contexto: str, wbs_estrutura: Dict, qualidade: int = 3):
        """Salva WBS na base de conhecimento."""

        # Gerar embedding do contexto
        embedding = self.gerar_embedding(contexto)

        with get_db_connection() as db:
            with db.cursor() as cur:
                # Salvar na base_conhecimento_wbs
                cur.execute("""
                    INSERT INTO base_conhecimento_wbs
                    (id_cliente, id_wbs, tipo_projeto, contexto, wbs_estrutura, qualidade)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    RETURNING id_conhecimento
                """, (self.id_cliente, id_wbs, tipo_projeto, contexto,
                      Json(wbs_estrutura), qualidade))
                id_conhecimento = cur.fetchone()["id_conhecimento"]

                # Salvar embedding
                cur.execute("""
                    INSERT INTO embeddings (id_cliente, tipo, referencia_id, embedding, texto_original)
                    VALUES (%s, 'wbs_contexto', %s, %s, %s)
                """, (self.id_cliente, id_conhecimento, embedding, contexto))

                db.commit()

    def buscar_similares(self, contexto: str, limite: int = 3, min_similaridade: float = 0.7) -> List[Dict]:
        """Busca WBS similares por contexto."""

        # Gerar embedding da query
        query_embedding = self.gerar_embedding(contexto)

        with get_db_connection() as db:
            with db.cursor() as cur:
                cur.execute("""
                    SELECT
                        bk.id_conhecimento,
                        bk.tipo_projeto,
                        bk.contexto,
                        bk.wbs_estrutura,
                        bk.qualidade,
                        bk.vezes_reutilizado,
                        1 - (e.embedding <=> %s::vector) as similaridade
                    FROM embeddings e
                    JOIN base_conhecimento_wbs bk ON e.referencia_id = bk.id_conhecimento
                    WHERE e.tipo = 'wbs_contexto'
                      AND e.id_cliente = %s
                      AND 1 - (e.embedding <=> %s::vector) >= %s
                    ORDER BY similaridade DESC, bk.qualidade DESC
                    LIMIT %s
                """, (query_embedding, self.id_cliente, query_embedding, min_similaridade, limite))

                return cur.fetchall()
```

### 9.2 Feedback Loop

```sql
-- Atualizar qualidade após feedback
UPDATE base_conhecimento_wbs
SET qualidade = qualidade + 1,
    vezes_reutilizado = vezes_reutilizado + 1
WHERE id_conhecimento = %s;

-- Query para WBS mais bem avaliadas
SELECT * FROM base_conhecimento_wbs
WHERE id_cliente = %s AND tipo_projeto = %s
ORDER BY qualidade DESC, vezes_reutilizado DESC
LIMIT 5;
```

---

## 10. Code Review

### 10.1 Arquitetura do Code Reviewer

O Code Reviewer suporta **Azure DevOps e Jira**, detectando automaticamente a plataforma.

```python
# apps/worker/tasks/code_reviewer.py

class MaestroCodeReviewer:
    """
    Analisa código com foco em segurança, performance e qualidade.

    Suporta:
    - Azure DevOps (Work Items)
    - Jira Cloud (Issues)
    """

    def __init__(
        self,
        id_cliente: int,
        integracao_config: Dict = None,
        platform: str = "azure"  # "azure" ou "jira"
    ):
        self.id_cliente = id_cliente
        self.integracao_config = integracao_config
        self.platform = platform.lower()
        self.modelo = "gpt-4o"

    async def executar_review(
        self,
        codigo: str,
        work_item_id: int,
        work_item_title: str,
        linguagem: str = None,
        criterios_aceite: List[str] = None
    ) -> Dict:
        """
        Executa code review completo.

        Etapas:
        1. Detectar linguagem (se não informada)
        2. Análise estática (regex patterns)
        3. Buscar contexto hierárquico (Story, Feature, Epic)
        4. Chamar GPT para análise profunda
        5. Consolidar resultados
        6. Salvar no banco
        7. Postar no Azure DevOps
        """

        # 1. Detectar linguagem
        if not linguagem:
            linguagem = self._detectar_linguagem(codigo)

        # 2. Análise estática
        analise_estatica = self._analise_estatica(codigo, linguagem)

        # 3. Contexto hierárquico
        contexto_hierarquico = await self._buscar_contexto_hierarquico(work_item_id)

        # 4. Análise GPT
        resultado_gpt = await self._chamar_gpt_review(
            codigo=codigo,
            linguagem=linguagem,
            analise_estatica=analise_estatica,
            criterios_aceite=criterios_aceite or contexto_hierarquico.get("criterios_aceite"),
            work_item_title=work_item_title,
            contexto_hierarquico=contexto_hierarquico
        )

        # 5. Consolidar
        resultado = self._consolidar_resultados(analise_estatica, resultado_gpt, codigo, linguagem)

        # 6. Salvar
        id_review = self._salvar_review(work_item_id, work_item_title, codigo, linguagem, resultado)

        # 7. Postar
        comentario = self._formatar_review_como_comentario(resultado, work_item_title, linguagem)
        await self._postar_review_work_item(work_item_id, comentario)

        # 8. Adicionar tag de status
        tag_status = self._determinar_tag_status(resultado["score_geral"])
        await self._adicionar_tag_status(work_item_id, tag_status)

        return resultado
```

### 10.2 Suporte Multi-Plataforma

O Code Reviewer detecta automaticamente se é Azure DevOps ou Jira:

```python
# tag_detector.py

def _executar_maestro_code_review(self, epico_id: int, work_item_data: Dict) -> Dict:
    """Executa Code Review com suporte a Azure DevOps e Jira."""

    work_item_id = work_item_data.get("id")  # Pode ser int (Azure) ou string (Jira: PROJ-123)

    # Detectar plataforma baseado no ID
    is_jira = _is_jira_work_item(work_item_id)
    platform = "jira" if is_jira else "azure"

    # Criar reviewer com plataforma detectada
    reviewer = MaestroCodeReviewer(
        id_cliente=self.id_cliente,
        integracao_config=self.integracao_config,
        platform=platform
    )

    resultado = await reviewer.executar_review(
        work_item_id=work_item_id,
        codigo=codigo,
        work_item_type=work_item_type,
        work_item_title=work_item_title
    )

    return resultado
```

**Client Factory Pattern:**

```python
def _create_client(self):
    """Cria client apropriado baseado na plataforma."""
    if self.platform == "jira":
        from packages.integrations.jira.provider import JiraProvider
        return JiraProvider(self.integracao_config)
    else:  # azure
        from apps.worker.tasks.publish import AzureDevOpsClient
        return AzureDevOpsClient(
            org=self.integracao_config.get("organization"),
            project=self.integracao_config.get("project"),
            pat=self.integracao_config.get("pat")
        )
```

**Busca de Contexto Hierárquico (Azure e Jira):**

```python
async def _buscar_contexto_hierarquico(self, work_item_id: int) -> Dict:
    """Busca contexto hierárquico em ambas plataformas."""

    client = self._create_client()

    if self.platform == "jira":
        # Jira: get_work_item retorna ProviderWorkItem
        work_item = client.get_work_item(str(work_item_id))
        work_item_type = work_item.hierarchy.name  # EPIC, STORY, TASK
        titulo = work_item.title
        descricao = work_item.description
        parent_id = work_item.parent_id

    else:  # Azure DevOps
        # Azure: obter_work_item retorna dict
        work_item = client.obter_work_item(work_item_id, expand="Relations")
        fields = work_item.get("fields", {})
        work_item_type = fields.get("System.WorkItemType")
        titulo = fields.get("System.Title")
        descricao = fields.get("System.Description")
        # Buscar parent via relations
        parent_id = self._extract_parent_from_relations(work_item.get("relations"))

    # Processar contexto...
    return contexto
```

**Postagem de Comentários:**

```python
async def _postar_review_work_item(self, work_item_id: int, comentario: str) -> bool:
    """Posta review em Azure DevOps ou Jira."""

    client = self._create_client()

    if self.platform == "jira":
        # Jira: ID é string (PROJ-123)
        comment_result = client.add_comment(str(work_item_id), comentario)
        return comment_result is not None

    else:  # Azure DevOps
        # Azure: ID é int
        resultado = client.adicionar_comentario(work_item_id, comentario)
        return resultado.get("sucesso", False)
```

**Onde Colocar o Código:**

> ⚠️ **IMPORTANTE:** O código deve ser colocado nos **comentários/discussão**, NÃO na descrição do work item.

- **Azure DevOps:** Seção **Discussion** (comentários) da Task/Story/Bug
- **Jira:** Seção **Comments** (comentários) da Issue (Task/Story/Bug)

O extrator de código (`code_extractor.py`) analisa o conteúdo dos comentários buscando blocos de código em diferentes formatos.

**Formatos Aceitos:**

1. **Markdown com code blocks:**
   ```
   \`\`\`python
   def login(user, pwd):
       return db.execute(f"SELECT * FROM users WHERE user='{user}'")
   \`\`\`
   ```

2. **Código direto:**
   ```
   def login(user, pwd):
       return db.execute(f"SELECT * FROM users WHERE user='{user}'")
   ```

3. **HTML (Azure DevOps):**
   ```html
   <pre><code>
   def login(user, pwd):
       return db.execute(f"SELECT * FROM users WHERE user='{user}'")
   </code></pre>
   ```

### 10.3 Análise Estática (Regex)

```python
def _analise_estatica(self, codigo: str, linguagem: str) -> Dict:
    """Análise estática com padrões regex."""

    vulnerabilidades = []

    # Padrões por linguagem
    patterns = {
        "python": {
            "sql_injection": [
                r'execute\s*\(\s*f["\']',           # f-string em execute
                r'execute\s*\(\s*["\'].*%s',        # % formatting
                r'cursor\.execute\s*\([^,]+\+',     # concatenação
            ],
            "command_injection": [
                r'os\.system\s*\(',
                r'subprocess\.call\s*\([^,]+shell\s*=\s*True',
                r'eval\s*\(',
                r'exec\s*\(',
            ],
            "hardcoded_secrets": [
                r'password\s*=\s*["\'][^"\']+["\']',
                r'api_key\s*=\s*["\'][^"\']+["\']',
                r'secret\s*=\s*["\'][^"\']+["\']',
            ]
        },
        "javascript": {
            "xss": [
                r'innerHTML\s*=',
                r'document\.write\s*\(',
                r'\.html\s*\([^)]*\$',
            ],
            "sql_injection": [
                r'query\s*\(\s*[`"\'].*\$\{',
            ]
        }
    }

    lang_patterns = patterns.get(linguagem, {})

    for categoria, regexes in lang_patterns.items():
        for pattern in regexes:
            matches = re.finditer(pattern, codigo, re.IGNORECASE)
            for match in matches:
                linha = codigo[:match.start()].count('\n') + 1
                vulnerabilidades.append({
                    "categoria": categoria,
                    "linha": linha,
                    "codigo": match.group()[:100],
                    "severidade": self._classificar_severidade(categoria)
                })

    return {
        "vulnerabilidades_encontradas": len(vulnerabilidades),
        "vulnerabilidades": vulnerabilidades,
        "metricas": {
            "linhas": codigo.count('\n') + 1,
            "caracteres": len(codigo)
        }
    }
```

### 10.3 Contexto Hierárquico

O Code Reviewer busca contexto completo da hierarquia:

```python
async def _buscar_contexto_hierarquico(self, work_item_id: int) -> Dict:
    """
    Busca contexto hierárquico completo.

    Task → Story (pai) → Feature (avô) → Epic (bisavô)

    Retorna critérios de aceite da Story e descrições dos níveis superiores
    para contextualizar o código sendo revisado.
    """
    contexto = {
        "story": None,
        "feature": None,
        "epic": None,
        "criterios_aceite": []
    }

    client = AzureDevOpsClient(...)
    current_id = work_item_id

    while current_id:
        work_item = client.obter_work_item(current_id, expand="Relations")
        tipo = work_item["fields"].get("System.WorkItemType")

        if tipo == "User Story":
            contexto["story"] = {
                "id": current_id,
                "titulo": work_item["fields"]["System.Title"],
                "descricao": work_item["fields"].get("System.Description", "")
            }
            # Extrair critérios de aceite
            criterios = work_item["fields"].get("Microsoft.VSTS.Common.AcceptanceCriteria", "")
            contexto["criterios_aceite"] = self._parsear_criterios(criterios)

        elif tipo == "Feature":
            contexto["feature"] = {...}

        elif tipo == "Epic":
            contexto["epic"] = {...}
            break

        # Buscar parent
        current_id = self._extrair_parent_id(work_item)

    return contexto
```

### 10.4 Formato do Comentário

```python
def _formatar_review_como_comentario(self, resultado: Dict, work_item_title: str, linguagem: str) -> str:
    """Formata review como comentário compacto."""

    score = resultado["score_geral"]

    # Determinar status
    if score >= 8:
        status = "✅ APROVADO"
    elif score >= 6:
        status = "⚠️ APROVADO COM RESSALVAS"
    else:
        status = "❌ REQUER CORREÇÕES"

    lines = [
        f"## {status}",
        f"**Score Geral: {score}/10**",
        "",
        f"🔒 Seg: {resultado['score_seguranca']}/10 | "
        f"⚡ Perf: {resultado['score_performance']}/10 | "
        f"✨ Qual: {resultado['score_qualidade']}/10 | "
        f"🔧 Mnt: {resultado['score_manutencao']}/10",
    ]

    # Vulnerabilidades
    if resultado["vulnerabilidades_criticas"] > 0:
        lines.append(f"\n**🔴 {resultado['vulnerabilidades_criticas']} vulnerabilidades críticas**")

    # Top 3 findings
    for finding in resultado.get("analise_seguranca", {}).get("findings", [])[:3]:
        lines.append(f"- [{finding['severidade']}] {finding['titulo']}")

    # Top 3 sugestões
    if resultado.get("sugestoes_melhoria"):
        lines.append("\n**💡 Sugestões:**")
        for s in resultado["sugestoes_melhoria"][:3]:
            lines.append(f"- {s[:100]}")

    lines.append("\n---")
    lines.append("_🤖 Maestro Code Reviewer_")

    return "\n".join(lines)
```

---

## 11. Geração de Testes

### 11.1 Test Case Generator

```python
# apps/worker/tasks/test_case_generator.py

class TestCaseGenerator:
    """Gera casos de teste a partir de User Stories."""

    async def gerar_test_cases(self, story_id: int) -> Dict:
        """
        Gera test cases baseado nos critérios de aceite.

        Fluxo:
        1. Buscar Story no Azure DevOps
        2. Extrair critérios de aceite
        3. Chamar GPT para gerar test cases
        4. Criar Test Cases no Azure DevOps
        5. Vincular Test Cases à Story
        """

        # 1. Buscar Story
        client = AzureDevOpsClient(...)
        story = client.obter_work_item(story_id)

        titulo = story["fields"]["System.Title"]
        descricao = story["fields"].get("System.Description", "")
        criterios = story["fields"].get("Microsoft.VSTS.Common.AcceptanceCriteria", "")

        # 2. Gerar com GPT
        prompt = self._construir_prompt(titulo, descricao, criterios)
        test_cases = await self._chamar_gpt(prompt)

        # 3. Criar no Azure DevOps
        criados = []
        for tc in test_cases:
            novo_tc = client.criar_work_item(
                tipo="Test Case",
                campos={
                    "System.Title": tc["titulo"],
                    "Microsoft.VSTS.TCM.Steps": tc["steps_xml"],
                    "System.Description": tc["descricao"]
                },
                parent_id=story_id
            )
            criados.append(novo_tc)

        return {
            "sucesso": True,
            "test_cases_criados": len(criados),
            "ids": [tc["id"] for tc in criados]
        }
```

### 11.2 Test Automation Generator

```python
# apps/worker/tasks/test_automation_generator.py

class TestAutomationGenerator:
    """Gera scripts de automação de testes."""

    frameworks_suportados = {
        "selenium": {
            "linguagem": "Python",
            "dependencias": ["selenium", "pytest", "webdriver-manager"]
        },
        "playwright": {
            "linguagem": "Python",
            "dependencias": ["playwright", "pytest", "pytest-playwright"]
        },
        "cypress": {
            "linguagem": "JavaScript",
            "dependencias": ["cypress"]
        }
    }

    async def gerar_script(self, test_case_id: int, framework: str) -> Dict:
        """
        Gera script de automação para um Test Case.

        1. Buscar Test Case no Azure DevOps
        2. Extrair steps
        3. Gerar código com GPT
        4. Postar na Discussion do Test Case
        """

        client = AzureDevOpsClient(...)
        test_case = client.obter_work_item(test_case_id)

        titulo = test_case["fields"]["System.Title"]
        steps = self._extrair_steps(test_case["fields"].get("Microsoft.VSTS.TCM.Steps", ""))

        # Gerar código
        prompt = self._construir_prompt(titulo, steps, framework)
        resultado = await self._chamar_gpt(prompt)

        # Formatar e postar
        comentario = self._formatar_script_como_comentario(
            script_code=resultado["script_code"],
            framework=framework,
            test_case_nome=titulo
        )

        client.adicionar_comentario(test_case_id, comentario)

        return {
            "sucesso": True,
            "framework": framework,
            "script_code": resultado["script_code"]
        }
```

---

## 12. Multi-Tenancy

### 12.1 Arquitetura Multi-Tenant

O Maestro suporta múltiplos clientes (tenants) com isolamento de dados:

```
┌─────────────────────────────────────────────────────────────────┐
│                        MAESTRO API                               │
│                                                                  │
│   ┌─────────────────────────────────────────────────────────┐   │
│   │                   Webhook Handler                        │   │
│   │   - Detecta cliente pelo payload                         │   │
│   │   - Busca configuração de integração                     │   │
│   │   - Passa id_cliente + integracao_config                 │   │
│   └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                        PROCESSAMENTO                             │
│                                                                  │
│   TagDetector(id_cliente=1, integracao_config={...})            │
│                                                                  │
│   - Todas as queries filtram por id_cliente                      │
│   - Prompts são específicos por cliente                          │
│   - Credenciais vêm do integracao_config                         │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                         BANCO DE DADOS                           │
│                                                                  │
│   ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│   │  Cliente 1   │  │  Cliente 2   │  │  Cliente 3   │          │
│   │  - tags      │  │  - tags      │  │  - tags      │          │
│   │  - prompts   │  │  - prompts   │  │  - prompts   │          │
│   │  - epicos    │  │  - epicos    │  │  - epicos    │          │
│   │  - reviews   │  │  - reviews   │  │  - reviews   │          │
│   └──────────────┘  └──────────────┘  └──────────────┘          │
└─────────────────────────────────────────────────────────────────┘
```

### 12.2 Tabela de Integrações (PAT Tokens)

> **IMPORTANTE:** Os tokens de autenticação (PAT) são armazenados na tabela `integracoes`, NÃO em variáveis de ambiente. Isso garante isolamento multi-tenant.

```sql
-- Tabela de integrações por cliente
CREATE TABLE integracoes (
    id_integracao SERIAL PRIMARY KEY,
    id_cliente INT REFERENCES clientes(id_cliente),
    tipo VARCHAR(50) NOT NULL,           -- 'azure_devops', 'jira', 'github'
    config JSONB NOT NULL,               -- Configurações específicas
    ativo BOOLEAN DEFAULT TRUE,
    criado_em TIMESTAMP DEFAULT NOW(),
    UNIQUE(id_cliente, tipo)
);

-- Exemplo de integração Azure DevOps
INSERT INTO integracoes (id_cliente, tipo, config) VALUES (
    1,
    'azure_devops',
    '{
        "organization": "minha-org",
        "project": "meu-projeto",
        "pat": "BASE64_ENCODED_PAT_TOKEN",
        "area_path": "MeuProjeto\\Team A",
        "iteration_path": "MeuProjeto\\Sprint 1"
    }'::jsonb
);

-- Consulta usada pelo AzureDevOpsClient
SELECT config FROM integracoes
WHERE id_cliente = %s AND tipo = 'azure_devops' AND ativo = true;
```

**Fluxo de Autenticação:**
1. Webhook recebe evento com `id_cliente`
2. Sistema busca configuração na tabela `integracoes`
3. `AzureDevOpsClient(id_cliente=X)` busca PAT do banco automaticamente
4. Todas as operações (obter, criar, comentar) usam o PAT do cliente

### 12.3 Configuração por Cliente (Legado)

```sql
-- Tabela de clientes com configurações (configurações gerais, não credenciais)
CREATE TABLE clientes (
    id_cliente SERIAL PRIMARY KEY,
    nome VARCHAR(255) NOT NULL,
    codigo VARCHAR(50) UNIQUE NOT NULL,
    config JSONB DEFAULT '{}'
);

-- Exemplo de configuração completa
UPDATE clientes SET config = '{
    "azure_devops": {
        "organization": "contoso",
        "project": "Projeto-X",
        "pat_encrypted": "encrypted_value",
        "area_path": "Projeto-X\\Team A",
        "iteration_path": "Projeto-X\\Sprint 1"
    },
    "jira": {
        "url": "https://contoso.atlassian.net",
        "email": "bot@contoso.com",
        "token_encrypted": "encrypted_value",
        "project_key": "PROJ"
    },
    "openai": {
        "model": "gpt-4-turbo",
        "max_tokens": 4000,
        "temperature": 0.7
    },
    "features": {
        "code_review": true,
        "test_generation": true,
        "wbs_generation": true
    }
}' WHERE id_cliente = 1;
```

### 12.3 Passagem de Contexto

```python
# No webhook handler
@router.post("/azure")
async def webhook_azure(request: Request):
    payload = await request.json()

    # Detectar cliente
    id_cliente = await detect_cliente_from_payload(payload)

    # Buscar configuração de integração
    integracao_config = await get_integracao_config(id_cliente, "azure_devops")

    # Publicar evento com contexto completo
    event_data = {
        "work_item_id": payload["resource"]["id"],
        "id_cliente": id_cliente,
        "integracao_config": integracao_config,
        # ...
    }

    redis_client.xadd("maestro_events", event_data)

# No processador
class TagDetector:
    def __init__(self, id_cliente: int, integracao_config: Dict = None):
        self.id_cliente = id_cliente
        self.integracao_config = integracao_config

    def _get_azure_client(self):
        """Cria client com credenciais do tenant."""
        if self.integracao_config:
            return AzureDevOpsClient(
                org=self.integracao_config.get("organization"),
                project=self.integracao_config.get("project"),
                pat=self.integracao_config.get("pat")
            )
        else:
            # Fallback para variáveis de ambiente
            return AzureDevOpsClient()
```

---

## 13. Configuração e Deploy

### 13.1 Variáveis de Ambiente

```bash
# .env (NÃO COMMITAR)

# Database
DB_HOST=localhost
DB_PORT=5432
DB_NAME=maestro
DB_USER=maestro
DB_PASSWORD=sua_senha_segura

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379

# Azure DevOps (default, pode ser sobrescrito por cliente)
AZURE_ORG=sua-organizacao
AZURE_PROJECT=seu-projeto
AZURE_PAT=seu_pat_token

# OpenAI
OPENAI_API_KEY=sk-...

# Jira (opcional)
JIRA_URL=https://sua-empresa.atlassian.net
JIRA_EMAIL=bot@empresa.com
JIRA_API_TOKEN=seu_token

# Security
SECRET_KEY=chave_secreta_para_jwt
WEBHOOK_SECRET=segredo_para_validar_webhooks

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json
```

### 13.2 Docker Compose

```yaml
# docker-compose.local.yml

version: '3.8'

services:
  maestro-api:
    build:
      context: .
      dockerfile: Dockerfile.api
    ports:
      - "8000:8000"
    environment:
      - DB_HOST=maestro-postgres
      - REDIS_HOST=maestro-redis
    depends_on:
      - maestro-postgres
      - maestro-redis
    volumes:
      - ./apps:/app/apps
      - ./packages:/app/packages
    command: uvicorn apps.api.main:app --host 0.0.0.0 --port 8000 --reload

  maestro-event-consumer:
    build:
      context: .
      dockerfile: Dockerfile.worker
    environment:
      - DB_HOST=maestro-postgres
      - REDIS_HOST=maestro-redis
    depends_on:
      - maestro-postgres
      - maestro-redis
    volumes:
      - ./apps:/app/apps
      - ./packages:/app/packages
    command: python -m apps.worker.event_consumer

  maestro-postgres:
    image: pgvector/pgvector:pg15
    environment:
      - POSTGRES_DB=maestro
      - POSTGRES_USER=maestro
      - POSTGRES_PASSWORD=${DB_PASSWORD}
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./packages/db/migrations:/docker-entrypoint-initdb.d

  maestro-redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

  maestro-backoffice:
    build:
      context: .
      dockerfile: Dockerfile.backoffice
    ports:
      - "8501:8501"
    environment:
      - API_URL=http://maestro-api:8000
    depends_on:
      - maestro-api

volumes:
  postgres_data:
  redis_data:
```

### 13.3 Comandos de Deploy

```bash
# Iniciar todos os serviços
docker-compose -f docker-compose.local.yml up -d

# Rebuild após mudanças
docker-compose -f docker-compose.local.yml up -d --build

# Ver logs
docker-compose -f docker-compose.local.yml logs -f maestro-event-consumer

# Restart serviço específico
docker-compose -f docker-compose.local.yml restart maestro-event-consumer

# Executar migrations
docker-compose -f docker-compose.local.yml exec maestro-postgres psql -U maestro -d maestro -f /docker-entrypoint-initdb.d/001_initial.sql

# Acessar banco
docker-compose -f docker-compose.local.yml exec maestro-postgres psql -U maestro -d maestro
```

### 13.4 Health Checks

```python
# apps/api/routers/health.py

@router.get("/health")
async def health_check():
    """Health check completo."""

    checks = {
        "api": "ok",
        "database": await check_database(),
        "redis": await check_redis(),
        "openai": await check_openai()
    }

    all_ok = all(v == "ok" for v in checks.values())

    return {
        "status": "healthy" if all_ok else "degraded",
        "checks": checks,
        "version": "4.0.0",
        "timestamp": datetime.utcnow().isoformat()
    }

async def check_database():
    try:
        with get_db_connection() as db:
            with db.cursor() as cur:
                cur.execute("SELECT 1")
        return "ok"
    except Exception as e:
        return f"error: {str(e)}"
```

---

## 14. Troubleshooting

### 14.1 Problemas Comuns

#### Webhook não está sendo processado

**Sintomas:** Tag adicionada mas nada acontece

**Diagnóstico:**
```bash
# 1. Verificar logs da API
docker-compose -f docker-compose.local.yml logs maestro-api | grep webhook

# 2. Verificar se evento chegou no Redis
docker-compose -f docker-compose.local.yml exec maestro-redis redis-cli
> XLEN maestro_events
> XRANGE maestro_events - + COUNT 5

# 3. Verificar logs do consumer
docker-compose -f docker-compose.local.yml logs maestro-event-consumer
```

**Soluções comuns:**
- Webhook URL incorreta no Azure DevOps
- Firewall bloqueando conexão
- Anti-loop bloqueando (mudança feita pelo próprio sistema)

#### Code Review não encontra código

**Sintomas:** "Nenhum código encontrado" ou review não executado

**Diagnóstico:**
```sql
-- Ver work item processado
SELECT * FROM code_reviews WHERE work_item_id = 12345 ORDER BY criado_em DESC LIMIT 1;
```

**Soluções:**
- ⚠️ **Código deve estar nos COMENTÁRIOS/DISCUSSÃO**, não na Description
- Usar formato de code block: \`\`\`python ... \`\`\` ou `<code>...</code>`
- Código deve ter padrões reconhecíveis (import, def, class, function, etc.)
- Verificar encoding do texto (UTF-8)
- Para Jira, usar formato `{code:python}...{code}`

#### Erro de conexão com Azure DevOps

**Sintomas:** "401 Unauthorized" ou "404 Not Found"

**Diagnóstico:**
```python
# Testar conexão manualmente
from apps.worker.tasks.publish import AzureDevOpsClient
client = AzureDevOpsClient()
print(client.obter_work_item(12345))
```

**Soluções:**
- PAT expirado - regenerar no Azure DevOps
- Permissões insuficientes - verificar escopo do PAT
- Organization/Project incorretos

### 14.2 Logs e Monitoramento

```python
# packages/common/logging.py

import logging
import json
from datetime import datetime

class StructuredLogger:
    """Logger com output JSON estruturado."""

    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)

        handler = logging.StreamHandler()
        handler.setFormatter(JsonFormatter())
        self.logger.addHandler(handler)

    def info(self, message: str, **extra):
        self.logger.info(message, extra={"custom": extra})

    def error(self, message: str, **extra):
        self.logger.error(message, extra={"custom": extra}, exc_info=True)

class JsonFormatter(logging.Formatter):
    def format(self, record):
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            "logger": record.name,
            "extra": getattr(record, "custom", {})
        }
        return json.dumps(log_data)

# Uso
logger = get_logger(__name__)
logger.info("Processando work item", work_item_id=12345, acao="code_review")
```

### 14.3 Queries de Debug

```sql
-- Últimos eventos processados
SELECT * FROM prompt_execucoes ORDER BY criado_em DESC LIMIT 10;

-- Code reviews recentes
SELECT
    id_review,
    work_item_id,
    score_geral,
    status,
    criado_em
FROM code_reviews
ORDER BY criado_em DESC
LIMIT 10;

-- Tags configuradas para cliente
SELECT
    t.nome as tag,
    a.codigo as acao,
    p.contexto as prompt
FROM tags t
JOIN tag_acoes ta ON t.id_tag = ta.id_tag
JOIN acoes a ON ta.id_acao = a.id_acao
LEFT JOIN prompts p ON ta.id_prompt = p.id_prompt
WHERE t.id_cliente = 1;

-- Verificar se prompt existe
SELECT * FROM prompts WHERE contexto = 'code_review' AND id_cliente = 1;

-- Epicos pendentes
SELECT
    azure_id,
    titulo,
    status,
    criado_em
FROM epicos
WHERE id_cliente = 1 AND status NOT IN ('concluido', 'erro')
ORDER BY criado_em DESC;
```

---

## 15. API Reference

### 15.1 Endpoints

#### POST /webhook/azure

Recebe webhooks do Azure DevOps.

**Request:**
```json
{
    "eventType": "workitem.updated",
    "resource": {
        "id": 12345,
        "fields": {
            "System.WorkItemType": "Epic",
            "System.Title": "Novo Sistema",
            "System.Tags": "Maestro Executar; Priority High",
            "System.ChangedBy": "user@company.com"
        }
    }
}
```

**Response:**
```json
{
    "status": "accepted",
    "work_item_id": 12345,
    "message": "Event queued for processing"
}
```

#### POST /webhook/jira

Recebe webhooks do Jira.

**Request:**
```json
{
    "webhookEvent": "jira:issue_updated",
    "issue": {
        "key": "PROJ-123",
        "fields": {
            "summary": "Nova Feature",
            "labels": ["Maestro Executar"]
        }
    }
}
```

#### GET /health

Health check do sistema.

**Response:**
```json
{
    "status": "healthy",
    "checks": {
        "api": "ok",
        "database": "ok",
        "redis": "ok",
        "openai": "ok"
    },
    "version": "4.0.0"
}
```

#### POST /automation/code-review

Trigger manual de code review.

**Request:**
```json
{
    "work_item_id": 12345,
    "codigo": "def hello():\n    print('Hello')",
    "linguagem": "python"
}
```

**Response:**
```json
{
    "sucesso": true,
    "id_review": 456,
    "score_geral": 7.5,
    "score_seguranca": 8.0,
    "score_performance": 7.0,
    "score_qualidade": 7.5,
    "score_manutencao": 7.5
}
```

### 15.2 Códigos de Erro

| Código | Significado |
|--------|-------------|
| 200 | Sucesso |
| 202 | Aceito para processamento |
| 400 | Payload inválido |
| 401 | Não autorizado |
| 404 | Recurso não encontrado |
| 429 | Rate limit excedido |
| 500 | Erro interno |

### 15.3 Rate Limiting

```
Limite: 100 requests/minuto por IP
Header: X-RateLimit-Remaining: 95
Header: X-RateLimit-Reset: 1704067200
```

---

## 16. MCP Server - Model Context Protocol

### O Que É o MCP Server?

O **MCP Server** (Model Context Protocol Server) é um servidor REST API que funciona como uma **ponte de integração** entre o Maestro e Inteligências Artificiais (LLMs como Claude, GPT-4, etc.).

**Em resumo:** O MCP Server expõe as funcionalidades do Maestro como "ferramentas" que agentes de IA podem usar automaticamente para executar tarefas complexas.

**Analogia:** Imagine que o Maestro é uma caixa de ferramentas e o MCP Server é um assistente que organiza essas ferramentas e as entrega para a IA quando ela precisa.

**O que o MCP faz no sistema:**
- ✅ Permite que IAs (Claude, GPT-4) leiam Epics do Azure DevOps
- ✅ Permite que IAs criem Features, Stories e Tasks automaticamente
- ✅ Permite que IAs busquem projetos similares na base de conhecimento
- ✅ Permite que IAs consultem templates e configurações
- ✅ Automatiza geração completa de WBS usando agentes autônomos

**Porta:** 8100 (HTTP REST API)

### 16.1 Visão Geral Técnica

O **MCP Server** é implementado usando FastAPI e fornece 10 ferramentas (tools) que LLMs podem chamar via HTTP POST.

**Arquitetura:**
```
┌─────────────┐
│   LLM/Agent │
│  (Claude)   │
└──────┬──────┘
       │ HTTP REST
       │
┌──────▼──────────────────────┐
│      MCP Server             │
│  (FastAPI - Port 8100)      │
├─────────────────────────────┤
│  - Azure Tools              │
│  - Knowledge Base Tools     │
│  - Database Tools           │
└──────┬──────────────────────┘
       │
       ▼
┌──────────────────────────────┐
│  Azure DevOps | PostgreSQL   │
└──────────────────────────────┘
```

**Tecnologias:**
- FastAPI (async/await)
- Pydantic (validação)
- OpenAI (embeddings)
- PostgreSQL + pgvector

### 16.2 Ferramentas Disponíveis

#### Azure DevOps Tools (4 ferramentas)

**1. get_epic_details**
```python
# Obtém Epic completo com relações
{
  "tool_name": "get_epic_details",
  "parameters": {"epic_id": 12345}
}
```

**Retorno:**
```json
{
  "success": true,
  "data": {
    "id": 12345,
    "title": "Implementar Login Social",
    "description": "...",
    "state": "New",
    "relations": [{"type": "child", "id": 12346}],
    "url": "https://dev.azure.com/..."
  }
}
```

**2. get_work_item**
```python
# Obtém qualquer work item (Epic/Feature/Story/Task)
{
  "tool_name": "get_work_item",
  "parameters": {
    "work_item_id": 12346,
    "expand": "Relations"  # opcional
  }
}
```

**3. create_feature**
```python
# Cria Feature no Azure DevOps
{
  "tool_name": "create_feature",
  "parameters": {
    "title": "Autenticação Google",
    "description": "Implementar OAuth 2.0",
    "parent_id": 12345  # opcional
  }
}
```

**4. add_comment**
```python
# Adiciona comentário a work item
{
  "tool_name": "add_comment",
  "parameters": {
    "work_item_id": 12345,
    "comment": "Análise concluída"
  }
}
```

#### Knowledge Base Tools (3 ferramentas)

**5. search_knowledge_base**
```python
# Busca semântica com pgvector
{
  "tool_name": "search_knowledge_base",
  "parameters": {
    "query": "Sistema de autenticação com login social",
    "limit": 3,  # opcional, padrão 3
    "min_similarity": 0.7  # opcional, padrão 0.7
  }
}
```

**Retorno:**
```json
{
  "success": true,
  "data": [
    {
      "id": 42,
      "epic_id": 11223,
      "project_type": "software",
      "wbs": {...},
      "quality": 4,
      "times_used": 15,
      "similarity": 0.89
    }
  ]
}
```

**6. get_wbs_by_id**
```python
# Obtém WBS específica por ID
{
  "tool_name": "get_wbs_by_id",
  "parameters": {"wbs_id": 42}
}
```

**7. save_wbs_to_knowledge**
```python
# Salva WBS na base de conhecimento
{
  "tool_name": "save_wbs_to_knowledge",
  "parameters": {
    "epic_id": 12345,
    "wbs_data": {...},
    "quality_score": 3  # opcional, 1-5
  }
}
```

#### Database Tools (3 ferramentas)

**8. get_epic_from_db**
```python
# Obtém Epic do banco local
{
  "tool_name": "get_epic_from_db",
  "parameters": {"epic_id": 12345}
}
```

**9. get_wbs_template**
```python
# Obtém template de WBS
{
  "tool_name": "get_wbs_template",
  "parameters": {
    "project_type": "software",
    "client_id": 1  # opcional
  }
}
```

**10. get_client_config**
```python
# Obtém configuração do cliente
{
  "tool_name": "get_client_config",
  "parameters": {"client_id": 1}
}
```

### 16.3 Endpoints REST

#### GET /
Informações do servidor.

**Response:**
```json
{
  "name": "maestro-mcp",
  "version": "1.0.0",
  "status": "running"
}
```

#### GET /tools
Lista todas as ferramentas disponíveis.

**Response:**
```json
{
  "tools": [
    {
      "name": "get_epic_details",
      "description": "Obtém Epic do Azure DevOps",
      "parameters": {...},
      "category": "azure"
    },
    ...
  ]
}
```

#### POST /execute
Executa uma ferramenta.

**Request:**
```json
{
  "tool_name": "get_epic_details",
  "parameters": {"epic_id": 12345}
}
```

**Response (Success):**
```json
{
  "success": true,
  "data": {...}
}
```

**Response (Error):**
```json
{
  "success": false,
  "error": "Epic não encontrado"
}
```

#### GET /health
Health check.

**Response:**
```json
{"status": "healthy"}
```

### 16.4 Configuração

**Variáveis de Ambiente:**
```bash
# Database
DATABASE_URL=postgresql://user:pass@host:port/db

# Azure DevOps
AZURE_PAT=seu_token
AZURE_ORG=sua_organizacao
AZURE_PROJECT=seu_projeto

# OpenAI (embeddings)
OPENAI_API_KEY=sua_chave

# Server (opcional)
MCP_HOST=0.0.0.0
MCP_PORT=8100
LOG_LEVEL=INFO
```

**Docker Compose:**
```yaml
maestro-mcp:
  build:
    context: .
    dockerfile: Dockerfile.mcp
  command: python -m packages.mcp.main
  ports:
    - "8100:8100"
  environment:
    - DATABASE_URL=postgresql://...
    - AZURE_PAT=...
  depends_on:
    - maestro-postgres
```

### 16.5 Integração com LLMs

#### Exemplo com Claude (Anthropic)

```python
import anthropic
import requests

client = anthropic.Anthropic(api_key="sua_chave")

# Definir ferramentas
tools = [
    {
        "name": "get_epic_details",
        "description": "Obtém Epic do Azure DevOps",
        "input_schema": {
            "type": "object",
            "properties": {
                "epic_id": {"type": "integer"}
            }
        }
    }
]

# Conversa com Claude
response = client.messages.create(
    model="claude-3-5-sonnet-20241022",
    max_tokens=1024,
    tools=tools,
    messages=[
        {"role": "user", "content": "Mostre Epic 12345"}
    ]
)

# Executar tool no MCP Server
for content in response.content:
    if content.type == "tool_use":
        result = requests.post(
            "http://localhost:8100/execute",
            json={
                "tool_name": content.name,
                "parameters": content.input
            }
        )
        print(result.json())
```

#### Exemplo com OpenAI GPT-4

```python
from openai import OpenAI

client = OpenAI(api_key="sua_chave")

tools = [
    {
        "type": "function",
        "function": {
            "name": "get_epic_details",
            "description": "Obtém Epic do Azure DevOps",
            "parameters": {
                "type": "object",
                "properties": {
                    "epic_id": {"type": "integer"}
                }
            }
        }
    }
]

response = client.chat.completions.create(
    model="gpt-4-turbo-preview",
    messages=[
        {"role": "user", "content": "Mostre Epic 12345"}
    ],
    tools=tools
)
```

### 16.6 Casos de Uso

#### 1. Agente de WBS Automático
```python
# Fluxo completo de geração de WBS
1. get_epic_details(12345)
2. search_knowledge_base("descrição do epic")
3. get_wbs_template("software")
4. Gerar WBS com LLM
5. create_feature(...) para cada feature
6. save_wbs_to_knowledge(...)
7. add_comment(12345, "WBS criada")
```

#### 2. Consultor de Projetos Similares
```python
# Busca e análise de projetos anteriores
1. search_knowledge_base(query, limit=10)
2. Análise dos resultados com LLM
3. Extração de boas práticas
4. Recomendações personalizadas
```

#### 3. Assistente de Análise de Backlog
```python
# Análise e sugestões de melhorias
1. get_epic_from_db(epic_id)
2. search_knowledge_base(contexto)
3. Análise comparativa com LLM
4. add_comment(epic_id, sugestões)
```

### 16.7 Estrutura do Código

```
packages/mcp/
├── __init__.py              # Exports
├── server.py                # FastAPI server
├── config.py                # Configuração
├── main.py                  # Entrypoint
└── tools/
    ├── __init__.py
    ├── azure_tools.py       # Azure DevOps integration
    ├── knowledge_base_tools.py  # pgvector search
    └── database_tools.py    # Database queries
```

**Classe Principal:**
```python
class MCPServer:
    def __init__(self, config: MCPConfig):
        self.app = FastAPI(...)
        self.azure_tools = AzureDevOpsTools(config)
        self.kb_tools = KnowledgeBaseTools(config)
        self.db_tools = DatabaseTools(config)

    def get_available_tools(self) -> List[Dict]:
        # Lista todas as ferramentas
        pass

    async def _execute_tool(self, tool_name: str, params: Dict) -> Any:
        # Executa ferramenta específica
        pass
```

### 16.8 Monitoramento

**Logs:**
```bash
# Docker
docker-compose -f docker-compose.local.yml logs -f maestro-mcp

# Formato estruturado
2026-01-12 14:30:00 - INFO - 🔧 Executando tool: get_epic_details
2026-01-12 14:30:01 - INFO - ✅ Epic 12345 obtido com sucesso
```

**Health Check:**
```bash
curl http://localhost:8100/health
```

**Métricas (Futuro):**
- `mcp_tool_executions_total`
- `mcp_tool_duration_seconds`
- `mcp_errors_total`

### 16.9 Segurança

**Validação:**
- Todos os parâmetros validados via Pydantic
- Type hints em 100% do código
- SQL queries parametrizadas

**Autenticação (Futuro):**
- OAuth 2.0 / API Keys
- RBAC por tenant
- Rate limiting por cliente

**Logs de Auditoria:**
- Todas as execuções logadas
- Parâmetros sanitizados
- Rastreamento por cliente

---

## 17. Segurança - Documentação Completa

Esta seção detalha todos os mecanismos de segurança implementados no Maestro para proteção de dados, comunicação e autenticação.

### 17.1 Visão Geral de Segurança

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        CAMADAS DE SEGURANÇA                              │
├─────────────────────────────────────────────────────────────────────────┤
│  🔐 TRANSPORTE          │ HTTPS/TLS 1.2+ em todas as comunicações      │
├─────────────────────────────────────────────────────────────────────────┤
│  🔑 AUTENTICAÇÃO        │ PAT Token via HTTPBasicAuth (Base64)         │
├─────────────────────────────────────────────────────────────────────────┤
│  ✅ WEBHOOK VALIDATION   │ HMAC-SHA256 com proteção timing-attack       │
├─────────────────────────────────────────────────────────────────────────┤
│  🔒 SECRETS MANAGEMENT  │ Azure Key Vault + .env fallback              │
├─────────────────────────────────────────────────────────────────────────┤
│  🛡️ SECURITY HEADERS    │ OWASP-compliant (HSTS, CSP, X-Frame-Options) │
├─────────────────────────────────────────────────────────────────────────┤
│  🌐 CORS                │ Configuração por ambiente (prod/staging/dev) │
├─────────────────────────────────────────────────────────────────────────┤
│  ⏱️ RATE LIMITING       │ Por tenant/IP com Redis                      │
└─────────────────────────────────────────────────────────────────────────┘
```

### 17.2 Autenticação com Azure DevOps

#### 17.2.1 PAT Token (Personal Access Token)

O Maestro utiliza **PAT Token via HTTPBasicAuth** para autenticação com Azure DevOps.

**Formato da autenticação:**
```python
from requests.auth import HTTPBasicAuth
import base64

# PAT é codificado em Base64 com username vazio
auth = HTTPBasicAuth("", pat_token)

# Ou manualmente
auth_string = f":{pat_token}"
auth_b64 = base64.b64encode(auth_string.encode()).decode()
headers = {"Authorization": f"Basic {auth_b64}"}
```

**Permissões mínimas requeridas para o PAT:**

| Permissão | Escopo | Uso |
|-----------|--------|-----|
| Work Items | Read & Write | Criar Features, Stories, Tasks |
| Work Items | Delete | Limpar artefatos |
| Test Management | Read & Write | Criar Test Cases |
| Build | Read | Informações de build |
| Code | Read | Code Review |

**Arquivo:** `apps/worker/tasks/azure_test_plans_client.py`

```python
class AzureTestPlansClient:
    def __init__(self, organization=None, project=None, pat=None):
        # Multi-tenant: credenciais específicas do cliente
        self.pat = pat if pat else os.getenv("AZURE_DEVOPS_PAT", os.getenv("AZURE_PAT"))

    def criar_test_case(self, ...):
        response = requests.post(
            url,
            auth=HTTPBasicAuth("", self.pat),  # Autenticação Basic
            headers=headers,
            json=payload
        )
```

### 17.3 Validação de Webhooks - HMAC-SHA256

#### 17.3.1 Implementação

O Maestro valida assinaturas HMAC-SHA256 para garantir autenticidade dos webhooks.

**Arquivo:** `apps/api/middleware/webhook_security.py`

```python
import hmac
import hashlib

class WebhookSecurity:
    @staticmethod
    def validate_azure_signature(payload: bytes, signature: str, secret: str) -> bool:
        """
        Valida assinatura HMAC SHA-256 do Azure DevOps

        IMPORTANTE: Usa hmac.compare_digest() para proteção contra timing attacks
        """
        if not signature or not secret:
            return False

        if not signature.startswith("sha256="):
            return False

        received_hash = signature[7:]  # Remove "sha256="

        # Calcula hash esperado
        expected_hash = hmac.new(
            secret.encode('utf-8'),
            payload,
            hashlib.sha256
        ).hexdigest()

        # Comparação SEGURA contra timing attacks
        return hmac.compare_digest(expected_hash, received_hash)
```

#### 17.3.2 Configuração no Azure DevOps

1. Acesse **Project Settings → Service Hooks**
2. Crie um webhook para o endpoint `/webhook/azure`
3. Configure o **Secret** (será usado para validação HMAC)
4. O Azure DevOps enviará header `X-Hub-Signature-256: sha256=<hash>`

#### 17.3.3 Validações Adicionais

```python
# Validar Content-Type
if not request.headers.get("content-type", "").startswith("application/json"):
    raise HTTPException(400, "Invalid Content-Type")

# Validar User-Agent (warning)
allowed_agents = ["Azure DevOps Services", "VSServices", "VSTS"]
user_agent = request.headers.get("user-agent", "")
if not any(agent in user_agent for agent in allowed_agents):
    logger.warning(f"User-Agent suspeito: {user_agent}")
```

### 17.4 Azure Key Vault Integration

#### 17.4.1 Arquitetura

**Arquivo:** `packages/common/key_vault.py`

```python
class KeyVaultManager:
    """Gerenciador seguro do Azure Key Vault com cache e fallback"""

    def __init__(self):
        self.client: Optional[SecretClient] = None
        self._secrets_cache: Dict[str, str] = {}
        self._initialize_client()

    def _initialize_client(self):
        vault_url = os.getenv("AZURE_KEY_VAULT_URL")

        if not vault_url:
            logger.warning("Key Vault não configurado - usando .env fallback")
            return

        # Prioridade 1: Service Principal (produção)
        client_id = os.getenv("AZURE_CLIENT_ID")
        client_secret = os.getenv("AZURE_CLIENT_SECRET")
        tenant_id = os.getenv("AZURE_TENANT_ID")

        if client_id and client_secret and tenant_id:
            credential = ClientSecretCredential(tenant_id, client_id, client_secret)
        else:
            # Prioridade 2: DefaultAzureCredential (Managed Identity)
            credential = DefaultAzureCredential()

        self.client = SecretClient(vault_url, credential)
```

#### 17.4.2 Secrets Armazenados

| Secret Name | Descrição | Fallback .env |
|-------------|-----------|---------------|
| `database-connection-string` | PostgreSQL connection | `DATABASE_URL` |
| `openai-api-key` | API Key do OpenAI | `OPENAI_API_KEY` |
| `azure-devops-pat` | Personal Access Token | `AZURE_PAT` |
| `webhook-hmac-azure` | Chave HMAC Azure | `WEBHOOK_SECRET` |
| `webhook-hmac-jira` | Chave HMAC Jira | `JIRA_WEBHOOK_SECRET` |

#### 17.4.3 Fluxo de Recuperação

```
1. Verifica cache local
2. Se não existe, busca no Key Vault
3. Se Key Vault falha, usa .env fallback
4. Armazena em cache para próximas requisições
```

### 17.5 Security Headers (OWASP)

#### 17.5.1 Headers Implementados

**Arquivo:** `apps/api/middleware/security_headers.py`

| Header | Valor | Proteção |
|--------|-------|----------|
| `X-Content-Type-Options` | `nosniff` | MIME type sniffing |
| `X-Frame-Options` | `DENY` | Clickjacking |
| `Strict-Transport-Security` | `max-age=31536000; includeSubDomains` | Force HTTPS (HSTS) |
| `Content-Security-Policy` | `default-src 'self'...` | XSS, data injection |
| `X-XSS-Protection` | `1; mode=block` | XSS (browsers antigos) |
| `Referrer-Policy` | `strict-origin-when-cross-origin` | Vazamento de referrer |
| `Permissions-Policy` | `geolocation=(), microphone=()` | APIs do browser |

#### 17.5.2 Content-Security-Policy Detalhado

```python
CSP_POLICY = {
    "default-src": "'self'",
    "script-src": "'self' 'unsafe-inline'",  # Streamlit requer
    "style-src": "'self' 'unsafe-inline'",   # CSS inline
    "img-src": "'self' data: https:",        # Imagens externas
    "connect-src": "'self' https://dev.azure.com",  # Azure DevOps API
    "frame-ancestors": "'none'",              # Previne iframe
}
```

### 17.6 CORS Configuration

#### 17.6.1 Configuração por Ambiente

**Arquivo:** `apps/api/middleware/cors_security.py`

| Ambiente | Origins | Métodos | Headers |
|----------|---------|---------|---------|
| **Produção** | Domínios específicos | GET, POST | Restrito + x-hub-signature-256 |
| **Staging** | Domínios staging | GET, POST, PUT | Expandido |
| **Desenvolvimento** | `localhost:*` | Todos | Todos |

```python
CORS_CONFIG = {
    "production": {
        "allowed_origins": ["https://maestro.empresa.com"],
        "allowed_methods": ["GET", "POST"],
        "allowed_headers": ["Content-Type", "Authorization", "x-hub-signature-256"],
        "allow_credentials": False,
        "max_age": 3600
    }
}
```

### 17.7 Rate Limiting

#### 17.7.1 Implementação

**Arquivo:** `apps/api/middleware/rate_limiting.py`

```python
class RateLimitMiddleware:
    """
    Rate limiting por tenant/IP usando Redis

    Limites padrão:
    - 100 requests/minuto por tenant
    - 1000 requests/hora por tenant
    - 10 requests/segundo por IP (anti-DDoS)
    """

    def __init__(self, redis_client):
        self.redis = redis_client

    async def check_rate_limit(self, tenant_id: str, ip: str) -> bool:
        key = f"ratelimit:{tenant_id}:{ip}"
        current = await self.redis.incr(key)

        if current == 1:
            await self.redis.expire(key, 60)  # 1 minuto

        return current <= 100
```

### 17.8 Proteção contra Ataques Comuns

#### 17.8.1 SQL Injection

**Proteção:** Queries parametrizadas com psycopg2

```python
# CORRETO - Parametrizado
cursor.execute("SELECT * FROM epicos WHERE azure_id = %s", (work_item_id,))

# ERRADO - Vulnerável
cursor.execute(f"SELECT * FROM epicos WHERE azure_id = {work_item_id}")
```

#### 17.8.2 XSS (Cross-Site Scripting)

**Proteção:** Escape de caracteres especiais em XML

```python
def _escape_xml(self, texto: str) -> str:
    """Escapa caracteres especiais para XML"""
    texto = texto.replace("&", "&amp;")
    texto = texto.replace("<", "&lt;")
    texto = texto.replace(">", "&gt;")
    texto = texto.replace('"', "&quot;")
    texto = texto.replace("'", "&apos;")
    return texto
```

#### 17.8.3 Anti-Loop Protection

**Proteção:** Ignora eventos de usuários de sistema

```python
# Usuários de sistema que NÃO devem triggerar eventos
SYSTEM_USERS = [
    "Sistema Maestro",
    "Bot Maestro",
    "Automation",
    "Azure DevOps"
]

def should_process_event(changed_by: str) -> bool:
    return changed_by not in SYSTEM_USERS
```

### 17.9 Logs de Auditoria

#### 17.9.1 Informações Registradas

Todas as operações sensíveis são logadas:

```python
logger.info(
    "Webhook recebido",
    extra={
        "client_ip": get_client_ip(request),
        "user_agent": request.headers.get("user-agent"),
        "work_item_id": work_item_id,
        "action": "create_feature",
        "tenant_id": tenant_id,
        "signature_valid": True
    }
)
```

#### 17.9.2 Sanitização de Logs

```python
# Nunca logar secrets
def safe_log(data: dict) -> dict:
    sensitive_keys = ["pat", "token", "password", "secret", "api_key"]
    return {k: "***" if any(s in k.lower() for s in sensitive_keys) else v
            for k, v in data.items()}
```

### 17.10 Checklist de Segurança para Deploy

#### Produção

- [ ] PAT Token em Azure Key Vault (não em .env)
- [ ] WEBHOOK_SECRET único e seguro (32+ caracteres)
- [ ] HTTPS habilitado em todos os endpoints
- [ ] CORS restrito a domínios específicos
- [ ] Rate limiting configurado
- [ ] Logs de auditoria ativos
- [ ] Security Headers habilitados
- [ ] Banco de dados com SSL

#### Variáveis de Ambiente de Segurança

```bash
# Key Vault (Produção)
AZURE_KEY_VAULT_URL=https://maestro-vault.vault.azure.net/
AZURE_CLIENT_ID=xxxxx
AZURE_CLIENT_SECRET=xxxxx
AZURE_TENANT_ID=xxxxx

# Fallback (.env local apenas)
AZURE_PAT=xxxxx
WEBHOOK_SECRET=your-strong-webhook-secret-32chars
OPENAI_API_KEY=sk-xxxxx
DATABASE_URL=postgresql://user:pass@host:5432/maestro?sslmode=require

# Security
ENFORCE_HTTPS=true
CORS_ALLOWED_ORIGINS=https://maestro.empresa.com
RATE_LIMIT_ENABLED=true
```

### 17.11 Troubleshooting de Segurança

#### Webhook retorna 401 (Unauthorized)

```bash
# 1. Verificar se secret está configurado
echo $WEBHOOK_SECRET

# 2. Testar localmente com curl
curl -X POST http://localhost:8000/webhook/azure \
  -H "Content-Type: application/json" \
  -H "X-Hub-Signature-256: sha256=$(echo -n '{}' | openssl dgst -sha256 -hmac 'seu-secret' | awk '{print $2}')" \
  -d '{}'
```

#### Key Vault não conecta

```bash
# 1. Verificar credenciais Azure
az login
az keyvault secret list --vault-name maestro-vault

# 2. Verificar permissões
az keyvault show --name maestro-vault --query "properties.accessPolicies"
```

#### Rate limit atingido

```bash
# Verificar contadores no Redis
redis-cli KEYS "ratelimit:*"
redis-cli GET "ratelimit:tenant1:192.168.1.1"
```

### 16.10 Desenvolvimento

**Adicionar Nova Ferramenta:**

1. Criar método em `tools/*.py`:
```python
async def nova_ferramenta(self, param: str) -> Dict:
    """Descrição da ferramenta"""
    # Implementação
    return result
```

2. Registrar em `server.py → get_available_tools()`:
```python
{
    "name": "nova_ferramenta",
    "description": "Descrição",
    "parameters": {...},
    "category": "azure|knowledge|database"
}
```

3. Adicionar execução em `server.py → _execute_tool()`:
```python
elif tool_name == "nova_ferramenta":
    return await self.azure_tools.nova_ferramenta(
        parameters.get("param")
    )
```

4. Documentar e testar

### 16.11 Troubleshooting

**Problema:** MCP Server não inicia

**Solução:**
```bash
# Verificar logs
docker-compose logs maestro-mcp

# Reconstruir
docker-compose down maestro-mcp
docker-compose build --no-cache maestro-mcp
docker-compose up -d maestro-mcp
```

**Problema:** Erro "AZURE_PAT não configurado"

**Solução:**
```bash
# Verificar .env.local
cat .env.local | grep AZURE_PAT
```

**Problema:** Busca semântica retorna vazio

**Solução:**
```sql
-- Verificar pgvector
SELECT * FROM pg_extension WHERE extname = 'vector';

-- Verificar embeddings
SELECT COUNT(*) FROM embeddings WHERE tipo = 'wbs_contexto';
```

### 16.12 Roadmap

- [x] v1.0.0 - 10 ferramentas básicas
- [ ] v1.1.0 - Autenticação + Testes + Cache
- [ ] v1.2.0 - WebSocket + Métricas Prometheus
- [ ] v1.3.0 - Jira Tools + Batch Operations
- [ ] v2.0.0 - Multi-Agent Framework + GraphQL

---

## Apêndices

### A. Checklist de Deploy

- [ ] Variáveis de ambiente configuradas
- [ ] Banco de dados migrado
- [ ] Redis acessível
- [ ] Webhook configurado no Azure DevOps
- [ ] Tags criadas no banco
- [ ] Prompts configurados
- [ ] Health check passando
- [ ] Logs funcionando

### B. Contatos

- **Suporte Técnico:** devops@empresa.com
- **Documentação:** Este manual
- **Issues:** GitHub Issues

### C. Changelog Técnico

| Versão | Data | Mudanças |
|--------|------|----------|
| 4.2.0 | Fev/2026 | **Code Review via Comentários** - Código agora é extraído dos comentários/discussão (não mais da descrição). **Multi-tenant completo** - PAT tokens armazenados na tabela `integracoes` do banco. **Dockerfiles otimizados** - ENVIRONMENT=production. |
| 4.1.0 | Jan/2026 | **MCP Server v1.0.0** - 10 ferramentas para LLMs, integração Claude/GPT-4 |
| 4.0.0 | Jan/2026 | Code Review com contexto hierárquico |
| 3.5.0 | Jan/2026 | Multi-tenant Jira/Azure |
| 3.1.0 | Dez/2025 | WBS completa funcional |
| 3.0.0 | Nov/2025 | Arquitetura Event-Driven |

---

*Última atualização: Fevereiro 2026*

*Maestro WBS - Manual Técnico v4.2.0*
