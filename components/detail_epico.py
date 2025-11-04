import html
import json
import re
from typing import Any, Dict, List, Optional, Tuple

import streamlit as st
from repositories.analises_repository import buscar_analises_por_epico
from repositories.epicos_repository import listar_epicos


def _format_label(label: str) -> str:
    """Transforma chaves em rótulos legíveis."""
    return label.replace("_", " ").strip().capitalize()


def _value_to_text(value: Any) -> str:
    """Converte um valor arbitrário em texto simples."""
    if isinstance(value, (str, int, float)):
        return str(value)
    if isinstance(value, list):
        return ", ".join(_value_to_text(item) for item in value)
    if isinstance(value, dict):
        return ", ".join(
            f"{_format_label(str(k))}: {_value_to_text(v)}" for k, v in value.items()
        )
    return str(value)


def _value_to_html(value: Any) -> str:
    """Converte valores em HTML amigável."""
    if isinstance(value, dict):
        title = value.get("name") or value.get("title")
        description = value.get("description") or value.get("descricao")
        pills: List[str] = []
        for key, val in value.items():
            if key in {"name", "title", "description", "descricao"}:
                continue
            if val in (None, "", []):
                continue
            pills.append(
                f"<span class='azure-pill'>{html.escape(_format_label(str(key)))}: "
                f"{html.escape(_value_to_text(val))}</span>"
            )

        parts = []
        if title:
            parts.append(f"<strong>{html.escape(str(title))}</strong>")
        if description:
            parts.append(f"<div>{html.escape(str(description))}</div>")
        if pills:
            parts.append(
                "<div class='azure-pill-container'>" + " ".join(pills) + "</div>"
            )

        if not parts:
            return html.escape(_value_to_text(value))
        return "".join(parts)

    if isinstance(value, list):
        return _list_to_html(value)

    return html.escape(_value_to_text(value))


def _list_to_html(items: List[Any]) -> str:
    """Gera uma lista HTML a partir de valores simples ou estruturados."""
    if not items:
        return ""

    parts = ["<ul>"]
    for item in items:
        parts.append(f"<li>{_value_to_html(item)}</li>")
    parts.append("</ul>")
    return "".join(parts)


def _split_azure_sections(resultado: str) -> List[Dict[str, str]]:
    """Divide o conteúdo retornado pela IA em seções markdown nomeadas."""
    if not resultado:
        return []

    section_pattern = re.compile(r"^##\s*(?:\d+\.\s*)?(?P<title>.+)$")
    sections: List[Dict[str, str]] = []
    current_title: Optional[str] = None
    current_lines: List[str] = []

    for raw_line in resultado.splitlines():
        stripped = raw_line.strip()
        header = section_pattern.match(stripped)

        if header:
            if current_title is not None:
                sections.append(
                    {
                        "title": current_title,
                        "body": "\n".join(current_lines).strip(),
                    }
                )
            current_title = header.group("title").strip()
            current_lines = []
        else:
            if current_title is None:
                current_title = "Resumo"
            current_lines.append(raw_line)

    if current_title is not None:
        sections.append(
            {
                "title": current_title,
                "body": "\n".join(current_lines).strip(),
            }
        )

    return [section for section in sections if section["body"]]


def _markdown_to_simple_html(markdown_text: str) -> str:
    """Converte markdown simples em HTML básico (títulos e listas)."""
    if not markdown_text:
        return "<p>Sem conteúdo disponível.</p>"

    lines = markdown_text.splitlines()
    html_parts: List[str] = []
    in_list = False

    for raw_line in lines:
        stripped = raw_line.strip()

        if not stripped:
            if in_list:
                html_parts.append("</ul>")
                in_list = False
            continue

        if stripped.startswith("-"):
            if not in_list:
                html_parts.append("<ul>")
                in_list = True
            item_text = html.escape(stripped[1:].strip())
            html_parts.append(f"<li>{item_text}</li>")
        else:
            if in_list:
                html_parts.append("</ul>")
                in_list = False
            html_parts.append(f"<p>{html.escape(stripped)}</p>")

    if in_list:
        html_parts.append("</ul>")

    return "\n".join(html_parts) or "<p>Sem conteúdo disponível.</p>"


def _try_parse_json_result(resultado: str) -> Optional[Tuple[Optional[str], Any]]:
    """Tenta interpretar a resposta como JSON, preservando prefixos textuais."""
    if not resultado:
        return None

    text = resultado.strip()

    try:
        return None, json.loads(text)
    except json.JSONDecodeError:
        pass

    start = text.find("{")
    if start == -1:
        return None

    prefix = text[:start].strip() or None
    json_payload = text[start:]

    try:
        return prefix, json.loads(json_payload)
    except json.JSONDecodeError:
        return None


