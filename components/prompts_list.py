"""
Componente de listagem de Prompts.
"""

import streamlit as st
import pandas as pd
from repositories.prompts_repository import (
    listar_prompts, excluir_prompt, excluir_prompt_permanente, atualizar_prompt
)


def show_prompts_list():
    """Lista todos os prompts cadastrados"""

    # Carregar dados (fora do try para não capturar exceções de rerun)
    try:
        prompts = listar_prompts(apenas_ativos=False)
    except Exception as e:
        st.error(f"Erro ao carregar prompts do banco: {str(e)}")
        return

    if not prompts:
        st.info("Nenhum prompt cadastrado ainda.")
        return

    # Estatísticas
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total de Prompts", len(prompts))
    col2.metric("Ativos", sum(1 for p in prompts if p['ativo']))
    col3.metric("Inativos", sum(1 for p in prompts if not p['ativo']))
    col4.metric("Contextos", len(set(p['tag'] for p in prompts)))

    st.markdown("---")

    # Filtros
    col1, col2 = st.columns(2)

    with col1:
        contextos = sorted(set(p['tag'] for p in prompts))
        contextos_options = ["Todos"] + contextos
        filtro_contexto = st.selectbox("Filtrar por Contexto:", contextos_options)

    with col2:
        filtro_status = st.selectbox("Filtrar por Status:", ["Todos", "Ativos", "Inativos"])

    # Aplicar filtros
    prompts_filtrados = prompts

    if filtro_contexto != "Todos":
        prompts_filtrados = [p for p in prompts_filtrados if p['tag'] == filtro_contexto]

    if filtro_status == "Ativos":
        prompts_filtrados = [p for p in prompts_filtrados if p['ativo']]
    elif filtro_status == "Inativos":
        prompts_filtrados = [p for p in prompts_filtrados if not p['ativo']]

    st.markdown(f"**Exibindo {len(prompts_filtrados)} prompts**")
    st.markdown("---")

    # Agrupar por contexto
    prompts_por_contexto = {}
    for prompt in prompts_filtrados:
        contexto = prompt['tag']
        if contexto not in prompts_por_contexto:
            prompts_por_contexto[contexto] = []
        prompts_por_contexto[contexto].append(prompt)

    # Exibir prompts agrupados
    for contexto, prompts_ctx in sorted(prompts_por_contexto.items()):
        st.markdown(f"### 📁 {contexto.upper()} ({len(prompts_ctx)} prompts)")
        st.markdown("---")

        for prompt in sorted(prompts_ctx, key=lambda x: x['nome']):
            col1, col2 = st.columns([4, 1])

            with col1:
                # Nome e versão
                status_icon = "✅" if prompt['ativo'] else "❌"
                st.markdown(f"**{status_icon} {prompt['nome']}** `v{prompt['versao']}`")

                # Métricas
                col_a, col_b, col_c, col_d = st.columns(4)
                col_a.metric("Temperatura", f"{prompt['temperatura']:.1f}")
                col_b.metric("Max Tokens", prompt['max_tokens'])
                col_c.metric("Usos", prompt['em_uso'])
                col_d.metric("Atualizado", prompt['ultima_atualizacao'])

                # Template do prompt (preview em expander)
                with st.expander("📝 Ver Template"):
                    st.code(prompt['template_prompt'], language="text")

                # Variáveis esperadas
                if prompt.get('variaveis_esperadas'):
                    with st.expander("🔧 Variáveis Esperadas"):
                        st.json(prompt['variaveis_esperadas'])

                # Metadata
                if prompt.get('metadata'):
                    with st.expander("📋 Metadata"):
                        st.json(prompt['metadata'])

            with col2:
                st.markdown("**Ações**")

                # Editar
                if st.button("✏️ Editar", key=f"edit_{prompt['id_prompt']}", use_container_width=True):
                    st.session_state['prompt_edicao'] = prompt
                    st.rerun()

                # Ativar/Desativar
                if prompt['ativo']:
                    if st.button("🚫 Desativar", key=f"deactivate_{prompt['id_prompt']}", use_container_width=True):
                        if atualizar_prompt(prompt['id_prompt'], ativo=False):
                            st.success("Prompt desativado!")
                            st.rerun()
                else:
                    if st.button("✅ Ativar", key=f"activate_{prompt['id_prompt']}", use_container_width=True):
                        if atualizar_prompt(prompt['id_prompt'], ativo=True):
                            st.success("Prompt ativado!")
                            st.rerun()

                # Excluir (soft delete)
                if st.button("🗑️ Excluir", key=f"delete_{prompt['id_prompt']}", type="secondary", use_container_width=True):
                    if excluir_prompt(prompt['id_prompt']):
                        st.success("Prompt excluído (inativado)!")
                        st.rerun()

                # Excluir permanentemente
                if st.button("⚠️ Excluir Permanente", key=f"delete_perm_{prompt['id_prompt']}", use_container_width=True):
                    if excluir_prompt_permanente(prompt['id_prompt']):
                        st.success("Prompt excluído permanentemente!")
                        st.rerun()
                    else:
                        st.error("❌ Não é possível excluir: prompt está em uso em associações tag_acoes!")

            st.markdown("---")
