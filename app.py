import streamlit as st
import pandas as pd
from components.table_epicos import show_epicos
from components.form_epico import show_form_epico
from components.detail_epico import show_detail_epico
from components.tags_list import show_tags_list
from components.tags_form import show_tags_form
from components.tag_acoes_manager import show_tag_acoes_manager
from components.prompts_list import show_prompts_list
from components.prompts_form import show_prompts_form
from observability import (
    init_metrics,
    observe_render,
    track_page_view,
    track_streamlit_event,
)
from repositories.epicos_repository import contar_epicos
from repositories.analises_repository import contar_analises, listar_analises
from repositories.prompts_repository import contar_prompts, listar_prompts
from repositories.tags_repository import contar_tags

# ============================
# CONFIGURAÇÃO INICIAL
# ============================
st.set_page_config(page_title="Maestro", layout="wide")
init_metrics()

# Carrega CSS customizado
with open("assets/style.css", "r", encoding="utf-8") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


# ============================
# FUNÇÃO PARA CARREGAR SVG LOCAL
# ============================
def load_svg_content(path):
    """Lê um arquivo SVG e retorna o conteúdo como string."""
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


# Carrega o conteúdo SVG das 3 engrenagens (baseado em Maestro.png)
gear_red_svg = load_svg_content("assets/gear_red.svg")
gear_green_svg = load_svg_content("assets/gear_green.svg")
gear_yellow_svg = load_svg_content("assets/gear_yellow.svg")

# ============================
# CABEÇALHO (LOGO + ENGRENAGENS)
# ============================
st.markdown(
    f"""
    <div class="header">
        <div class="gears-container">
            <div class="gear gear-red">{gear_red_svg}</div>
            <div class="gears-right">
                <div class="gear gear-green">{gear_green_svg}</div>
                <div class="gear gear-yellow">{gear_yellow_svg}</div>
            </div>
        </div>
        <span class="title">Maestro</span>
    </div>
    """,
    unsafe_allow_html=True
)


# ============================
# MENU LATERAL
# ============================
menu = st.sidebar.radio(
    "Navegação",
    ["🏠 Início", "📂 Épicos", "🧠 Análises", "💬 Prompts", "🏷️ Tags", "🔗 Integrações", "⚙️ Administração"]
)


# ============================
# VERIFICAÇÃO DE CONEXÃO COM BANCO
# ============================
from database.connection import test_connection


def render_painel_inicio():
    track_page_view("inicio")
    with observe_render("pagina_inicio"):
        st.markdown("### 🧭 Painel Maestro")

        try:
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Épicos cadastrados", contar_epicos())
            col2.metric("Análises executadas", contar_analises())
            col3.metric("Prompts ativos", contar_prompts())
            col4.metric("Tags ativas", contar_tags())

            st.markdown("---")
            st.markdown(
                "Central de orquestração de épicos, prompts e análises GPT. "
                "Use o menu à esquerda para navegar entre módulos."
            )

            st.markdown("---")
            st.markdown("### 📊 Status do Sistema")

            col1, col2 = st.columns(2)

            with col1:
                st.markdown("**🔗 Conexão com Banco de Dados**")
                if test_connection():
                    st.success("✅ Conectado ao PostgreSQL")
                else:
                    st.error("❌ Sem conexão com o banco")

            with col2:
                import os

                st.markdown("**⚙️ Configurações**")
                st.info(f"Cliente ID: {os.getenv('DEFAULT_CLIENT_ID', '1')}")

        except Exception as e:
            st.error(f"Erro ao carregar dashboard: {str(e)}")


def render_epicos():
    track_page_view("epicos")
    with observe_render("pagina_epicos"):
        abas = st.tabs(["Lista", "Criar", "Detalhe"])
        with abas[0]:
            with observe_render("epicos_lista"):
                show_epicos()
        with abas[1]:
            with observe_render("epicos_criar"):
                show_form_epico()
        with abas[2]:
            with observe_render("epicos_detalhe"):
                show_detail_epico()


def render_analises():
    track_page_view("analises")
    with observe_render("pagina_analises"):
        st.subheader("🧠 Histórico de análises GPT")

        try:
            analises = listar_analises(limite=50)

            if not analises:
                st.info("Nenhuma an�lise executada ainda.")
            else:
                st.markdown(f"Exibindo **{len(analises)}** an�lises mais recentes")

                df = pd.DataFrame(analises)
                df_display = df[
                    [
                        "id_execucao",
                        "epico",
                        "prompt_contexto",
                        "data",
                        "tokens_consumidos",
                        "custo_estimado",
                        "status",
                    ]
                ].copy()

                df_display.columns = ["ID", "Épico", "Contexto", "Data", "Tokens", "Custo (R$)", "Status"]

                st.dataframe(df_display, use_container_width=True)

        except Exception as e:
            st.error(f"Erro ao carregar análises: {str(e)}")


def render_prompts():
    track_page_view("prompts")
    with observe_render("pagina_prompts"):
        st.markdown("### 💬 Gerenciamento de Prompts")

        if st.session_state.get("prompt_edicao"):
            with observe_render("prompt_form_edicao"):
                show_prompts_form()
            st.markdown("---")
            if st.button("🔙 Voltar para Lista"):
                track_streamlit_event("prompts_voltar_lista")
                if "prompt_edicao" in st.session_state:
                    del st.session_state["prompt_edicao"]
                st.rerun()
        else:
            abas = st.tabs(["📋 Lista de Prompts", "✍️ Criar/Editar Prompt"])

            with abas[0]:
                with observe_render("prompts_lista"):
                    show_prompts_list()

            with abas[1]:
                with observe_render("prompts_form"):
                    show_prompts_form()


def render_tags():
    track_page_view("tags")
    with observe_render("pagina_tags"):
        st.markdown("### 🏷️ Gerenciamento de Tags e Ações")

        abas = st.tabs(["🏷️ Lista de Tags", "✏️ Criar/Editar Tag", "🔗 Associações Tag-Ação"])

        with abas[0]:
            with observe_render("tags_lista"):
                show_tags_list()

        with abas[1]:
            with observe_render("tags_form"):
                show_tags_form()

        with abas[2]:
            with observe_render("tags_associacoes"):
                show_tag_acoes_manager()


def render_integracoes():
    track_page_view("integracoes")
    with observe_render("pagina_integracoes"):
        st.subheader("🔗 Integrações futuras (Azure, Jira, GPT, etc.)")


def render_administracao():
    track_page_view("administracao")
    with observe_render("pagina_administracao"):
        st.subheader("⚙️ Administração e usuários (mock)")
        st.write("Gestão de tenants e permissões será implementada em versão posterior.")

# Testar conexão com banco de dados
try:
    db_status = test_connection()
    if not db_status:
        st.sidebar.warning("⚠️ Banco de dados não está acessível")
except Exception as e:
    st.sidebar.error(f"❌ Erro de conexão: {str(e)}")


# ============================
# PÁGINAS
# ============================
if menu == "🏠 Início":
    render_painel_inicio()

elif menu == "📂 Épicos":
    render_epicos()

elif menu == "🧠 Análises":
    render_analises()

elif menu == "💬 Prompts":
    render_prompts()

elif menu == "🏷️ Tags":
    render_tags()

elif menu == "🔗 Integrações":
    render_integracoes()

elif menu == "⚙️ Administração":
    render_administracao()