def _render_user_stories_html(stories: List[Dict[str, Any]]) -> str:
    if not stories:
        return ""

    rendered: List[str] = []
    for story in stories:
        if not isinstance(story, dict):
            rendered.append(
                f"<div class='azure-story'>{html.escape(_value_to_text(story))}</div>"
            )
            continue

        title = story.get("name") or story.get("title") or "História"
        description = story.get("description") or story.get("descricao")

        pills: List[str] = []
        for key in (
            "priority",
            "story_points",
            "business_value",
            "status",
            "owner",
        ):
            value = story.get(key)
            if value in (None, "", []):
                continue
            pills.append(
                f"<span class='azure-pill'>{html.escape(_format_label(str(key)))}: "
                f"{html.escape(_value_to_text(value))}</span>"
            )

        other_keys = set(story.keys()) - {
            "name",
            "title",
            "description",
            "descricao",
            "acceptance_criteria",
            "tasks",
            "priority",
            "story_points",
            "business_value",
            "status",
            "owner",
        }

        for key in sorted(other_keys):
            value = story.get(key)
            if value in (None, "", []):
                continue
            pills.append(
                f"<span class='azure-pill'>{html.escape(_format_label(str(key)))}: "
                f"{html.escape(_value_to_text(value))}</span>"
            )

        pills_html = ""
        if pills:
            pills_html = "<div class='azure-pill-container'>" + " ".join(pills) + "</div>"

        acceptance_html = ""
        if story.get("acceptance_criteria"):
            acceptance_html = (
                "<div class='azure-subtitle'>Critérios de aceite</div>"
                + _list_to_html(story["acceptance_criteria"])
            )

        tasks_html = ""
        if story.get("tasks"):
            tasks_html = (
                "<div class='azure-subtitle'>Tarefas sugeridas</div>"
                + _list_to_html(story["tasks"])
            )

        story_body = "".join(
            filter(
                None,
                [
                    f"<div class='azure-story__title'>{html.escape(str(title))}</div>",
                    f"<p>{html.escape(str(description))}</p>" if description else "",
                    pills_html,
                    acceptance_html,
                    tasks_html,
                ],
            )
        )

        rendered.append(
            f"<div class='azure-story'>{story_body or html.escape(_value_to_text(story))}</div>"
        )

    return "".join(rendered)


