"""
Componente de formulário para criar/editar Prompts.
"""

import streamlit as st
import json
from repositories.prompts_repository import (
    criar_prompt, atualizar_prompt, listar_contextos_disponiveis
)


def show_prompts_form():
    """Formulário para criar ou editar prompts"""

    # Verificar se há prompt em edição
    prompt_edicao = st.session_state.get('prompt_edicao', None)

    if prompt_edicao:
        st.info(f"✏️ Editando: **{prompt_edicao['nome']}** (v{prompt_edicao['versao']})")

        if st.button("❌ Cancelar Edição"):
            del st.session_state['prompt_edicao']
            st.rerun()

    # Carregar contextos (com tratamento de erro separado)
    try:
        contextos_existentes = listar_contextos_disponiveis()
    except Exception as e:
        st.error(f"Erro ao carregar contextos: {str(e)}")
        contextos_existentes = []

    with st.form("form_prompt"):
        st.markdown("### " + ("Editar Prompt" if prompt_edicao else "Criar Novo Prompt"))

        # Nome
        nome = st.text_input(
            "Nome do Prompt *",
            value=prompt_edicao['nome'] if prompt_edicao else "",
            placeholder="Ex: Pré-análise com Perguntas v3.0",
            help="Nome descritivo do prompt"
        )

        # Contexto
        col1, col2 = st.columns([2, 1])
        with col1:
            # Sugerir contextos existentes
            contexto_sugerido = st.selectbox(
                "Contexto Sugerido (opcional)",
                ["-- Digitar novo --"] + contextos_existentes,
                index=0
            )

        with col2:
            # Versão
            versao = st.text_input(
                "Versão *",
                value=prompt_edicao['versao'] if prompt_edicao else "1.0.0",
                placeholder="1.0.0",
                help="Formato: X.Y.Z"
            )

        # Campo de contexto (digitado ou selecionado)
        if contexto_sugerido == "-- Digitar novo --":
            contexto = st.text_input(
                "Contexto *",
                value=prompt_edicao['tag'] if prompt_edicao else "",
                placeholder="Ex: pre_analise, wbs_geracao, feature_criacao",
                help="Identificador do contexto de uso do prompt"
            )
        else:
            contexto = contexto_sugerido
            st.info(f"📁 Contexto selecionado: **{contexto}**")

        # Template do Prompt
        template_prompt = st.text_area(
            "Template do Prompt *",
            value=prompt_edicao['template_prompt'] if prompt_edicao else "",
            placeholder="Digite o template do prompt aqui...\n\nVocê pode usar variáveis como {nome_variavel}",
            height=300,
            help="Template do prompt com variáveis entre chaves {variavel}"
        )

        # Parâmetros de IA
        col1, col2 = st.columns(2)

        with col1:
            temperatura = st.slider(
                "Temperatura *",
                min_value=0.0,
                max_value=1.0,
                value=float(prompt_edicao['temperatura']) if prompt_edicao else 0.7,
                step=0.1,
                help="Controla a criatividade (0.0 = mais determinístico, 1.0 = mais criativo)"
            )

        with col2:
            max_tokens = st.number_input(
                "Max Tokens *",
                min_value=100,
                max_value=16000,
                value=prompt_edicao['max_tokens'] if prompt_edicao else 4000,
                step=100,
                help="Número máximo de tokens na resposta"
            )

        # Variáveis Esperadas (JSON)
        st.markdown("#### Variáveis Esperadas (JSON - opcional)")
        st.caption("📝 Este é um campo opcional para documentar quais variáveis o prompt usa")
        variaveis_default = ""
        if prompt_edicao and prompt_edicao.get('variaveis_esperadas'):
            variaveis_default = json.dumps(prompt_edicao['variaveis_esperadas'], indent=2, ensure_ascii=False)

        variaveis_esperadas = st.text_area(
            "Variáveis Esperadas",
            value=variaveis_default,
            placeholder='{\n  "titulo": "Título do épico",\n  "descricao": "Descrição detalhada"\n}',
            height=150,
            help="JSON com descrição das variáveis usadas no template",
            label_visibility="collapsed"
        )

        # Metadata (JSON)
        st.markdown("#### Metadata (JSON - opcional)")
        st.caption("📋 Campo opcional para metadados adicionais")
        metadata_default = ""
        if prompt_edicao and prompt_edicao.get('metadata'):
            metadata_default = json.dumps(prompt_edicao['metadata'], indent=2, ensure_ascii=False)

        metadata = st.text_area(
            "Metadata",
            value=metadata_default,
            placeholder='{\n  "categoria": "analise",\n  "prioridade": "alta"\n}',
            height=100,
            help="Metadados adicionais em JSON",
            label_visibility="collapsed"
        )

        # Botão de envio
        submitted = st.form_submit_button(
            "💾 " + ("Atualizar Prompt" if prompt_edicao else "Criar Prompt"),
            type="primary",
            use_container_width=True
        )

    if submitted:
        # Validações
        if not nome or not contexto or not template_prompt:
            st.error("❌ Preencha todos os campos obrigatórios (*)!")
            return

        # Validar JSON (se fornecidos)
        variaveis_json = None
        metadata_json = None

        try:
            if variaveis_esperadas:
                variaveis_json = json.loads(variaveis_esperadas)
        except json.JSONDecodeError:
            st.error("❌ Variáveis Esperadas: JSON inválido!")
            return

        try:
            if metadata:
                metadata_json = json.loads(metadata)
        except json.JSONDecodeError:
            st.error("❌ Metadata: JSON inválido!")
            return

        # Criar ou atualizar (sem try/except para não capturar rerun)
        if prompt_edicao:
            # Atualizar
            try:
                sucesso = atualizar_prompt(
                    id_prompt=prompt_edicao['id_prompt'],
                    nome=nome,
                    contexto=contexto,
                    versao=versao,
                    template_prompt=template_prompt,
                    temperatura=temperatura,
                    max_tokens=max_tokens,
                    variaveis_esperadas=variaveis_json,
                    metadata=metadata_json
                )

                if sucesso:
                    st.success(f"✅ Prompt **{nome}** atualizado com sucesso!")
                    del st.session_state['prompt_edicao']
                    st.rerun()
                else:
                    st.error("❌ Erro ao atualizar prompt!")
            except Exception as e:
                st.error(f"❌ Erro ao atualizar prompt: {str(e)}")

        else:
            # Criar
            try:
                id_prompt = criar_prompt(
                    nome=nome,
                    contexto=contexto,
                    versao=versao,
                    template_prompt=template_prompt,
                    temperatura=temperatura,
                    max_tokens=max_tokens,
                    variaveis_esperadas=variaveis_json,
                    metadata=metadata_json
                )

                st.success(f"✅ Prompt **{nome}** criado com sucesso! (ID: {id_prompt})")
                st.info("O prompt está ativo e pode ser usado em associações tag-ação.")
                st.rerun()
            except Exception as e:
                st.error(f"❌ Erro ao criar prompt: {str(e)}")
