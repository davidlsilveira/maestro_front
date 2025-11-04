import streamlit as st
import pandas as pd
from repositories.epicos_repository import listar_epicos

def show_epicos():
    st.subheader("📋 Lista de Épicos")

    try:
        epicos = listar_epicos()

        if not epicos:
            st.info("Nenhum épico cadastrado.")
            return

        # Selecionar e renomear colunas para exibição
        df = pd.DataFrame(epicos)

        # Renomear colunas para português
        df_display = df[[
            'id_epico', 'titulo', 'status', 'tag', 'origem',
            'external_id', 'criado_em', 'atualizado_em'
        ]].copy()

        df_display.columns = [
            'ID', 'Título', 'Status', 'Tag', 'Origem',
            'ID Externo', 'Criado em', 'Atualizado em'
        ]

        st.dataframe(df_display, use_container_width=True)

    except Exception as e:
        st.error(f"Erro ao carregar épicos: {str(e)}")
        st.info("Verifique se o banco de dados está acessível.")
