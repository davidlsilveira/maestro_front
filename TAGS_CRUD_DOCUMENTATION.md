# CRUD de Tags e Tag_Acoes - Maestro Front

## ✅ Implementação Completa

O sistema de gerenciamento de Tags e suas associações com Ações foi totalmente implementado e integrado ao Maestro Front.

## 📋 Visão Geral

### O que são Tags?

Tags no sistema Maestro são marcadores que podem ser aplicados a épicos do Azure DevOps para disparar ações automatizadas. Exemplos:
- `Maestro Executar` - Gera WBS completa automaticamente
- `Maestro Revisar` - Executa pré-análise detalhada
- `Maestro Refinar` - Refina épicos existentes

### O que são Tag_Acoes?

Tag_Acoes são **associações** entre Tags e Ações. Definem:
- Qual **Ação** deve ser executada quando uma **Tag** é detectada
- Qual **Prompt** (template) deve ser usado
- **Prioridade** de execução
- **Condições extras** e **Parâmetros** personalizados

## 🗄️ Estrutura do Banco de Dados

### Tabela: `tags`

```sql
CREATE TABLE tags (
    id_tag INTEGER PRIMARY KEY,
    id_cliente INTEGER NOT NULL,
    nome VARCHAR(100) NOT NULL,
    descricao TEXT,
    cor_hex VARCHAR(7),         -- Ex: #B22222
    ativo BOOLEAN DEFAULT true,
    criado_em TIMESTAMP DEFAULT NOW(),
    atualizado_em TIMESTAMP DEFAULT NOW()
);
```

### Tabela: `acoes`

```sql
CREATE TABLE acoes (
    id_acao INTEGER PRIMARY KEY,
    codigo VARCHAR(50) NOT NULL,
    nome VARCHAR(100) NOT NULL,
    descricao TEXT,
    tipo VARCHAR(30),           -- ai_analysis, workflow, integration, notification
    ativo BOOLEAN DEFAULT true,
    criado_em TIMESTAMP DEFAULT NOW()
);
```

### Tabela: `tag_acoes`

```sql
CREATE TABLE tag_acoes (
    id_tag_acao INTEGER PRIMARY KEY,
    id_tag INTEGER NOT NULL REFERENCES tags(id_tag),
    id_acao INTEGER NOT NULL REFERENCES acoes(id_acao),
    id_prompt INTEGER NOT NULL REFERENCES prompts(id_prompt),
    prioridade INTEGER DEFAULT 1,
    condicoes_extras JSONB,
    parametros JSONB,
    ativo BOOLEAN DEFAULT true,
    criado_em TIMESTAMP DEFAULT NOW()
);
```

## 📂 Arquivos Criados

### Repositórios (Business Logic)

1. **`repositories/tags_repository.py`**
   - `listar_tags()` - Lista todas as tags de um cliente
   - `buscar_tag_por_id()` - Busca tag por ID
   - `buscar_tag_por_nome()` - Busca tag por nome
   - `criar_tag()` - Cria nova tag
   - `atualizar_tag()` - Atualiza tag existente
   - `excluir_tag()` - Soft delete (marca como inativa)
   - `excluir_tag_permanente()` - Hard delete
   - `contar_tags()` - Conta total de tags

2. **`repositories/acoes_repository.py`**
   - `listar_acoes()` - Lista todas as ações
   - `buscar_acao_por_id()` - Busca ação por ID
   - `buscar_acao_por_codigo()` - Busca ação por código
   - `listar_acoes_por_tipo()` - Filtra por tipo
   - `listar_tipos_acoes()` - Lista tipos disponíveis
   - `contar_acoes()` - Conta total de ações

3. **`repositories/tag_acoes_repository.py`**
   - `listar_tag_acoes()` - Lista associações (com filtros)
   - `buscar_tag_acao_por_id()` - Busca associação específica
   - `criar_tag_acao()` - Cria nova associação
   - `atualizar_tag_acao()` - Atualiza associação
   - `excluir_tag_acao()` - Soft delete
   - `excluir_tag_acao_permanente()` - Hard delete
   - `listar_acoes_por_tag()` - Lista ações de uma tag
   - `contar_tag_acoes()` - Conta associações
   - `verificar_duplicata()` - Valida duplicatas

### Componentes UI (Streamlit)

