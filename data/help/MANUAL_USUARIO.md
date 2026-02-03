# Manual do Usuário - Maestro WBS

## Pergunta: O que o MCP faz no sistema?

**Resposta Simples:**

O **MCP Server** é como um "atendente inteligente" que permite que robôs de Inteligência Artificial (como Claude ou ChatGPT) conversem com o Maestro e executem tarefas automaticamente.

**O que o MCP faz na prática:**

1. **Lê seus Epics automaticamente** - A IA pode ver o que você escreveu no Azure DevOps ou Jira
2. **Cria Features e Stories sozinha** - A IA monta todo o backlog sem você precisar fazer manualmente
3. **Busca projetos parecidos** - A IA procura na base de conhecimento por projetos similares ao seu para usar como referência
4. **Gera WBS completa** - A IA cria toda a estrutura de trabalho (Features → Stories → Tasks) de forma inteligente

**Você precisa fazer algo diferente?**

Não! Continue usando as tags normalmente (como `Maestro Executar`). O MCP Server trabalha nos bastidores. Você nem percebe que ele está lá, mas se beneficia de gerações mais inteligentes e rápidas.

**Exemplo prático:**

- **Sem MCP:** Você adiciona a tag `Maestro Executar` → Maestro cria Features básicas
- **Com MCP:** Você adiciona a tag `Maestro Executar` → Maestro usa IA para buscar projetos similares, analisa o melhor jeito de quebrar o Epic, e cria Features muito mais completas e inteligentes

---

## Índice

