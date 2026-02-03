# FAQ - MCP Server (Model Context Protocol)

## O que é o MCP?

O **MCP** significa **Model Context Protocol Server**. É um servidor REST API que funciona como ponte entre o Maestro e agentes de Inteligência Artificial.

## O que o MCP faz no sistema?

O MCP Server permite que Inteligências Artificiais (como Claude e GPT-4) interajam automaticamente com o Maestro. Especificamente:

### Funcionalidades Principais:

1. **Leitura de Work Items**
   - A IA pode ler Epics, Features, Stories e Tasks do Azure DevOps ou Jira
   - Obtém todos os detalhes: título, descrição, estado, relações, etc.

2. **Criação de Work Items**
   - A IA pode criar Features, Stories e Tasks automaticamente
   - Mantém a hierarquia correta (Epic → Feature → Story → Task)

3. **Busca Semântica na Base de Conhecimento**
   - A IA pode procurar projetos similares usando busca inteligente
   - Encontra WBS de projetos anteriores para usar como referência

4. **Consulta de Templates e Configurações**
   - A IA pode obter templates de WBS por tipo de projeto
   - Acessa configurações específicas de cada cliente

5. **Automação Completa de WBS**
   - Agentes de IA podem gerar backlogs completos de forma autônoma
   - Aprendem com projetos anteriores para melhorar continuamente

## Como o MCP ajuda os usuários?

**Para Usuários de Negócio:**
- ✅ Gerações de WBS mais inteligentes e completas
- ✅ Análise automática de projetos similares
- ✅ Sugestões baseadas em histórico de sucesso
- ✅ Trabalho nos bastidores - você não precisa fazer nada diferente

**Para Desenvolvedores:**
- ✅ API REST padronizada para integração com LLMs
- ✅ 10 ferramentas prontas para uso
- ✅ Suporte a Claude, GPT-4 e outros LLMs
- ✅ Documentação completa e exemplos práticos

## Preciso fazer algo diferente para usar o MCP?

**Não!** O MCP Server trabalha nos bastidores. Continue usando as tags normalmente:
- `Maestro Executar`
- `Maestro Revisar`
- `Maestro WBS`
- etc.

O sistema pode usar agentes de IA (via MCP Server) para melhorar as gerações, mas isso é transparente para você.

## Qual a diferença entre Maestro com e sem MCP?

**Sem MCP Server:**
- Maestro executa workflows pré-configurados
- Usa prompts fixos para geração
- Não busca conhecimento de projetos anteriores automaticamente

**Com MCP Server:**
- Agentes de IA podem tomar decisões inteligentes
- Busca automática por projetos similares
- Geração adaptativa baseada em aprendizado contínuo
- Qualidade superior nas WBS geradas

## O MCP está ativo no meu ambiente?

Verifique com a equipe técnica. Se o MCP Server estiver rodando:
- Porta 8100 estará ativa
- Você verá o serviço `maestro-mcp` no Docker

Mas como usuário de negócio, você não precisa se preocupar - o sistema funciona normalmente com ou sem MCP.

## Onde está a documentação técnica do MCP?

- **Manual Técnico:** Seção 16 - MCP Server
- **Documentação Completa:** maestro/docs/MCP_SERVER.md
- **Quick Start:** maestro/docs/MCP_QUICKSTART.md
- **Exemplos:** maestro/examples/mcp_agent_example.py

## Quais ferramentas o MCP Server oferece?

### Azure DevOps Tools (4):
1. `get_epic_details` - Obtém Epic completo
2. `get_work_item` - Obtém qualquer work item
3. `create_feature` - Cria Feature
4. `add_comment` - Adiciona comentário

### Knowledge Base Tools (3):
5. `search_knowledge_base` - Busca semântica
6. `get_wbs_by_id` - Obtém WBS específica
7. `save_wbs_to_knowledge` - Salva WBS

### Database Tools (3):
8. `get_epic_from_db` - Obtém Epic do banco
9. `get_wbs_template` - Obtém template
10. `get_client_config` - Obtém configuração

## Como funciona a integração com Claude/GPT-4?

1. **Agente de IA recebe tarefa** - Ex: "Gere WBS para Epic 12345"
2. **IA decide quais ferramentas usar** - Ex: get_epic_details, search_knowledge_base
3. **IA chama MCP Server** - HTTP POST /execute com nome da ferramenta
4. **MCP Server executa e retorna dados** - Ex: detalhes do Epic
5. **IA analisa e continua** - Usa dados para próximas decisões
6. **IA cria work items** - Chama create_feature quando necessário

## Casos de uso práticos

### 1. Agente de WBS Automático
```
1. Lê Epic (get_epic_details)
2. Busca similares (search_knowledge_base)
3. Obtém template (get_wbs_template)
4. Gera análise com IA
5. Cria Features (create_feature)
6. Salva conhecimento (save_wbs_to_knowledge)
7. Adiciona comentário (add_comment)
```

### 2. Consultor de Projetos
```
1. Recebe descrição de projeto
2. Busca projetos similares (search_knowledge_base)
3. Analisa boas práticas com IA
4. Recomenda estrutura de WBS
```

### 3. Assistente de Backlog
```
1. Lista Epics pendentes (get_epic_from_db)
2. Analisa cada Epic com IA
3. Sugere melhorias
4. Adiciona comentários (add_comment)
```

## Tecnologias utilizadas

- **Framework:** FastAPI (Python)
- **Porta:** 8100
- **Validação:** Pydantic
- **Embeddings:** OpenAI API
- **Database:** PostgreSQL + pgvector
- **Container:** Docker

## Versão atual

- **Versão:** 1.0.0
- **Data:** Janeiro 2026
- **Status:** Produção

## Roadmap

- [x] v1.0.0 - 10 ferramentas básicas
- [ ] v1.1.0 - Autenticação + Testes
- [ ] v1.2.0 - WebSocket + Métricas
- [ ] v1.3.0 - Jira Tools + Batch Ops
- [ ] v2.0.0 - Multi-Agent Framework

---

**Resumo em uma frase:**

O MCP Server é um servidor que permite que IAs usem o Maestro como uma "ferramenta", automatizando completamente a geração de WBS de forma inteligente.