1. **`components/tags_list.py`**
   - Listagem de tags com estatísticas
   - Filtro de tags ativas/inativas
   - Visualização de cor em formato HTML
   - Contadores de uso e ações associadas
   - Botões de editar/excluir

2. **`components/tags_form.py`**
   - Formulário de criação de tags
   - Formulário de edição de tags
   - Seletor de cores visual (color picker)
   - Preview da tag com cor
   - Validação de duplicatas

3. **`components/tag_acoes_manager.py`**
   - Listagem de associações tag-ação
   - Agrupamento por tag
   - Formulário de criação de associações
   - Edição de prioridades inline
   - Gestão de condições e parâmetros JSON

### Integração com App Principal

**`app.py`** foi atualizado com:
- Import dos novos componentes e repositórios
- Menu "🏷️ Tags" adicionado
- Métrica de "Tags ativas" no dashboard
- Página completa com 3 tabs:
  - Lista de Tags
  - Criar/Editar Tag
  - Associações Tag-Ação

## 🎯 Funcionalidades Implementadas

### 1. CRUD de Tags

#### Criar Tag
```python
from repositories.tags_repository import criar_tag

id_tag = criar_tag(
    nome="Maestro Executar",
    descricao="Gera WBS completa automaticamente",
    cor_hex="#B22222"
)
```

#### Listar Tags
```python
from repositories.tags_repository import listar_tags

tags = listar_tags(apenas_ativas=True)
# Retorna lista com usos e ações associadas
```

#### Atualizar Tag
```python
from repositories.tags_repository import atualizar_tag

atualizar_tag(
    id_tag=1,
    nome="Maestro Executar v2",
    cor_hex="#FF0000",
    ativo=True
)
```

#### Excluir Tag
```python
from repositories.tags_repository import excluir_tag

# Soft delete (marca como inativa)
excluir_tag(id_tag=1)

# Hard delete (remove permanentemente)
excluir_tag_permanente(id_tag=1)
```

### 2. Gerenciamento de Associações (Tag_Acoes)

#### Criar Associação
```python
from repositories.tag_acoes_repository import criar_tag_acao

id_tag_acao = criar_tag_acao(
    id_tag=1,              # ID da tag
    id_acao=2,             # ID da ação (ex: ai_analysis)
    id_prompt=5,           # ID do prompt a executar
    prioridade=1,          # Menor = mais prioritário
    condicoes_extras={"tipo_projeto": "software"},
    parametros={"temperatura": 0.7}
)
```

#### Listar Associações
```python
from repositories.tag_acoes_repository import listar_tag_acoes

# Todas as associações
associacoes = listar_tag_acoes()

# Filtrar por tag específica
associacoes_tag = listar_tag_acoes(id_tag=1)
```

#### Atualizar Prioridade
```python
from repositories.tag_acoes_repository import atualizar_tag_acao

atualizar_tag_acao(
    id_tag_acao=10,
    prioridade=5
)
```

## 🎨 Interface do Usuário

### Dashboard Principal
```
┌─────────────────────────────────────────────────┐
│ 🧭 Painel Maestro                               │
├─────────────┬───────────┬─────────┬─────────────┤
│ Épicos: 35  │ Análises: │ Prompts:│ Tags: 8     │
│             │ 770       │ 4       │             │
└─────────────┴───────────┴─────────┴─────────────┘
```

### Página de Tags

**Tab 1: Lista de Tags**
- Cards expansíveis por tag
- Cor visual da tag
- Contadores de uso
- Botões de ação (editar/excluir)

**Tab 2: Criar/Editar Tag**
- Campo nome (obrigatório)
- Campo descrição
- Seletor de cor visual
- Preview da tag
- Validação de duplicatas

**Tab 3: Associações Tag-Ação**
- Sub-tab de listagem (agrupada por tag)
- Sub-tab de criação
- Edição inline de prioridades
- Suporte a JSON para condições e parâmetros

## 📊 Estatísticas e Métricas

Cada tag exibe:
- **Nome e descrição**
- **Cor** (preview visual)
- **Status** (ativa/inativa)
- **Usos em épicos** - Quantas vezes foi aplicada
- **Ações associadas** - Quantas ações estão configuradas
- **Datas** - Criação e última atualização

## 🔒 Validações Implementadas

