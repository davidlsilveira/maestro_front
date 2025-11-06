import base64
import os
import re
from pathlib import Path
from typing import Optional, Union

import streamlit as st
import pandas as pd
import streamlit.components.v1 as components
from dotenv import load_dotenv
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
from observability.logging import setup_logging, get_logger

# Configurar logging estruturado
setup_logging()
logger = get_logger(__name__)

from repositories.epicos_repository import contar_epicos
from repositories.analises_repository import contar_analises, listar_analises
from repositories.prompts_repository import contar_prompts, listar_prompts
from repositories.tags_repository import contar_tags

DEFAULT_GEAR_SVG = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">
  <path fill="currentColor" d="M50,8 L56,18 L68,16 L70,28 L82,32 L76,43 L84,52 L72,58 L72,70 L60,70 L52,82 L43,74 L32,80 L28,68 L16,66 L18,54 L8,50 L18,44 L16,32 L28,30 L32,18 L43,24 L50,8 Z M50,28 A22,22 0 1,0 50,72 A22,22 0 1,0 50,28 Z"/>
</svg>"""

DEFAULT_GEARS = {
    "gear_red.svg": DEFAULT_GEAR_SVG,
    "gear_green.svg": DEFAULT_GEAR_SVG,
    "gear_yellow.svg": DEFAULT_GEAR_SVG,
}

BASE_DIR = Path(__file__).resolve().parent
ASSETS_DIR = BASE_DIR / "assets"

load_dotenv(BASE_DIR / ".env")


def _get_setting(secret_key: str, env_key: str, default: Optional[str] = None) -> Optional[str]:
    """Try secrets.toml first, then environment variables, then default."""
    try:
        value = st.secrets[secret_key]
    except FileNotFoundError:
        value = os.getenv(env_key, default)
    except KeyError:
        value = os.getenv(env_key, default)
    return value if value not in (None, "") else default

def _resolve_asset_path(path: Optional[Union[str, Path]]) -> Optional[Path]:
    if path is None:
        return None
    candidate = Path(path)
    if not candidate.is_absolute():
        candidate = (ASSETS_DIR / candidate).resolve()
    return candidate


def _sanitize_svg(content: str) -> str:
    content = re.sub(r"<\?xml[^>]*\?>", "", content, flags=re.IGNORECASE)
    content = re.sub(r"<!DOCTYPE[\s\S]*?>", "", content, flags=re.IGNORECASE)
    return content.strip()


def _replace_style_fill(match: re.Match[str], fill_color: str) -> str:
    style = match.group(1)
    updated = re.sub(
        r'(fill\s*:\s*)(?!none)(#[0-9a-fA-F]{3,8}|[a-zA-Z]+)',
        lambda m: f"{m.group(1)}{fill_color}",
        style,
        flags=re.IGNORECASE,
    )
    return f'style="{updated}"'


def load_svg_content(
    path: Union[str, Path],
    fill_color: str,
    fallback: Optional[Union[str, Path]] = None,
) -> str:
    """Lê um arquivo SVG, ajusta a cor e retorna uma tag <img> embutida."""
    svg_path = _resolve_asset_path(path)
    fallback_path = _resolve_asset_path(fallback) if fallback else None

    content: Optional[str] = None
    used_fallback = False

    for candidate in (svg_path, fallback_path):
        if candidate and candidate.exists():
            with candidate.open('r', encoding='utf-8') as f:
                content = f.read()
            used_fallback = candidate == fallback_path
            break

    if content is None:
        for name in filter(None, [Path(path).name, Path(fallback).name if fallback else None]):
            if name in DEFAULT_GEARS:
                content = DEFAULT_GEARS[name]
                used_fallback = True
                break

    if content is None:
        return ''

    content = _sanitize_svg(content)

    has_shapes = re.search(
        r"<(path|polygon|circle|rect|line|polyline)\b",
        content,
        flags=re.IGNORECASE,
    )

    if not has_shapes:
        if fallback_path and fallback_path.exists() and not used_fallback:
            return load_svg_content(fallback_path, fill_color)
        for name in filter(None, [Path(fallback).name if fallback else None, Path(path).name]):
            if name in DEFAULT_GEARS:
                content = _sanitize_svg(DEFAULT_GEARS[name])
                break
        else:
            return ''

    content = re.sub(
        r'fill\s*=\s*"(?!none)([^"\']*)"',
        f'fill="{fill_color}"',
        content,
        flags=re.IGNORECASE,
    )

    content = re.sub(
        r'(fill\s*:\s*)(?!none)(#[0-9a-fA-F]{3,8}|[a-zA-Z]+)',
        lambda m: f"{m.group(1)}{fill_color}",
        content,
        flags=re.IGNORECASE,
    )

    content = re.sub(
        r'style\s*=\s*"([^"]*)"',
        lambda m: _replace_style_fill(m, fill_color),
        content,
        flags=re.IGNORECASE,
    )

    encoded = base64.b64encode(content.encode('utf-8')).decode('ascii')
    return f'<img src="data:image/svg+xml;base64,{encoded}" alt="gear" />'


# ============================
# CONFIGURAÇÃO INICIAL
# ============================
st.set_page_config(page_title="Maestro", layout="wide")
init_metrics()

# Log de inicialização da aplicação
logger.info("Maestro Front iniciando", extra={"version": "1.0.0", "page": "init"})

# Carrega CSS customizado
with open("assets/style.css", "r", encoding="utf-8") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


# ============================
# FUNÇÃO PARA CARREGAR SVG LOCAL
# ============================

# Carrega o conteúdo SVG das 3 engrenagens (baseado em Maestro.png)
gear_red_svg = load_svg_content("1.svg", "#A52A2A", fallback="gear_red.svg")
gear_green_svg = load_svg_content("2.svg", "#2D8659", fallback="gear_green.svg")
gear_yellow_svg = load_svg_content("3.svg", "#F5C518", fallback="gear_yellow.svg")

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
    ["🏠 Início", "📂 Épicos", "🧠 Análises", "💬 Prompts", "🏷️ Tags", "🔗 Integrações", "⚙️ Administração", "📈 Observabilidade"]
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

def render_observabilidade():
    track_page_view("observabilidade")
    with observe_render("pagina_observabilidade"):
        logger.info("Acessando página de observabilidade", extra={"page": "observabilidade"})

        st.markdown("### 📈 Observabilidade – Grafana")

        grafana_url = _get_setting("grafana_url", "GRAFANA_URL", "http://200.229.76.122:3000")
        grafana_user = _get_setting("grafana_user", "GRAFANA_USER", "admin")
        grafana_pass = _get_setting("grafana_pass", "GRAFANA_PASS", "maestro2024")

        # URL do dashboard de logs
        logs_dashboard_url = f"{grafana_url}/d/maestro-logs/maestro-logs-dashboard"

        st.info(
            "Ao abrir o painel será necessário autenticar no Grafana. "
            f"Use usuário **{grafana_user}** e senha **{grafana_pass}**."
        )

        col1, col2 = st.columns(2)

        with col1:
            if st.button("📊 Abrir Grafana Home"):
                logger.info("Abrindo Grafana home", extra={"action": "open_grafana"})
                st.markdown(
                    f'<meta http-equiv="refresh" content="0; url={grafana_url}">',
                    unsafe_allow_html=True,
                )

        with col2:
            if st.button("📝 Abrir Dashboard de Logs"):
                logger.info("Abrindo dashboard de logs", extra={"action": "open_logs_dashboard"})
                st.markdown(
                    f'<meta http-equiv="refresh" content="0; url={logs_dashboard_url}">',
                    unsafe_allow_html=True,
                )

        st.markdown("---")
        st.markdown("#### 📝 Dashboard de Logs - Visualização Integrada")

        # Credenciais
        with st.expander("🔑 Credenciais de Acesso"):
            st.code(
                f"Usuario: {grafana_user}\n"
                f"Senha: {grafana_pass}",
                language="bash",
            )

        # Iframe do dashboard de logs por padrão
        components.iframe(logs_dashboard_url, height=900, scrolling=True)

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

elif menu == "📈 Observabilidade":
    render_observabilidade()
