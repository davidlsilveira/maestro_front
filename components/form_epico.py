import streamlit as st
from repositories.epicos_repository import criar_epico

def show_form_epico():
    st.subheader("📝 Criar Novo Épico")

    with st.form("form_epico"):
        titulo = st.text_input("Título do Épico *")
        descricao = st.text_area("Descrição *")
        contexto = st.text_area("Contexto adicional")
        tag = st.selectbox("Tag de Análise", ["analise_pre", "wbs", "refino"])
        origem = st.selectbox("Origem", ["manual", "azure", "jira"])
        external_id = st.text_input("ID Externo (opcional)")
        submitted = st.form_submit_button("Salvar Épico")

    if submitted:
        if not titulo or not descricao:
            st.error("Título e Descrição são obrigatórios!")
            return

        try:
            id_epico = criar_epico(
                titulo=titulo,
                descricao=descricao,
                origem=origem,
                tag=tag,
                external_id=external_id if external_id else None,
                contexto=contexto if contexto else None
            )

            st.success(f"✅ Épico **{titulo}** criado com sucesso! (ID: {id_epico})")
            st.info("O épico foi salvo no banco de dados e está disponível para análise.")

        except Exception as e:
            st.error(f"❌ Erro ao criar épico: {str(e)}")
            st.info("Verifique se o banco de dados está acessível.")