1. **Nome único** - Não permite tags duplicadas
2. **Cor em formato hexadecimal** - Validação de formato
3. **Verificação de uso** - Impede exclusão de tags em uso
4. **Duplicata de associações** - Não permite mesma tag+ação+prompt
5. **Campos obrigatórios** - Nome, tag, ação e prompt

## 🎯 Casos de Uso

### Caso 1: Criar Tag "Maestro Executar"

1. Acessar menu "🏷️ Tags"
2. Ir para aba "➕ Criar/Editar Tag"
3. Preencher:
   - Nome: `Maestro Executar`
   - Descrição: `Gera WBS completa automaticamente`
   - Cor: `#B22222` (vermelho)
4. Clicar em "💾 Salvar Tag"

### Caso 2: Associar Tag com Ação de IA

1. Ir para aba "🔗 Associações Tag-Ação"
2. Sub-aba "➕ Nova Associação"
3. Preencher:
   - Tag: `Maestro Executar`
   - Ação: `Análise com IA - ai_analysis`
   - Prompt: `WBS Generator (v2)`
   - Prioridade: `1`
4. Clicar em "💾 Criar Associação"

### Caso 3: Editar Prioridade de Execução

1. Aba "🔗 Associações Tag-Ação"
2. Expandir tag desejada
3. Alterar número no campo "Prioridade"
4. Clicar em "💾" para salvar

## 🚀 Exemplos de Código

### Exemplo Completo: Criar Tag e Associação

```python
import streamlit as st
from repositories.tags_repository import criar_tag
from repositories.tag_acoes_repository import criar_tag_acao

# 1. Criar a tag
id_tag = criar_tag(
    nome="Maestro Urgente",
    descricao="Análise prioritária com IA",
    cor_hex="#FF0000"
)

st.success(f"Tag criada com ID: {id_tag}")

# 2. Criar associação com ação de IA
id_tag_acao = criar_tag_acao(
    id_tag=id_tag,
    id_acao=1,  # ai_analysis
    id_prompt=3,  # Pre-Analise
    prioridade=1,
    parametros={"urgente": True}
)

st.success(f"Associação criada com ID: {id_tag_acao}")
```

## 🐛 Troubleshooting

### Erro: "Tag não encontrada"
```
Verifique:
1. Se a tag existe no banco
2. Se está ativa (apenas_ativas=False para ver todas)
3. Se pertence ao cliente correto (DEFAULT_CLIENT_ID)
```

### Erro: "Já existe uma tag com este nome"
```
Solução:
1. Use outro nome
2. Ou edite a tag existente
3. Ou reative a tag inativa
```

### Erro: "Não pode excluir tag em uso"
```
A tag está sendo usada em épicos. Para excluir:
1. Remova a tag dos épicos primeiro
2. Ou use soft delete (marca como inativa)
```

## ✅ Checklist de Implementação

- [x] Repositório de Tags
- [x] Repositório de Ações
- [x] Repositório de Tag_Acoes
- [x] Componente de listagem de Tags
- [x] Componente de formulário de Tags
- [x] Componente de gerenciamento de Tag_Acoes
- [x] Integração com app.py
- [x] Métrica no dashboard
- [x] Validações de duplicata
- [x] Soft delete e hard delete
- [x] Suporte a JSON (condições e parâmetros)
- [x] Filtros e agrupamentos
- [x] Documentação completa

## 📝 Próximos Passos Sugeridos

1. **Testes Automatizados**
   - Unit tests para repositórios
   - Integration tests para componentes

2. **Importação/Exportação**
   - Exportar tags para JSON/CSV
   - Importar tags em lote

3. **Histórico de Mudanças**
   - Log de alterações em tags
   - Auditoria de associações

4. **Dashboard de Estatísticas**
   - Gráficos de uso de tags
   - Análise de eficiência de ações

## 🎉 Conclusão

O CRUD completo de Tags e Tag_Acoes está **100% funcional** e integrado ao Maestro Front!

Principais benefícios:
- ✅ Gerenciamento visual de tags
- ✅ Configuração de ações automatizadas
- ✅ Priorização de execução
- ✅ Validações e segurança
- ✅ Interface intuitiva
- ✅ Integrado ao banco de dados do projeto Maestro

Para usar, execute:
```bash
streamlit run app.py
```

E acesse o menu **🏷️ Tags**!
