# Maestro RAG - Índice de Documentação

**Última Atualização:** 2026-02-03
**Versão Maestro:** 4.2.0

---

## 📚 Estrutura da Documentação

```
RAG/
├── INDEX.md (este arquivo)
├── MANUAL_TECNICO.md
├── MANUAL_USUARIO.md
├── FAQ_MCP.md
│
├── technical_docs/
│   ├── STATE_MACHINE_IMPLEMENTATION.md ⭐ NOVO
│   ├── MCP_SERVER_COMPLETE_IMPLEMENTATION.md
│   └── MCP_IMPLEMENTATION_PATTERNS.md
│
└── business_docs/
    ├── STATE_MACHINE_BUSINESS_VALUE.md ⭐ NOVO
    └── MCP_SERVER_BUSINESS_VALUE.md
```

---

## 🎯 Guia Rápido por Perfil

### Para Desenvolvedores

**Implementando features:**
1. [MANUAL_TECNICO.md](./MANUAL_TECNICO.md) - Visão geral da arquitetura
2. [STATE_MACHINE_IMPLEMENTATION.md](./technical_docs/STATE_MACHINE_IMPLEMENTATION.md) - Sistema de estados
3. [MCP_SERVER_COMPLETE_IMPLEMENTATION.md](./technical_docs/MCP_SERVER_COMPLETE_IMPLEMENTATION.md) - MCP Server
4. [MCP_IMPLEMENTATION_PATTERNS.md](./technical_docs/MCP_IMPLEMENTATION_PATTERNS.md) - Patterns e best practices

