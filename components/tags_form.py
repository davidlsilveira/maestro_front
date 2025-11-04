"""
Componente de formulário de Tags (criar/editar).
"""

import streamlit as st
from repositories.tags_repository import criar_tag, atualizar_tag, buscar_tag_por_id, buscar_tag_por_nome


def show_tags_form():
    # Verificar se está editando
    edit_tag_id = st.session_state.get('edit_tag_id')

    if edit_tag_id:
        st.subheader("✏️ Editar Tag")
        tag_atual = buscar_tag_por_id(edit_tag_id)

        if not tag_atual:
            st.error("Tag não encontrada!")
            if st.button("Voltar"):
                del st.session_state['edit_tag_id']
                st.rerun()
            return
    else:
        st.subheader("📝 Criar Nova Tag")
        tag_atual = None

    with st.form("form_tag"):
        # Nome da tag
        nome = st.text_input(
            "Nome da Tag *",
            value=tag_atual['nome'] if tag_atual else "",
            placeholder="Ex: Maestro Executar, Maestro Revisar"
        )

        # Descrição
        descricao = st.text_area(
            "Descrição",
            value=tag_atual['descricao'] if tag_atual and tag_atual['descricao'] else "",
            placeholder="Descreva o propósito desta tag..."
        )

        # Cor (com seletor visual)
        col1, col2 = st.columns([1, 3])

        with col1:
            cor_hex = st.color_picker(
                "Cor",
                value=tag_atual['cor_hex'] if tag_atual and tag_atual['cor_hex'] else "#B22222"
            )

        with col2:
            st.markdown(f"**Preview:** <span style='background-color:{cor_hex};padding:5px 20px;border-radius:5px;color:white;font-weight:bold;'>{nome or 'Tag'}</span>", unsafe_allow_html=True)

        # Status (apenas para edição)
        if tag_atual:
            ativo = st.checkbox("Tag Ativa", value=tag_atual['ativo'])
        else:
            ativo = True

        # Botões
        col1, col2, col3 = st.columns([2, 1, 1])

        with col1:
            submitted = st.form_submit_button(
                "💾 Salvar Tag" if not tag_atual else "💾 Atualizar Tag",
                type="primary",
                use_container_width=True
            )

        with col2:
            if tag_atual:
                if st.form_submit_button("❌ Cancelar", use_container_width=True):
                    del st.session_state['edit_tag_id']
                    st.rerun()
                    return

    if submitted:
        # Validações
        if not nome:
            st.error("Nome da tag é obrigatório!")
            return

        # Verificar duplicata (apenas ao criar ou ao mudar o nome)
        if not tag_atual or tag_atual['nome'] != nome:
            tag_existente = buscar_tag_por_nome(nome)
            if tag_existente:
                st.error(f"Já existe uma tag com o nome '{nome}'!")
                return

        try:
            if tag_atual:
                # Atualizar tag existente
                success = atualizar_tag(
                    id_tag=tag_atual['id_tag'],
                    nome=nome,
                    descricao=descricao if descricao else None,
                    cor_hex=cor_hex,
                    ativo=ativo
                )

                if success:
                    st.success(f"✅ Tag '{nome}' atualizada com sucesso!")
                    del st.session_state['edit_tag_id']
                    st.rerun()
                    return
                else:
                    st.error("Erro ao atualizar tag")
            else:
                # Criar nova tag
                id_tag = criar_tag(
                    nome=nome,
                    descricao=descricao if descricao else None,
                    cor_hex=cor_hex
                )

                st.success(f"✅ Tag '{nome}' criada com sucesso! (ID: {id_tag})")
                st.info("A tag está disponível para ser associada a ações.")

                # Limpar form
                st.rerun()
                return

        except Exception as e:
            st.error(f"❌ Erro ao salvar tag: {str(e)}")
            st.info("Verifique se o banco de dados está acessível.")
