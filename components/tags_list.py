"""
Componente de listagem de Tags.
"""

import streamlit as st
import pandas as pd
from repositories.tags_repository import listar_tags, excluir_tag


def show_tags_list():
    st.subheader("📋 Lista de Tags")

    try:
        # Filtro de tags ativas/inativas
        col1, col2 = st.columns([3, 1])
        with col2:
            mostrar_inativas = st.checkbox("Mostrar inativas", value=False)

        tags = listar_tags(apenas_ativas=not mostrar_inativas)

        if not tags:
            st.info("Nenhuma tag cadastrada.")
            return

        # Criar DataFrame para exibição
        df = pd.DataFrame(tags)

        # Formatação da cor
        def format_cor(cor_hex):
            if cor_hex:
                return f'<span style="background-color:{cor_hex};padding:2px 10px;border-radius:3px;color:white;">{cor_hex}</span>'
            return "-"

        # Exibir estatísticas
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total de Tags", len(tags))
        col2.metric("Tags Ativas", len([t for t in tags if t['ativo']]))
        col3.metric("Usos Totais", sum(t['usos'] for t in tags))
        col4.metric("Ações Associadas", sum(t['acoes_associadas'] for t in tags))

        st.markdown("---")

        # Exibir tabela de tags
        for tag in tags:
            with st.expander(f"🏷️ {tag['nome']} ({tag['usos']} usos)"):
                col1, col2 = st.columns([3, 1])

                with col1:
                    st.markdown(f"**Nome:** {tag['nome']}")

                    if tag['descricao']:
                        st.markdown(f"**Descrição:** {tag['descricao']}")

                    if tag['cor_hex']:
                        st.markdown(f"**Cor:** {format_cor(tag['cor_hex'])}", unsafe_allow_html=True)

                    st.markdown(f"**Status:** {'✅ Ativa' if tag['ativo'] else '❌ Inativa'}")
                    st.markdown(f"**Usos em Épicos:** {tag['usos']}")
                    st.markdown(f"**Ações Associadas:** {tag['acoes_associadas']}")

                    # Datas
                    st.caption(f"Criada em: {tag['criado_em']}")
                    if tag['atualizado_em']:
                        st.caption(f"Atualizada em: {tag['atualizado_em']}")

                with col2:
                    # Ações da tag
                    if st.button("✏️ Editar", key=f"edit_{tag['id_tag']}", use_container_width=True):
                        st.session_state['edit_tag_id'] = tag['id_tag']
                        st.rerun()
                        return

                    if tag['usos'] == 0:
                        if st.button("🗑️ Excluir", key=f"delete_{tag['id_tag']}", type="secondary", use_container_width=True):
                            if excluir_tag(tag['id_tag']):
                                st.success(f"Tag '{tag['nome']}' excluída com sucesso!")
                                st.rerun()
                                return
                            else:
                                st.error("Erro ao excluir tag")
                    else:
                        st.caption(f"⚠️ Não pode excluir\n({tag['usos']} usos)")

    except Exception as e:
        st.error(f"Erro ao carregar tags: {str(e)}")
        st.info("Verifique se o banco de dados está acessível.")