**Troubleshooting:**
- Estado inconsistente → [STATE_MACHINE_IMPLEMENTATION.md § Troubleshooting](./technical_docs/STATE_MACHINE_IMPLEMENTATION.md#troubleshooting)
- MCP não responde → [FAQ_MCP.md](./FAQ_MCP.md)

### Para Product Owners / Gestores

**Entendendo o valor:**
1. [STATE_MACHINE_BUSINESS_VALUE.md](./business_docs/STATE_MACHINE_BUSINESS_VALUE.md) - ROI e ganhos do State Machine
2. [MCP_SERVER_BUSINESS_VALUE.md](./business_docs/MCP_SERVER_BUSINESS_VALUE.md) - Valor do MCP Server

**Métricas e KPIs:**
- State Machine: [STATE_MACHINE_BUSINESS_VALUE.md § Métricas](./business_docs/STATE_MACHINE_BUSINESS_VALUE.md#-métricas-de-sucesso)
- MCP Server: [MCP_SERVER_BUSINESS_VALUE.md § KPIs](./business_docs/MCP_SERVER_BUSINESS_VALUE.md)

### Para Usuários Finais

**Começando:**
1. [MANUAL_USUARIO.md](./MANUAL_USUARIO.md) - Guia completo de uso
2. [FAQ_MCP.md](./FAQ_MCP.md) - Perguntas frequentes

**Casos de uso comuns:**
- Processar épico → [MANUAL_USUARIO.md § Maestro Executar](./MANUAL_USUARIO.md)
- Refazer WBS → [STATE_MACHINE_BUSINESS_VALUE.md § Caso de Uso 1](./business_docs/STATE_MACHINE_BUSINESS_VALUE.md#caso-de-uso-1-ajuste-de-escopo-mid-sprint)

---

## 📖 Documentação por Tópico

### State Machine (v3.6.0) ⭐ NOVA FEATURE

**O que é:** Sistema de controle de ciclo de vida de épicos com validação e confirmações.

**Documentação Técnica:**
- **Implementação Completa:** [STATE_MACHINE_IMPLEMENTATION.md](./technical_docs/STATE_MACHINE_IMPLEMENTATION.md)
  - Arquitetura e componentes
  - Modelo de dados (tabelas SQL)
  - Estados e transições
  - API e integração
  - Queries úteis

**Documentação de Negócio:**
- **Valor e ROI:** [STATE_MACHINE_BUSINESS_VALUE.md](./business_docs/STATE_MACHINE_BUSINESS_VALUE.md)
  - Problemas resolvidos
  - Economia anual estimada (R$ 63k)
  - ROI: 320% no primeiro ano
  - Casos de uso práticos
  - Métricas e KPIs

**Quick Links:**
- 🔧 [Como integrar no código](./technical_docs/STATE_MACHINE_IMPLEMENTATION.md#api-e-integração)
- 💰 [Cálculo de ROI](./business_docs/STATE_MACHINE_BUSINESS_VALUE.md#-roi-e-economia)
- 🐛 [Troubleshooting](./technical_docs/STATE_MACHINE_IMPLEMENTATION.md#troubleshooting)
- 📊 [Queries úteis](./technical_docs/STATE_MACHINE_IMPLEMENTATION.md#queries-úteis)

---

### MCP Server

**O que é:** Model Context Protocol Server para integração com AI agents e IDEs.

**Documentação Técnica:**
- **Implementação Completa:** [MCP_SERVER_COMPLETE_IMPLEMENTATION.md](./technical_docs/MCP_SERVER_COMPLETE_IMPLEMENTATION.md)
- **Patterns de Implementação:** [MCP_IMPLEMENTATION_PATTERNS.md](./technical_docs/MCP_IMPLEMENTATION_PATTERNS.md)

**Documentação de Negócio:**
- **Valor de Negócio:** [MCP_SERVER_BUSINESS_VALUE.md](./business_docs/MCP_SERVER_BUSINESS_VALUE.md)

**FAQ:**
- [FAQ_MCP.md](./FAQ_MCP.md)

---

### Sistema Core Maestro

**Arquitetura Geral:**
- [MANUAL_TECNICO.md](./MANUAL_TECNICO.md)

**Guia do Usuário:**
- [MANUAL_USUARIO.md](./MANUAL_USUARIO.md)

---

### Segurança ⭐ NOVO

**Documentação Completa de Segurança:**
- [MANUAL_TECNICO.md § Seção 17](./MANUAL_TECNICO.md#17-segurança---documentação-completa)

**Tópicos Cobertos:**
- Autenticação PAT Token (Azure DevOps)
- Validação HMAC-SHA256 para webhooks
- Azure Key Vault integration
- Security Headers (OWASP)
- CORS por ambiente
- Rate Limiting
- Proteção SQL Injection/XSS
- Logs de Auditoria
- Checklist de Deploy

**Quick Links:**
- 🔐 [Visão Geral](./MANUAL_TECNICO.md#171-visão-geral-de-segurança)
- 🔑 [Autenticação Azure](./MANUAL_TECNICO.md#172-autenticação-com-azure-devops)
- ✅ [Validação Webhooks](./MANUAL_TECNICO.md#173-validação-de-webhooks---hmac-sha256)
- 🔒 [Key Vault](./MANUAL_TECNICO.md#174-azure-key-vault-integration)
- 🛡️ [Security Headers](./MANUAL_TECNICO.md#175-security-headers-owasp)
- 📋 [Checklist Deploy](./MANUAL_TECNICO.md#1710-checklist-de-segurança-para-deploy)

---

## 🔍 Busca Rápida

### Por Tecnologia

- **PostgreSQL / Banco de Dados:**
  - Modelo de dados: [STATE_MACHINE_IMPLEMENTATION.md § Modelo de Dados](./technical_docs/STATE_MACHINE_IMPLEMENTATION.md#modelo-de-dados)
  - Queries: [STATE_MACHINE_IMPLEMENTATION.md § Queries Úteis](./technical_docs/STATE_MACHINE_IMPLEMENTATION.md#queries-úteis)

- **Python / FastAPI:**
  - API do State Manager: [STATE_MACHINE_IMPLEMENTATION.md § API](./technical_docs/STATE_MACHINE_IMPLEMENTATION.md#api-e-integração)
  - MCP Server: [MCP_SERVER_COMPLETE_IMPLEMENTATION.md](./technical_docs/MCP_SERVER_COMPLETE_IMPLEMENTATION.md)

- **Azure DevOps:**
  - Integração: [MANUAL_TECNICO.md](./MANUAL_TECNICO.md)
  - Tags Maestro: [MANUAL_USUARIO.md](./MANUAL_USUARIO.md)

### Por Problema

- **"Como evitar perder trabalho ao refazer WBS?"**
  → [STATE_MACHINE_BUSINESS_VALUE.md § Problema 1](./business_docs/STATE_MACHINE_BUSINESS_VALUE.md#-problema-1-perda-acidental-de-trabalho)

- **"Estado do épico está inconsistente"**
  → [STATE_MACHINE_IMPLEMENTATION.md § Troubleshooting](./technical_docs/STATE_MACHINE_IMPLEMENTATION.md#erro-estado-inconsistente)

- **"Como integrar State Machine no meu código?"**
  → [STATE_MACHINE_IMPLEMENTATION.md § Integração](./technical_docs/STATE_MACHINE_IMPLEMENTATION.md#integração-no-tag_detectorpy)

- **"Qual o ROI do State Machine?"**
  → [STATE_MACHINE_BUSINESS_VALUE.md § ROI](./business_docs/STATE_MACHINE_BUSINESS_VALUE.md#-roi-total)

### Por Caso de Uso

- **Ajustar escopo mid-sprint:**
  → [STATE_MACHINE_BUSINESS_VALUE.md § Caso de Uso 1](./business_docs/STATE_MACHINE_BUSINESS_VALUE.md#caso-de-uso-1-ajuste-de-escopo-mid-sprint)

- **Onboarding de novo desenvolvedor:**
  → [STATE_MACHINE_BUSINESS_VALUE.md § Caso de Uso 2](./business_docs/STATE_MACHINE_BUSINESS_VALUE.md#caso-de-uso-2-novo-dev-na-equipe)

- **Auditoria de compliance:**
  → [STATE_MACHINE_BUSINESS_VALUE.md § Caso de Uso 3](./business_docs/STATE_MACHINE_BUSINESS_VALUE.md#caso-de-uso-3-auditoria-de-compliance)

---

## 📊 Changelog da Documentação

### 2026-02-03 - Code Review v4.2.0 ⭐ NOVO

**Atualizado:**
- ⚠️ **Code Review via Comentários** - Código agora é extraído dos comentários/discussão (não mais da descrição)
- 🔐 **Multi-tenant Completo** - PAT tokens armazenados na tabela `integracoes` do banco de dados
- 🐳 **Dockerfiles Otimizados** - ENVIRONMENT=production configurado
- 📚 `MANUAL_USUARIO.md` e `MANUAL_TECNICO.md` atualizados com novos fluxos

**Importante para Code Review:**
- O código para revisão deve ser postado nos **COMENTÁRIOS** da Task/Story/Bug
- Formatos suportados: Markdown (\`\`\`), HTML (`<code>`), Jira (`{code}`)
- Resultado aparece como novo comentário no mesmo item

---

### 2026-01-30 - Segurança Completa + RAG Otimizado

**Adicionado:**
- ✨ Seção 17 completa de Segurança no `MANUAL_TECNICO.md`
  - Autenticação PAT Token
  - Validação HMAC-SHA256
  - Azure Key Vault
  - Security Headers OWASP
  - CORS, Rate Limiting
  - Checklist de Deploy

**Atualizado:**
- 🔧 RAG chunks: 1.5k-2k com 20% overlap (melhor qualidade)
- 🔧 Frontend conectado ao PostgreSQL Azure
- 📚 INDEX.md com links para seção de Segurança

---

### 2026-01-13 - State Machine v3.6.0 ⭐

**Adicionado:**
- ✨ `technical_docs/STATE_MACHINE_IMPLEMENTATION.md` - Documentação técnica completa
- ✨ `business_docs/STATE_MACHINE_BUSINESS_VALUE.md` - Valor de negócio e ROI
- ✨ Este arquivo de índice (INDEX.md)

**Conteúdo:**
- Arquitetura do State Machine
- Modelo de dados (2 tabelas + 1 view)
- 8 estados possíveis
- 7 transições mapeadas
- Sistema de confirmação
- 15+ queries úteis
- Cálculo de ROI: R$ 63k/ano
- 3 casos de uso detalhados

### 2025-01-12 - MCP Server

**Adicionado:**
- `technical_docs/MCP_SERVER_COMPLETE_IMPLEMENTATION.md`
- `technical_docs/MCP_IMPLEMENTATION_PATTERNS.md`
- `business_docs/MCP_SERVER_BUSINESS_VALUE.md`
- `FAQ_MCP.md`

---

## 🚀 Roadmap da Documentação

### Q1 2026
- ✅ State Machine (Completo)
- ✅ MCP Server (Completo)
- 🔄 Video tutorials (Em progresso)

### Q2 2026
- 📋 Artifact Cleaner
- 📋 Auto-healing patterns
- 📋 Performance optimization guide

### Q3 2026
- 📋 Multi-tenant patterns
- 📋 Custom workflows guide
- 📋 Advanced integrations

---

## 📞 Contribuindo

**Encontrou um erro?**
- Abra issue no GitHub com label `documentation`

**Sugestão de melhoria?**
- Pull request na pasta `RAG/`

**Dúvida não respondida?**
- Adicione em [FAQ_MCP.md](./FAQ_MCP.md)

---

## 📜 Glossário

- **State Machine:** Sistema de controle de estados de épicos
- **MCP:** Model Context Protocol (protocolo de integração com AI)
- **WBS:** Work Breakdown Structure (estrutura de decomposição)
- **Epic:** Épico (work item type no Azure DevOps)
- **Cascata:** Efeito de deletar artefatos dependentes em cadeia
- **Confirmação:** Aprovação explícita antes de operação destrutiva

---

**Maestro RAG Documentation Index**
**v4.2.0**
**© 2026 Sempre IT - Todos os direitos reservados**
