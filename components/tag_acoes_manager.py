"""
Componente de gerenciamento de Tag_Acoes (associações entre tags e ações).
"""

import streamlit as st
import pandas as pd
from repositories.tag_acoes_repository import (
    listar_tag_acoes, criar_tag_acao, excluir_tag_acao_permanente,
    atualizar_tag_acao, verificar_duplicata
)
from repositories.tags_repository import listar_tags
from repositories.acoes_repository import listar_acoes
from repositories.prompts_repository import listar_prompts


def show_tag_acoes_manager():
    st.subheader("🔗 Associações Tag → Ação")

    # Tabs para listar e criar
    tab_list, tab_create = st.tabs(["📋 Lista de Associações", "➕ Nova Associação"])

    with tab_list:
        show_tag_acoes_list()

    with tab_create:
        show_tag_acoes_form()


def show_tag_acoes_list():
    """Lista todas as associações tag-ação"""

    try:
        # Filtro por tag
        tags = listar_tags()

        col1, col2 = st.columns([3, 1])
        with col1:
            tags_options = {f"{t['nome']} ({t['id_tag']})": t['id_tag'] for t in tags}
            tags_options = {"Todas as tags": None, **tags_options}

            tag_selecionada = st.selectbox(
                "Filtrar por Tag:",
                options=list(tags_options.keys())
            )

        id_tag_filtro = tags_options[tag_selecionada]

        # Buscar associações
        associacoes = listar_tag_acoes(id_tag=id_tag_filtro)

        if not associacoes:
            st.info("Nenhuma associação cadastrada.")
            return

        # Estatísticas
        col1, col2, col3 = st.columns(3)
        col1.metric("Total de Associações", len(associacoes))
        col2.metric("Tags com Ações", len(set(a['id_tag'] for a in associacoes)))
        col3.metric("Ações Usadas", len(set(a['id_acao'] for a in associacoes)))

        st.markdown("---")

        # Agrupar por tag
        associacoes_por_tag = {}
        for assoc in associacoes:
            tag_nome = assoc['tag_nome']
            if tag_nome not in associacoes_por_tag:
                associacoes_por_tag[tag_nome] = []
            associacoes_por_tag[tag_nome].append(assoc)

        # Exibir associações agrupadas
        for tag_nome, assocs in associacoes_por_tag.items():
            with st.expander(f"🏷️ {tag_nome} ({len(assocs)} ações)"):
                for assoc in sorted(assocs, key=lambda x: x['prioridade']):
                    col1, col2, col3 = st.columns([0.5, 3, 1])

                    with col1:
                        st.markdown(f"**#{assoc['prioridade']}**")

                    with col2:
                        # Cor da tag
                        cor = assoc.get('tag_cor', '#666666')
                        st.markdown(
                            f"<span style='background-color:{cor};padding:2px 8px;border-radius:3px;color:white;font-size:0.8em;'>{tag_nome}</span>",
                            unsafe_allow_html=True
                        )

                        st.markdown(f"**→ {assoc['acao_nome']}** (`{assoc['acao_codigo']}`)")
                        st.caption(f"Tipo: {assoc['acao_tipo']} | Prompt: {assoc['prompt_nome'] or 'N/A'}")

                        # Condições e parâmetros
                        if assoc['condicoes_extras']:
                            st.caption(f"📋 Condições: {assoc['condicoes_extras']}")
                        if assoc['parametros']:
                            st.caption(f"⚙️ Parâmetros: {assoc['parametros']}")

                        st.caption(f"Status: {'✅ Ativa' if assoc['ativo'] else '❌ Inativa'}")

                    with col3:
                        # Editar prioridade
                        nova_prioridade = st.number_input(
                            "Prioridade",
                            min_value=1,
                            max_value=100,
                            value=assoc['prioridade'],
                            key=f"prio_{assoc['id_tag_acao']}",
                            label_visibility="collapsed"
                        )

                        if nova_prioridade != assoc['prioridade']:
                            if st.button("💾", key=f"save_prio_{assoc['id_tag_acao']}"):
                                if atualizar_tag_acao(assoc['id_tag_acao'], prioridade=nova_prioridade):
                                    st.success("Prioridade atualizada!")
                                    st.rerun()
                                    return

                        # Excluir
                        if st.button("🗑️", key=f"del_{assoc['id_tag_acao']}", type="secondary"):
                            if excluir_tag_acao_permanente(assoc['id_tag_acao']):
                                st.success("Associação excluída!")
                                st.rerun()
                                return

                    st.markdown("---")

    except Exception as e:
        st.error(f"Erro ao carregar associações: {str(e)}")