def _render_epic_json(payload: Dict[str, Any], prefix: Optional[str]) -> None:
    if prefix:
        st.markdown(f"### {html.escape(prefix)}")

    epic_data = payload.get("epic") or {}
    summary_parts: List[str] = []

    title = epic_data.get("title")
    if title:
        summary_parts.append(
            f"<p><strong>Título:</strong> {html.escape(str(title))}</p>"
        )

    metrics: List[str] = []
    for key in ("total_story_points", "total_hours", "total_cost"):
        value = epic_data.get(key)
        if value in (None, "", []):
            continue
        metrics.append(
            f"<span class='azure-pill'>{html.escape(_format_label(str(key)))}: "
            f"{html.escape(_value_to_text(value))}</span>"
        )

    if metrics:
        summary_parts.append(
            "<div class='azure-pill-container'>" + " ".join(metrics) + "</div>"
        )

    other_fields: List[str] = []
    for key, value in epic_data.items():
        if key in {"title", "total_story_points", "total_hours", "total_cost"}:
            continue
        if value in (None, "", []):
            continue
        other_fields.append(
            f"<div><strong>{html.escape(_format_label(str(key)))}:</strong> "
            f"{_value_to_html(value)}</div>"
        )

    if other_fields:
        summary_parts.extend(other_fields)

    st.markdown(
        f"""
        <div class="azure-section">
            <div class="azure-section__header">Resumo do Épico</div>
            <div class="azure-section__body">
                {''.join(summary_parts) or '<p>Sem dados do épico.</p>'}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    features = payload.get("features") or []
    if not features:
        return

    for idx, feature in enumerate(features, start=1):
        if not isinstance(feature, dict):
            st.markdown(
                f"""
                <div class="azure-section">
                    <div class="azure-section__header">Funcionalidade {idx}</div>
                    <div class="azure-section__body">
                        <p>{html.escape(_value_to_text(feature))}</p>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            continue

        feature_name = feature.get("name") or f"Funcionalidade {idx}"
        description = feature.get("description") or feature.get("descricao")

        pills: List[str] = []
        for key in ("business_value", "story_points", "status", "owner"):
            value = feature.get(key)
            if value in (None, "", []):
                continue
            pills.append(
                f"<span class='azure-pill'>{html.escape(_format_label(str(key)))}: "
                f"{html.escape(_value_to_text(value))}</span>"
            )

        other_keys = set(feature.keys()) - {
            "name",
            "description",
            "descricao",
            "business_value",
            "story_points",
            "status",
            "owner",
            "user_stories",
            "acceptance_criteria",
            "tasks",
        }
        other_fields_html: List[str] = []

        for key in sorted(other_keys):
            value = feature.get(key)
            if value in (None, "", []):
                continue
            other_fields_html.append(
                f"<div><strong>{html.escape(_format_label(str(key)))}:</strong> "
                f"{_value_to_html(value)}</div>"
            )

        acceptance_html = ""
        if feature.get("acceptance_criteria"):
            acceptance_html = (
                "<div class='azure-subtitle'>Critérios de aceite</div>"
                + _list_to_html(feature["acceptance_criteria"])
            )

        tasks_html = ""
        if feature.get("tasks"):
            tasks_html = (
                "<div class='azure-subtitle'>Tarefas sugeridas</div>"
                + _list_to_html(feature["tasks"])
            )

        stories_html = ""
        if feature.get("user_stories"):
            stories_html = (
                "<div class='azure-subtitle'>Histórias de usuário</div>"
                + _render_user_stories_html(feature["user_stories"])
            )

        body_parts = [
            f"<p>{html.escape(str(description))}</p>" if description else "",
            "<div class='azure-pill-container'>" + " ".join(pills) + "</div>"
            if pills
            else "",
            "".join(other_fields_html),
            acceptance_html,
            stories_html,
            tasks_html,
        ]

        st.markdown(
            f"""
            <div class="azure-section">
                <div class="azure-section__header">🧩 {html.escape(str(feature_name))}</div>
                <div class="azure-section__body">
                    {''.join(part for part in body_parts if part)}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def _render_json_result(resultado: str) -> bool:
    parsed = _try_parse_json_result(resultado)
    if not parsed:
        return False

    prefix, payload = parsed

    if isinstance(payload, dict) and ("epic" in payload or "features" in payload):
        _render_epic_json(payload, prefix)
        return True

    if prefix:
        st.markdown(f"### {html.escape(prefix)}")

    st.markdown(
        f"""
        <div class="azure-section">
            <div class="azure-section__header">Informações</div>
            <div class="azure-section__body">{_value_to_html(payload)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    return True


def _render_formatted_result(resultado: str) -> None:
    if _render_json_result(resultado):
        return

    sections = _split_azure_sections(resultado)

    if not sections:
        st.markdown("Sem conteúdo estruturado. Visualizando saída original abaixo:")
        st.markdown(resultado or "_Sem conteúdo_", unsafe_allow_html=True)
        return

    for index, section in enumerate(sections, start=1):
        section_title = html.escape(section["title"])
        body_html = _markdown_to_simple_html(section["body"])
        st.markdown(
            f"""
            <div class="azure-section">
                <div class="azure-section__header">{index}. {section_title}</div>
                <div class="azure-section__body">{body_html}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def show_detail_epico():
    st.subheader("🧠 Detalhe do Épico")

    try:
        epicos = listar_epicos()

        if not epicos:
            st.info("Nenhum épico cadastrado ainda.")
            return

        opcoes = {f"{e['titulo']} (ID: {e['id_epico']})": e["id_epico"] for e in epicos}

        if not opcoes:
            st.info("Nenhum épico disponível para análise.")
            return

        selecionado = st.selectbox(
            "Selecione um épico para visualizar as análises:",
            list(opcoes.keys()),
        )

        id_epico_selecionado = opcoes[selecionado]

        analises = buscar_analises_por_epico(id_epico_selecionado)

        if not analises:
            st.warning("⏳ Nenhuma análise foi executada para este épico ainda.")
            st.info(
                "As análises são geradas automaticamente quando o épico recebe a tag"
                " 'Maestro Executar' ou 'Maestro Revisar' no Azure DevOps."
            )
            return

        epico_info = next(
            (e for e in epicos if e["id_epico"] == id_epico_selecionado), None
        )

        if epico_info:
            st.markdown(f"### 🧠 Épico: {epico_info['titulo']}")
            st.markdown("---")

            col1, col2, col3 = st.columns(3)
            col1.metric("Status", epico_info["status"])
            col2.metric("Tag Atual", epico_info["tag"])
            col3.metric("Origem", epico_info["origem"])

            st.markdown("---")

        st.markdown(f"#### 📊 Análises Executadas ({len(analises)})")

        for idx, analise in enumerate(analises, 1):
            with st.expander(
                f"🧾 Análise #{idx} - {analise['data']} ({analise['prompt_contexto']})"
            ):
                col1, col2, col3 = st.columns(3)
                col1.metric("Modelo", analise["modelo"])
                col2.metric("Tokens", analise.get("tokens_consumidos", "N/A"))
                col3.metric("Custo (R$)", f"{analise.get('custo_estimado', 0):.4f}")

                st.markdown(f"**Prompt:** {analise['prompt_nome']}")
                st.markdown(f"**Status:** {analise['status']}")

                st.markdown("---")
                st.markdown("#### 📄 Resultado da Análise")

                view_mode = st.radio(
                    "Formato de visualização",
                    ("Visualização Azure", "Saída do Azure"),
                    key=f"view-mode-{analise['id_execucao']}",
                    horizontal=True,
                )

                if view_mode == "Visualização Azure":
                    _render_formatted_result(analise.get("resultado", ""))
                else:
                    st.text_area(
                        "Saída bruta",
                        analise.get("resultado", ""),
                        key=f"view-raw-{analise['id_execucao']}",
                        height=300,
                    )

    except Exception as e:
        st.error(f"⚠️ Erro ao carregar análises: {str(e)}")
        st.info("Verifique se o banco de dados está acessível.")