1. [Introdução](#introdução)
2. [O que é o Maestro?](#o-que-é-o-maestro)
3. [Benefícios](#benefícios)
4. [Funcionalidades](#funcionalidades)
5. [Como Usar](#como-usar)
6. [Tags Disponíveis](#tags-disponíveis)
7. [Fluxos de Trabalho](#fluxos-de-trabalho)
8. [Exemplos Práticos](#exemplos-práticos)
9. [Perguntas Frequentes](#perguntas-frequentes)
10. [Glossário](#glossário)

---

## Introdução

Bem-vindo ao **Maestro WBS**! Este manual foi criado para ajudá-lo a utilizar todas as funcionalidades do sistema de forma simples e eficiente.

O Maestro é uma ferramenta de automação inteligente que trabalha diretamente com o Azure DevOps, eliminando tarefas repetitivas e acelerando o planejamento de projetos.

---

## O que é o Maestro?

O **Maestro WBS** (Work Breakdown Structure) é um sistema automatizado que:

- **Analisa** requisitos de projetos usando Inteligência Artificial
- **Gera** estruturas de trabalho completas (Features, User Stories, Tasks)
- **Aprende** com projetos anteriores para melhorar sugestões futuras
- **Integra** nativamente com Azure DevOps e Jira
- **Revisa** código automaticamente com análise de segurança

### Como Funciona?

1. Você adiciona uma **tag especial** a um item no Azure DevOps
2. O Maestro **detecta** essa tag automaticamente
3. A **ação correspondente** é executada pela IA
4. Os **resultados** são postados de volta no Azure DevOps

É simples assim: adicione uma tag e deixe o Maestro trabalhar por você.

---

## Benefícios

### Para Gerentes de Projeto

| Benefício | Descrição |
|-----------|-----------|
| **Economia de Tempo** | Reduz horas de planejamento para minutos |
| **Consistência** | Estruturas padronizadas em todos os projetos |
| **Visibilidade** | Estimativas de esforço automáticas |
| **Rastreabilidade** | Histórico completo de decisões |

### Para Desenvolvedores

| Benefício | Descrição |
|-----------|-----------|
| **Clareza** | User Stories bem definidas com critérios de aceite |
| **Code Review** | Análise automática de segurança e qualidade |
| **Testes** | Geração automática de casos de teste |
| **Automação** | Scripts de teste gerados para Selenium/Playwright |

### Para a Organização

| Benefício | Descrição |
|-----------|-----------|
| **Padronização** | Templates customizados por tipo de projeto |
| **Base de Conhecimento** | Aprende com projetos anteriores |
| **Multi-tenant** | Suporte a múltiplos clientes/equipes |
| **Auditoria** | Logs detalhados de todas as operações |

---

## Funcionalidades

### 1. Geração de WBS (Work Breakdown Structure)

Transforma um Epic com requisitos em uma estrutura completa de trabalho.

**O que é gerado:**
- Features (funcionalidades principais)
- User Stories (histórias de usuário)
- Tasks (tarefas técnicas)
- Estimativas de Story Points
- Estimativas de horas

**Exemplo de entrada:**
> "Sistema de autenticação com login social, MFA e recuperação de senha"

**Saída gerada:**
```
Epic: Sistema de Autenticação
├── Feature: Login Social
│   ├── Story: Integração com Google
│   │   ├── Task: Configurar OAuth Google
│   │   ├── Task: Implementar callback
│   │   └── Task: Testes de integração
│   └── Story: Integração com Microsoft
│       └── ...
├── Feature: Multi-Factor Authentication
│   └── ...
└── Feature: Recuperação de Senha
    └── ...
```

### 2. Pré-Análise de Requisitos

Analisa requisitos antes de gerar a estrutura, permitindo revisão humana.

**O que é analisado:**
- Clareza dos requisitos
- Riscos identificados
- Dependências técnicas
- Sugestões de melhoria
- Perguntas para esclarecimento

### 3. Code Review Automatizado

Analisa código fonte com foco em segurança, performance, qualidade e stress testing.

#### 📝 Como Colocar o Código para Revisão

**IMPORTANTE:** Cole o código nos **Comentários/Discussão** da Task, Story ou Bug.

> ⚠️ **Atenção:** O código deve estar nos **comentários**, NÃO na descrição do item. O Maestro analisa apenas o conteúdo dos comentários/discussão.

**Formato Recomendado - Markdown com code blocks:**

```
\`\`\`python
def login(username, password):
    query = f"SELECT * FROM users WHERE username='{username}'"
    return db.execute(query)
\`\`\`
```

**Formato Alternativo - Código direto:**

Você pode colar o código diretamente sem markdown. O Maestro detecta automaticamente.

**Formatos de Código Suportados:**
- ✅ Markdown: \`\`\`python ... \`\`\`
- ✅ HTML: `<code>...</code>` ou `<pre>...</pre>`
- ✅ Jira: `{code:python}...{code}`
- ✅ Texto puro (detecção automática)

**Plataformas Suportadas:**
- ✅ Azure DevOps (Work Items: Task, Story, Bug)
- ✅ Jira Cloud (Issues: Task, Story, Bug)

#### 🎯 Como Solicitar Code Review

**No Azure DevOps:**
1. Abra a Task/Story/Bug
2. Vá até a seção **Discussão** (Discussion)
3. Cole o código em um **novo comentário**
4. Adicione a tag `Maestro Code Review` no campo **Tags**
5. Salve o item

**No Jira:**
1. Abra a Issue (Task/Story/Bug)
2. Vá até a seção **Comentários** (Comments)
3. Cole o código em um **novo comentário**
4. Adicione o label `Maestro Code Review` no campo **Labels**
5. Salve a issue

**Tempo de processamento:** 15-30 segundos

**Onde ver o resultado:** O resultado aparece como um **novo comentário** no mesmo item/issue

#### 🔍 O que é Analisado

**Segurança (OWASP Top 10):**
- SQL Injection, XSS, Command Injection
- Autenticação quebrada, Exposição de dados sensíveis
- Hardcoded Secrets, Path Traversal

**Performance:**
- Queries N+1, Memory leaks
- Algoritmos ineficientes, Cache opportunities
- Complexidade algorítmica (Big O)

**Qualidade:**
- Clean Code, Princípios SOLID
- Code smells, Complexidade ciclomática
- Legibilidade, Testabilidade

**Stress/Carga:**
- Race conditions, Deadlocks
- Gargalos potenciais, Escalabilidade
- Resource exhaustion, Concorrência

#### 📊 Resultado do Code Review

O resultado aparece nos **Comentários** com:
- **Score Geral** (0-10)
- **Scores por Categoria:** Segurança, Performance, Qualidade, Manutenção
- **Vulnerabilidades** por severidade (Crítica, Alta, Média, Baixa)
- **Issues Detalhados** com linha e código problemático
- **Código Sugerido** com correções
- **Tag de Status** automática:
  - `Code Review Aprovado` (score ≥ 8)
  - `Code Review Aprovado com Ressalvas` (score 6-7.9)
  - `Code Review Requer Correções` (score < 6)

### 4. Geração de Casos de Teste

Cria casos de teste baseados nos critérios de aceite das User Stories.

**Formatos suportados:**
- Gherkin (BDD)
- Xray Test Cases
- TestRail format

### 5. Automação de Testes

Gera scripts de automação prontos para executar.

**Frameworks suportados:**
- Selenium (Python)
- Playwright (Python)
- Cypress (JavaScript)

### 6. Refinamento de Requisitos

Melhora a qualidade de requisitos existentes, adicionando:
- Critérios de aceite detalhados
- Cenários de teste
- Requisitos não-funcionais
- Dependências

### 7. ♿ Acessibilidade Automática (WCAG 2.1 AA)

**NOVIDADE:** O Maestro agora inclui requisitos de acessibilidade automaticamente em TODOS os projetos!

#### Por que isso é importante?

- **Inclusão Digital:** Garante que pessoas com deficiência possam usar seu sistema
- **Conformidade Legal:** Cumpre LBI (Lei Brasileira de Inclusão - Lei 13.146/2015)
- **Mais Usuários:** Amplia seu público-alvo em até 15% (pessoas com deficiência)
- **Melhor Experiência:** Beneficia TODOS os usuários, não apenas pessoas com deficiência

#### O que o Maestro faz automaticamente?

Quando você usa qualquer tag do Maestro (Executar, Revisar, etc.), o sistema automaticamente:

1. **Na Pré-Análise:**
   - Identifica requisitos de acessibilidade necessários
   - Sugere recursos de acessibilidade específicos para o projeto
   - Estima tempo adicional para implementação (10-15% do projeto)

2. **Nas User Stories:**
   - Adiciona critérios de aceite de acessibilidade (navegação por teclado, leitores de tela, contraste)
   - Cria tasks específicas para implementar acessibilidade
   - Inclui definição de pronto (DoD) com checklist WCAG 2.1 AA

3. **Nos Test Cases:**
   - Gera testes de navegação por teclado (Tab, Shift+Tab, Enter, Esc)
   - Gera testes com leitores de tela (NVDA, JAWS, VoiceOver)
   - Gera testes de contraste de cores (mínimo 4.5:1 para textos)
   - Gera testes de zoom até 200%
   - Gera testes de formulários (labels, mensagens de erro)

4. **Nos Scripts de Automação:**
   - Inclui testes automatizados com axe-core (padrão da indústria)
   - Verifica conformidade WCAG 2.1 AA automaticamente
   - Detecta problemas de acessibilidade antes do deploy

#### O que é WCAG 2.1 AA?

**WCAG** = Web Content Accessibility Guidelines (Diretrizes de Acessibilidade para Conteúdo Web)
**Nível AA** = Padrão internacional de acessibilidade (exigido pela maioria das leis)

**Principais requisitos:**
- ✅ **Navegação por teclado:** Tudo funciona sem mouse
- ✅ **Leitores de tela:** Compatível com NVDA, JAWS, VoiceOver
- ✅ **Contraste:** Cores com contraste adequado (4.5:1 textos, 3:1 componentes)
- ✅ **Zoom:** Funciona até 200% sem quebrar layout
- ✅ **Formulários:** Campos têm labels claros
- ✅ **Alternativas:** Imagens têm texto alternativo, vídeos têm legendas

#### Exemplo Prático

**Antes (sem acessibilidade):**
```
Story: Login com Email e Senha
Critérios de Aceite:
- ✅ Usuário digita email e senha
- ✅ Sistema valida credenciais
- ✅ Redireciona para dashboard
```

**Agora (com acessibilidade automática):**
```
Story: Login com Email e Senha
Critérios de Aceite Funcionais:
- ✅ Usuário digita email e senha
- ✅ Sistema valida credenciais
- ✅ Redireciona para dashboard

♿ Critérios de Aceite de Acessibilidade:
- ✅ Navegação via Tab funciona (Tab → Email → Senha → Botão)
- ✅ Enter no botão submete formulário
- ✅ Leitores de tela anunciam labels ("Email, obrigatório")
- ✅ Mensagens de erro anunciadas por screen reader
- ✅ Contraste do botão ≥ 4.5:1
- ✅ Foco visível em todos os campos

Tasks Adicionais:
- [ ] Adicionar aria-label em campos
- [ ] Validar contraste com ferramenta
- [ ] Testar com leitor de tela NVDA
```

#### Ferramentas Usadas

O Maestro recomenda e gera scripts para:
- **axe-core:** Padrão da indústria para testes automatizados
- **Lighthouse:** Ferramenta do Google Chrome
- **NVDA:** Leitor de tela gratuito para Windows
- **VoiceOver:** Leitor de tela nativo do Mac
- **Contrast Checker:** Ferramenta para validar cores

#### Você precisa fazer algo diferente?

**Não!** Continue usando o Maestro normalmente. A acessibilidade é adicionada automaticamente em todos os fluxos:
- `Maestro Revisar` → Já inclui análise de acessibilidade
- `Maestro Executar` → Já cria Stories com critérios de acessibilidade
- `Maestro Test Case` → Já gera testes de acessibilidade
- `Maestro Automacao` → Já inclui testes automatizados com axe-core

#### Perguntas Frequentes

**P: A acessibilidade aumenta o tempo do projeto?**
R: Sim, cerca de 10-15%, mas vale a pena. Você evita refatorações caras depois e amplia seu mercado.

**P: Posso desabilitar a acessibilidade?**
R: Tecnicamente sim, mas não recomendamos. É uma obrigação legal (LBI) e uma boa prática de mercado.

**P: O Maestro testa acessibilidade automaticamente?**
R: Sim! Os scripts gerados incluem testes automatizados com axe-core que verificam WCAG 2.1 AA.

**P: O que acontece se meu projeto já existir?**
R: Ao usar `Maestro Revisar` em um Epic existente, o sistema vai sugerir melhorias de acessibilidade que você pode implementar gradualmente.

**P: Acessibilidade é apenas para pessoas cegas?**
R: Não! Beneficia pessoas com deficiências visuais, motoras, auditivas, cognitivas e até idosos. Além disso, melhora a experiência para TODOS.

---

## Como Usar

### Pré-requisitos

1. Acesso ao Azure DevOps do projeto
2. Permissão para editar Work Items
3. Tags do Maestro configuradas no projeto

### Passo a Passo Básico

#### 1. Acesse o Work Item

Navegue até o Epic, Feature, Story ou Task que deseja processar.

#### 2. Adicione a Tag

No campo **Tags**, adicione a tag correspondente à ação desejada:

![Adicionando Tag](./images/add-tag.png)

#### 3. Salve o Work Item

Clique em **Save** para disparar o webhook.

#### 4. Aguarde o Processamento

O Maestro processará automaticamente. Você verá:
- Uma nova tag indicando o status (ex: "Maestro Processando")
- Comentários com o resultado na Discussion

#### 5. Revise o Resultado

Os resultados aparecem como:
- Comentários no Work Item original
- Novos Work Items criados (Features, Stories, Tasks)
- Tags de status atualizadas

---

## Tags Disponíveis

### Tags de Ação

| Tag | Descrição | Aplica-se a |
|-----|-----------|-------------|
| **Maestro Executar** | Executa WBS completa automaticamente | Epic |
| **Maestro Revisar** | Gera pré-análise para revisão | Epic |
| **Maestro Refinar** | Refina requisitos existentes | Epic, Feature |
| **Maestro Code Review** | Analisa código na Description | Task, Story, Bug |
| **Maestro Test Case** | Gera casos de teste | Story |
| **Maestro Automacao Selenium** | Gera script Selenium | Test Case |
| **Maestro Automacao Playwright** | Gera script Playwright | Test Case |
| **Maestro Automacao Cypress** | Gera script Cypress | Test Case |

### Tags de Status

Estas tags são adicionadas automaticamente pelo Maestro:

| Tag | Significado |
|-----|-------------|
| **Maestro Processando** | Work Item está sendo processado |
| **Maestro Concluido** | Processamento finalizado com sucesso |
| **Maestro Erro** | Ocorreu erro no processamento |
| **Code Review Aprovado** | Código aprovado (score >= 8) |
| **Code Review Aprovado com Ressalvas** | Código aprovado com alertas (score 6-7.9) |
| **Code Review Reprovado** | Código reprovado (score < 6) |

---

## Fluxos de Trabalho

### Fluxo 1: WBS Completa (Recomendado para novos projetos)

```
1. Criar Epic com descrição detalhada dos requisitos
2. Adicionar tag "Maestro Executar"
3. Aguardar processamento (2-5 minutos)
4. Revisar Features e Stories criadas
5. Ajustar estimativas se necessário
6. Iniciar Sprint Planning
```

### Fluxo 2: WBS com Revisão (Projetos complexos)

```
1. Criar Epic com requisitos
2. Adicionar tag "Maestro Revisar"
3. Ler pré-análise na Discussion
4. Ajustar requisitos conforme sugestões
5. Trocar tag para "Maestro Executar"
6. Aguardar geração da WBS
7. Revisar e aprovar
```

### Fluxo 3: Code Review (Durante desenvolvimento)

```
1. Desenvolvedor finaliza código
2. Abre a Task/Story/Bug no Azure DevOps ou Jira
3. Adiciona um comentário na Discussion com o código
4. Adiciona tag "Maestro Code Review"
5. Aguarda análise (15-30 segundos)
6. Revisa feedback no novo comentário gerado
7. Corrige issues encontrados
8. Re-submete se necessário (novo comentário + tag novamente)
```

### Fluxo 4: Geração de Testes (Após Stories aprovadas)

```
1. Story com critérios de aceite definidos
2. Adicionar tag "Maestro Test Case"
3. Test Cases criados automaticamente
4. Adicionar tag de automação desejada
5. Scripts gerados na Discussion do Test Case
```

---

## Exemplos Práticos

### Exemplo 1: Criando WBS para um Sistema de E-commerce

**Epic Description:**
```
Desenvolver módulo de carrinho de compras para o e-commerce.

Requisitos:
- Adicionar/remover produtos do carrinho
- Calcular frete por CEP
- Aplicar cupons de desconto
- Salvar carrinho para usuários logados
- Checkout com múltiplas formas de pagamento (cartão, PIX, boleto)

Requisitos não-funcionais:
- Performance: página deve carregar em menos de 2 segundos
- Disponibilidade: 99.9% uptime
```

**Ação:** Adicionar tag `Maestro Executar`

**Resultado:** Features, Stories e Tasks criadas automaticamente com estimativas.

---

### Exemplo 2: Code Review de uma API

**Passo 1 - Adicione um comentário na Task com o código:**
```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

class User(BaseModel):
    name: str
    email: str
    password: str

@app.post("/users")
async def create_user(user: User):
    query = f"INSERT INTO users VALUES ('{user.name}', '{user.email}', '{user.password}')"
    db.execute(query)
    return {"status": "created"}
```

**Passo 2 - Adicione a tag:** `Maestro Code Review`

**Resultado na Discussion:**
```
## ❌ Code Review - REQUER CORREÇÕES
**Score Geral: 4.5/10**

🔒 Seg: 2/10 | ⚡ Perf: 6/10 | ✨ Qual: 5/10 | 🔧 Mnt: 5/10

**🛡️ Vulnerabilidades:** 🔴 1 crítica | 🟠 1 alta

**🔒 Issues de Segurança:**
- [CRITICAL] SQL Injection - Query construída com string format (A03:2021)
- [HIGH] Senha armazenada em texto plano (A02:2021)

**💡 Sugestões:**
- Usar queries parametrizadas ou ORM
- Implementar hash de senha (bcrypt/argon2)
- Adicionar validação de email
```

---

### Exemplo 3: Gerando Testes Automatizados

**Test Case na Discussion:**
```
Test Case: Verificar login com credenciais válidas
Steps:
1. Acessar página de login
2. Preencher email válido
3. Preencher senha válida
4. Clicar em "Entrar"
Expected: Usuário redirecionado para dashboard
```

**Ação:** Adicionar tag `Maestro Automacao Playwright`

**Script gerado:**
```python
import pytest
from playwright.sync_api import Page, expect

def test_login_credenciais_validas(page: Page):
    # Step 1: Acessar página de login
    page.goto("https://app.exemplo.com/login")

    # Step 2: Preencher email válido
    page.fill("[data-testid='email']", "usuario@teste.com")

    # Step 3: Preencher senha válida
    page.fill("[data-testid='password']", "senha123")

    # Step 4: Clicar em "Entrar"
    page.click("[data-testid='submit']")

    # Expected: Usuário redirecionado para dashboard
    expect(page).to_have_url("https://app.exemplo.com/dashboard")
```

---

## Perguntas Frequentes

### Geral

**P: O Maestro substitui o trabalho humano?**

R: Não. O Maestro é uma ferramenta de **aceleração**. Ele gera uma primeira versão que deve ser **revisada e ajustada** pela equipe. A expertise humana continua essencial.

---

**P: Quanto tempo leva o processamento?**

R: Depende da complexidade:
- Pré-análise: 30-60 segundos
- WBS completa: 2-5 minutos
- Code Review: 15-30 segundos
- Geração de testes: 20-40 segundos

---

**P: Posso usar em qualquer projeto?**

R: Sim, desde que:
- O projeto use Azure DevOps ou Jira
- As tags do Maestro estejam configuradas
- O webhook esteja ativo

---

### WBS

**P: A WBS gerada está errada. O que fazer?**

R:
1. Revise se a descrição do Epic está clara e completa
2. Use "Maestro Revisar" primeiro para ver a pré-análise
3. Ajuste a descrição com base nas sugestões
4. Re-execute com "Maestro Executar"
5. Faça ajustes manuais conforme necessário

---

**P: Posso customizar os templates de WBS?**

R: Sim! A equipe técnica pode configurar templates específicos para:
- Tipos de projeto (software, infraestrutura, dados)
- Metodologias (Scrum, Kanban, SAFe)
- Padrões da organização

---

**P: O Maestro considera projetos anteriores?**

R: Sim! O Maestro possui uma **Base de Conhecimento** que:
- Aprende com WBS de projetos passados
- Sugere estruturas similares a projetos bem-sucedidos
- Melhora as estimativas com dados históricos

---

### Code Review

**P: Como colocar código para review?**

R: Cole o código nos **Comentários/Discussão** da Task/Story/Bug (NÃO na Description). Pode usar:
- Markdown com code blocks (recomendado): \`\`\`python ... \`\`\`
- HTML: `<code>...</code>` ou `<pre>...</pre>`
- Jira: `{code:python}...{code}`
- Código direto (o Maestro detecta automaticamente)

**P: Por que o código deve estar nos comentários e não na descrição?**

R: O Maestro usa os comentários para separar claramente o código a ser revisado do contexto do item. Isso permite que você coloque múltiplos trechos de código para revisão sem alterar a descrição original da tarefa.

---

**P: O Code Review detecta todas as vulnerabilidades?**

R: O Code Review analisa:
- OWASP Top 10 (principais vulnerabilidades web)
- Padrões comuns de código inseguro
- Más práticas conhecidas

Para análise de segurança completa, use também ferramentas especializadas (SAST/DAST).

---

**P: Qual score é considerado bom?**

R:
- **8-10**: Aprovado - Código de qualidade
- **6-7.9**: Aprovado com ressalvas - Melhorias recomendadas
- **< 6**: Reprovado - Correções necessárias

---

### Testes

**P: Os scripts de teste funcionam diretamente?**

R: Os scripts são gerados como **ponto de partida**. Você precisará:
- Ajustar seletores (data-testid, IDs, classes)
- Configurar URLs do ambiente
- Adicionar dados de teste específicos

---

**P: Posso gerar testes para qualquer linguagem?**

R: Atualmente suportamos:
- **Selenium**: Python
- **Playwright**: Python
- **Cypress**: JavaScript

Outros frameworks podem ser adicionados sob demanda.

---

## MCP Server - Integração com Agentes de IA

### O que é o MCP Server?

O **MCP Server** (Model Context Protocol Server) é um componente do Maestro que funciona como uma **ponte** entre o sistema e agentes de Inteligência Artificial como Claude, ChatGPT e outros LLMs (Large Language Models).

**Em palavras simples:** É um servidor que permite que IAs conversem com o Maestro e executem tarefas automaticamente, como criar Features, buscar projetos similares, e gerar WBS completas.

**Pense assim:** Se o Maestro fosse uma empresa, o MCP Server seria o atendente que entende o que a IA precisa e busca as informações certas ou executa as ações solicitadas.

### Para Que Serve?

Com o MCP Server, você pode criar **agentes autônomos** que:

- 📊 **Analisam Epics** e sugerem melhorias automaticamente
- 🤖 **Geram WBS completas** baseadas em projetos similares
- 🔍 **Buscam conhecimento** de projetos anteriores
- ✅ **Criam Features e Stories** no Azure DevOps sem intervenção manual
- 💡 **Fornecem consultoria** baseada em histórico de sucesso

### Exemplo de Uso

**Cenário:** Você tem um Epic complexo e quer que a IA crie toda a WBS automaticamente.

**Com MCP Server:**
1. Agente lê o Epic do Azure DevOps
2. Busca projetos similares na base de conhecimento
3. Gera proposta de Features baseada em exemplos
4. Cria todas as Features no Azure DevOps
5. Adiciona comentário no Epic resumindo o trabalho

**Tudo isso sem você mover um dedo!**

### Benefícios para Usuários de Negócio

- ⚡ **Velocidade**: WBS completa gerada em segundos
- 🎯 **Qualidade**: Baseado em projetos bem-sucedidos
- 🔄 **Consistência**: Mesmo padrão em todos os projetos
- 📚 **Aprendizado**: Sistema fica mais inteligente com o tempo

### Como Funciona?

O MCP Server funciona **nos bastidores**. Você não precisa fazer nada de especial:

1. Continue usando as tags normalmente (`Maestro Executar`, etc.)
2. O sistema pode usar agentes de IA para melhorar as gerações
3. Resultados aparecem no Azure DevOps como sempre

### Disponibilidade

O MCP Server está disponível para:
- ✅ Azure DevOps
- ✅ Jira Cloud
- ✅ Integração com Claude, GPT-4, e outros LLMs

**Nota:** O MCP Server é uma funcionalidade avançada geralmente configurada pela equipe técnica. Como usuário, você se beneficia automaticamente das melhorias que ele traz!

### Perguntas Frequentes sobre MCP Server

**P: O que o MCP faz no sistema?**
R: O MCP Server permite que agentes de IA (como Claude ou GPT-4) interajam com o Maestro automaticamente. Ele funciona como uma API que a IA pode usar para:
- Ler Epics e Work Items do Azure DevOps/Jira
- Criar Features, Stories e Tasks automaticamente
- Buscar projetos similares na base de conhecimento
- Gerar WBS completas sem intervenção humana

**P: Eu preciso fazer algo diferente para usar o MCP Server?**
R: Não! O MCP Server trabalha nos bastidores. Continue usando as tags normalmente (como `Maestro Executar`). A equipe técnica pode configurar agentes de IA que usam o MCP Server para melhorar a qualidade das gerações.

**P: Qual a diferença entre o Maestro normal e o Maestro com MCP?**
R: O Maestro normal executa os workflows configurados. Com o MCP Server, agentes de IA podem tomar decisões mais inteligentes, buscar conhecimento de projetos anteriores, e até criar WBS completas de forma autônoma, aprendendo continuamente.

**P: O MCP Server está ativo no meu ambiente?**
R: Pergunte à equipe técnica. Se o MCP Server estiver rodando, você verá a porta 8100 ativa no ambiente. Mas como usuário de negócio, você não precisa se preocupar com isso - o sistema funciona normalmente com ou sem MCP.

---

## Glossário

| Termo | Definição |
|-------|-----------|
| **WBS** | Work Breakdown Structure - Estrutura de decomposição do trabalho |
| **Epic** | Grande iniciativa que contém múltiplas Features |
| **Feature** | Funcionalidade de negócio que entrega valor |
| **User Story** | Descrição de funcionalidade do ponto de vista do usuário |
| **Task** | Tarefa técnica necessária para completar uma Story |
| **Story Points** | Unidade de estimativa de complexidade |
| **Sprint** | Iteração de desenvolvimento (geralmente 2 semanas) |
| **OWASP** | Open Web Application Security Project |
| **Critério de Aceite** | Condição que deve ser atendida para Story ser considerada pronta |
| **Webhook** | Notificação automática enviada quando algo muda |
| **Tag** | Etiqueta/rótulo adicionado a Work Items |
| **Multi-tenant** | Sistema que suporta múltiplos clientes isolados |
| **MCP** | Model Context Protocol - Protocolo para integração com LLMs |
| **LLM** | Large Language Model - Modelo de linguagem de grande escala (IA) |
| **Agente de IA** | Programa autônomo que executa tarefas usando IA |

---

## Suporte

### Canais de Atendimento

- **Email**: suporte@maestro.com.br
- **Teams**: Canal #maestro-suporte
- **Documentação**: Este manual e Manual Técnico

### Reportando Problemas

Ao reportar um problema, inclua:
1. ID do Work Item afetado
2. Tag utilizada
3. Descrição do comportamento esperado vs. obtido
4. Screenshot se aplicável

---

## Changelog

### Versão 4.2.0 (Fevereiro 2026)
- **Code Review via Comentários** - Código agora é analisado dos comentários/discussão (não mais da descrição)
- **Multi-tenant Completo** - Suporte a múltiplos clientes com tokens PAT independentes
- **Extração de Código Melhorada** - Detecta código em Markdown, HTML, Jira e texto puro
- **Dockerfiles Otimizados** - Ambiente de produção configurado corretamente

### Versão 4.1.0 (Janeiro 2026)
- **MCP Server** - Integração com agentes de IA (Claude, GPT-4)
- 10 ferramentas para automação via LLMs
- Agentes autônomos de geração de WBS

### Versão 4.0.0 (Janeiro 2026)
- Code Review com contexto hierárquico
- Suporte a Jira Enterprise
- Formato compacto de comentários

### Versão 3.5.0 (Janeiro 2026)
- Multi-tenant Jira/Azure
- Framework de automação de testes

### Versão 3.1.0 (Dezembro 2025)
- WBS 100% funcional
- Base de conhecimento ativa

---

*Última atualização: Fevereiro 2026*

*Maestro WBS - Automatizando o planejamento, acelerando a entrega.*