def show_tag_acoes_form():
    """Formulário para criar nova associação"""

    try:
        # Carregar dados para os selects
        tags = listar_tags(apenas_ativas=True)
        acoes = listar_acoes(apenas_ativas=True)
        prompts = listar_prompts(apenas_ativos=True)

        if not tags:
            st.warning("⚠️ Nenhuma tag ativa encontrada. Crie uma tag primeiro.")
            return

        if not acoes:
            st.warning("⚠️ Nenhuma ação ativa encontrada.")
            return

        if not prompts:
            st.warning("⚠️ Nenhum prompt ativo encontrado.")
            return

        with st.form("form_tag_acao"):
            st.markdown("### Criar Nova Associação")

            # Select da Tag
            tags_options = {f"{t['nome']} ({t['id_tag']})": t['id_tag'] for t in tags}
            tag_selecionada = st.selectbox(
                "Tag *",
                options=list(tags_options.keys())
            )
            id_tag = tags_options[tag_selecionada]

            # Select da Ação
            acoes_options = {f"{a['nome']} - {a['tipo']} ({a['codigo']})": a['id_acao'] for a in acoes}
            acao_selecionada = st.selectbox(
                "Ação *",
                options=list(acoes_options.keys())
            )
            id_acao = acoes_options[acao_selecionada]

            # Select do Prompt
            prompts_options = {f"{p['nome']} (v{p['versao']})": p['id_prompt'] for p in prompts}
            prompt_selecionado = st.selectbox(
                "Prompt *",
                options=list(prompts_options.keys())
            )
            id_prompt = prompts_options[prompt_selecionado]

            # Prioridade
            prioridade = st.number_input(
                "Prioridade *",
                min_value=1,
                max_value=100,
                value=1,
                help="Menor valor = maior prioridade"
            )

            # Condições extras (opcional)
            condicoes_extras = st.text_area(
                "Condições Extras (JSON - opcional)",
                placeholder='{"campo": "valor"}',
                help="JSON com condições adicionais para execução"
            )

            # Parâmetros (opcional)
            parametros = st.text_area(
                "Parâmetros (JSON - opcional)",
                placeholder='{"parametro": "valor"}',
                help="JSON com parâmetros para a execução"
            )

            # Botão de envio
            submitted = st.form_submit_button("💾 Criar Associação", type="primary", use_container_width=True)

        if submitted:
            # Validar JSON (se fornecidos)
            import json
            cond_json = None
            param_json = None

            try:
                if condicoes_extras:
                    cond_json = json.loads(condicoes_extras)
            except json.JSONDecodeError:
                st.error("❌ Condições Extras: JSON inválido!")
                return

            try:
                if parametros:
                    param_json = json.loads(parametros)
            except json.JSONDecodeError:
                st.error("❌ Parâmetros: JSON inválido!")
                return

            # Verificar duplicata
            if verificar_duplicata(id_tag, id_acao, id_prompt):
                st.error("❌ Já existe uma associação ativa entre esta tag, ação e prompt!")
                return

            # Criar associação
            try:
                id_tag_acao = criar_tag_acao(
                    id_tag=id_tag,
                    id_acao=id_acao,
                    id_prompt=id_prompt,
                    prioridade=prioridade,
                    condicoes_extras=cond_json,
                    parametros=param_json
                )

                st.success(f"✅ Associação criada com sucesso! (ID: {id_tag_acao})")
                st.info("A associação está ativa e será executada quando a tag for detectada.")
                st.rerun()
                return

            except Exception as e:
                st.error(f"❌ Erro ao criar associação: {str(e)}")

    except Exception as e:
        st.error(f"Erro ao carregar formulário: {str(e)}")
