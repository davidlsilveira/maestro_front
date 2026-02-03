"""
RAG Help Component - Sistema de ajuda inteligente com busca semântica.

Este módulo implementa um sistema RAG (Retrieval-Augmented Generation) para
responder perguntas dos usuários baseado nos manuais do Maestro.
"""

import os
import re
import hashlib
from pathlib import Path
from typing import List, Dict, Optional
from dataclasses import dataclass

import streamlit as st
import numpy as np

try:
    import tiktoken
    TIKTOKEN_AVAILABLE = True
except ImportError:
    TIKTOKEN_AVAILABLE = False

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False


# ============================
# CONFIGURAÇÕES RAG
# ============================
# Chunks: 1-2k caracteres com 20% overlap
# Isso melhora a qualidade das respostas mantendo contexto suficiente
#
# IMPORTANTE: Incrementar RAG_VERSION para forçar reindexação quando
# os manuais ou configurações de chunking mudarem.

RAG_VERSION = "4.2.0"  # Incrementar para forçar reindex

CHUNK_SIZE = 1800  # 1.8k caracteres por chunk (range ideal: 1-2k)
CHUNK_OVERLAP = 360  # 20% de 1800 = 360 (overlap para manter contexto)
TOP_K_CHUNKS = 5  # Número de chunks mais relevantes para busca
MAX_CONTEXT_TOKENS = 8000  # Aumentado para suportar chunks maiores
EMBEDDING_MODEL = "text-embedding-3-small"  # Modelo mais recente e eficiente
CHAT_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

BASE_DIR = Path(__file__).resolve().parent.parent
HELP_DATA_DIR = BASE_DIR / "data" / "help"


# ============================
# DATA CLASSES
# ============================

@dataclass
class Chunk:
    """Representa um pedaço do documento."""
    id: str
    content: str
    section: str
    source: str
    embedding: Optional[List[float]] = None


@dataclass
class SearchResult:
    """Resultado de busca com score de similaridade."""
    chunk: Chunk
    score: float


# ============================
# RAG ENGINE
# ============================

class RAGHelpEngine:
    """Motor de RAG para sistema de ajuda."""

    def __init__(self, manual_path: str, manual_type: str = "usuario"):
        self.manual_path = Path(manual_path)
        self.manual_type = manual_type
        self.chunks: List[Chunk] = []
        self.client: Optional[OpenAI] = None
        # Cache key inclui versão para forçar reindex quando configurações mudarem
        self._cache_key = f"rag_cache_{manual_type}_v{RAG_VERSION}"

        # Inicializar cliente OpenAI
        api_key = os.getenv("OPENAI_API_KEY")
        if api_key and api_key.strip() and OPENAI_AVAILABLE:
            try:
                self.client = OpenAI(api_key=api_key)
            except Exception:
                self.client = None

        self._load_and_process()

    def _get_file_hash(self) -> str:
        if self.manual_path.exists():
            content = self.manual_path.read_text(encoding="utf-8")
            return hashlib.md5(content.encode()).hexdigest()
        return ""

    def _load_and_process(self):
        if not self.manual_path.exists():
            return

        file_hash = self._get_file_hash()
        cache_key = f"{self._cache_key}_{file_hash}"

        if cache_key in st.session_state:
            self.chunks = st.session_state[cache_key]
            return

        content = self.manual_path.read_text(encoding="utf-8")
        self.chunks = self._create_chunks(content)

        if self.client:
            self._generate_embeddings()

        st.session_state[cache_key] = self.chunks

    def _create_chunks(self, content: str) -> List[Chunk]:
        chunks = []
        sections = re.split(r'\n(?=##\s)', content)

        for section in sections:
            if not section.strip():
                continue

            title_match = re.match(r'^(#{2,3})\s+(.+?)(?:\n|$)', section)
            section_title = title_match.group(2) if title_match else "Introdução"

            if len(section) <= CHUNK_SIZE:
                chunk_id = hashlib.md5(section[:100].encode()).hexdigest()[:8]
                chunks.append(Chunk(
                    id=chunk_id,
                    content=section.strip(),
                    section=section_title,
                    source=self.manual_path.name
                ))
            else:
                sub_chunks = self._split_large_section(section, section_title)
                chunks.extend(sub_chunks)

        return chunks

    def _split_large_section(self, section: str, section_title: str) -> List[Chunk]:
        chunks = []
        paragraphs = re.split(r'\n\n+', section)
        current_chunk = ""

        for para in paragraphs:
            if len(current_chunk) + len(para) <= CHUNK_SIZE:
                current_chunk += para + "\n\n"
            else:
                if current_chunk.strip():
                    chunk_id = hashlib.md5(current_chunk[:100].encode()).hexdigest()[:8]
                    chunks.append(Chunk(
                        id=chunk_id,
                        content=current_chunk.strip(),
                        section=section_title,
                        source=self.manual_path.name
                    ))
                overlap_start = max(0, len(current_chunk) - CHUNK_OVERLAP)
                current_chunk = current_chunk[overlap_start:] + para + "\n\n"

        if current_chunk.strip():
            chunk_id = hashlib.md5(current_chunk[:100].encode()).hexdigest()[:8]
            chunks.append(Chunk(
                id=chunk_id,
                content=current_chunk.strip(),
                section=section_title,
                source=self.manual_path.name
            ))

        return chunks

    def _generate_embeddings(self):
        if not self.client or not self.chunks:
            return

        try:
            texts = [chunk.content for chunk in self.chunks]
            batch_size = 100

            for i in range(0, len(texts), batch_size):
                batch = texts[i:i + batch_size]
                response = self.client.embeddings.create(
                    model=EMBEDDING_MODEL,
                    input=batch
                )
                for j, embedding_data in enumerate(response.data):
                    self.chunks[i + j].embedding = embedding_data.embedding

        except Exception:
            pass

    def _cosine_similarity(self, a: List[float], b: List[float]) -> float:
        a = np.array(a)
        b = np.array(b)
        return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

    def _keyword_search(self, query: str, top_k: int = TOP_K_CHUNKS) -> List[SearchResult]:
        results = []
        query_terms = set(query.lower().split())

        for chunk in self.chunks:
            content_lower = chunk.content.lower()
            matches = sum(1 for term in query_terms if term in content_lower)

            if query.lower() in content_lower:
                matches += 3

            if any(term in chunk.section.lower() for term in query_terms):
                matches += 2

            if matches > 0:
                score = matches / len(query_terms)
                results.append(SearchResult(chunk=chunk, score=score))

        results.sort(key=lambda x: x.score, reverse=True)
        return results[:top_k]

    def search(self, query: str, top_k: int = TOP_K_CHUNKS) -> List[SearchResult]:
        if self.client and all(chunk.embedding for chunk in self.chunks):
            try:
                response = self.client.embeddings.create(
                    model=EMBEDDING_MODEL,
                    input=query
                )
                query_embedding = response.data[0].embedding

                results = []
                for chunk in self.chunks:
                    score = self._cosine_similarity(query_embedding, chunk.embedding)
                    results.append(SearchResult(chunk=chunk, score=score))

                results.sort(key=lambda x: x.score, reverse=True)
                return results[:top_k]

            except Exception:
                return self._keyword_search(query, top_k)
        else:
            return self._keyword_search(query, top_k)

    def generate_answer(self, query: str, search_results: List[SearchResult]) -> str:
        if not self.client:
            return self._generate_fallback_answer(query, search_results)

        context_parts = []
        for result in search_results:
            context_parts.append(f"[Seção: {result.chunk.section}]\n{result.chunk.content}")

        context = "\n\n---\n\n".join(context_parts)

        if self.manual_type == "usuario":
            system_prompt = """Você é o assistente de ajuda do Maestro, especializado em ajudar usuários de negócio.

Sua função é:
- Explicar como usar o sistema de forma clara e simples
- Guiar o usuário passo a passo quando necessário
- Usar linguagem acessível, evitando termos técnicos desnecessários
- Dar exemplos práticos sempre que possível
- Se a pergunta não puder ser respondida com o contexto fornecido, diga honestamente

O Maestro é um sistema que automatiza a criação de Product Backlog (Features, User Stories, Tasks) a partir de Epics.

Responda SEMPRE em português brasileiro.
Seja direto e objetivo, mas completo.
Use formatação markdown para melhor legibilidade."""
        else:
            system_prompt = """Você é o assistente técnico do Maestro, especializado em ajudar desenvolvedores e equipe de infraestrutura.

Sua função é:
- Explicar detalhes técnicos de arquitetura e implementação
- Fornecer comandos, configurações e código quando relevante
- Guiar na instalação, deploy e troubleshooting
- Explicar fluxos de dados e integrações
- Se a pergunta não puder ser respondida com o contexto fornecido, diga honestamente

Responda SEMPRE em português brasileiro.
Seja técnico e preciso, incluindo detalhes relevantes.
Use formatação markdown, especialmente code blocks para comandos e código."""

        try:
            response = self.client.chat.completions.create(
                model=CHAT_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"""Contexto da documentação:

{context}

---

Pergunta do usuário: {query}

Responda baseado no contexto acima. Se a informação não estiver no contexto, informe que não encontrou a resposta na documentação."""}
                ],
                temperature=0.3,
                max_tokens=2000
            )

            return response.choices[0].message.content

        except Exception as e:
            return self._generate_fallback_answer(query, search_results)

    def _generate_fallback_answer(self, query: str, search_results: List[SearchResult]) -> str:
        if not search_results:
            return "Desculpe, não encontrei informações relevantes para sua pergunta. Tente reformular ou consulte o manual completo."

        response = "**Encontrei as seguintes informações relevantes:**\n\n"

        for i, result in enumerate(search_results[:3], 1):
            response += f"### {i}. {result.chunk.section}\n\n"
            content = result.chunk.content[:500]
            if len(result.chunk.content) > 500:
                content += "..."
            response += f"{content}\n\n"

        return response

    def get_stats(self) -> Dict:
        """Retorna estatísticas do índice RAG."""
        total_chars = sum(len(c.content) for c in self.chunks)
        avg_chunk_size = total_chars / len(self.chunks) if self.chunks else 0
        sections = set(c.section for c in self.chunks)

        return {
            "version": RAG_VERSION,
            "total_chunks": len(self.chunks),
            "total_chars": total_chars,
            "avg_chunk_size": round(avg_chunk_size),
            "unique_sections": len(sections),
            "has_embeddings": all(c.embedding for c in self.chunks) if self.chunks else False,
            "chunk_config": {
                "size": CHUNK_SIZE,
                "overlap": CHUNK_OVERLAP,
                "overlap_percent": round(CHUNK_OVERLAP / CHUNK_SIZE * 100)
            }
        }


# ============================
# COMPONENTES STREAMLIT
# ============================

def render_help_chat(manual_type: str = "usuario"):
    """Renderiza a interface de chat do help."""

    if manual_type == "usuario":
        st.markdown("### 📚 Central de Ajuda - Usuário")
        st.markdown("""
        Tire suas dúvidas sobre como usar o **Maestro**!

        Exemplos de perguntas:
        - *Como adicionar uma tag a um Epic?*
        - *O que significa o score do Code Review?*
        - *Quais são os fluxos de trabalho disponíveis?*
        - *Como gerar um Product Backlog completo?*
        """)
        manual_file = HELP_DATA_DIR / "MANUAL_USUARIO.md"
    else:
        st.markdown("### 🔧 Central de Ajuda - Desenvolvedor")
        st.markdown("""
        Tire suas dúvidas sobre a **arquitetura e implementação** do Maestro!

        Exemplos de perguntas:
        - *Como subir o ambiente com Docker?*
        - *Qual a estrutura do banco de dados?*
        - *Como funciona o Tag Detector?*
        - *Como adicionar uma nova ação no sistema?*
        """)
        manual_file = HELP_DATA_DIR / "MANUAL_TECNICO.md"

    if not manual_file.exists():
        st.error(f"❌ Manual não encontrado: {manual_file}")
        st.info("Execute o comando para copiar os manuais para o diretório data/help/")
        return

    # Inicializar engine (com cache)
    engine_key = f"rag_engine_{manual_type}"
    if engine_key not in st.session_state:
        with st.spinner("Carregando base de conhecimento..."):
            st.session_state[engine_key] = RAGHelpEngine(
                manual_path=str(manual_file),
                manual_type=manual_type
            )

    engine = st.session_state[engine_key]

    # Indicador de status com estatísticas
    stats = engine.get_stats()
    col1, col2 = st.columns([3, 1])

    with col1:
        if engine.client and stats["has_embeddings"]:
            st.success("✅ Assistente inteligente ativo")
        else:
            st.info("💡 Busca por palavras-chave ativa")

    with col2:
        with st.expander("📊 Info"):
            st.caption(f"**Versão RAG:** {stats['version']}")
            st.caption(f"**Chunks:** {stats['total_chunks']}")
            st.caption(f"**Tamanho médio:** {stats['avg_chunk_size']} chars")
            st.caption(f"**Seções:** {stats['unique_sections']}")
            st.caption(f"**Config:** {stats['chunk_config']['size']} chars, {stats['chunk_config']['overlap_percent']}% overlap")

    st.markdown("---")

    # Histórico de chat
    history_key = f"chat_history_{manual_type}"
    if history_key not in st.session_state:
        st.session_state[history_key] = []

    # Exibir histórico
    for msg in st.session_state[history_key]:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Input do usuário
    if prompt := st.chat_input("Digite sua pergunta..."):
        st.session_state[history_key].append({"role": "user", "content": prompt})

        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Buscando informações..."):
                search_results = engine.search(prompt)
                answer = engine.generate_answer(prompt, search_results)
                st.markdown(answer)

                # Mostrar fontes de forma simplificada
                if search_results:
                    with st.expander("📖 Ver seções consultadas"):
                        for result in search_results[:3]:
                            st.markdown(f"• **{result.chunk.section}**")

        st.session_state[history_key].append({"role": "assistant", "content": answer})

    # Botão para limpar histórico
    if st.session_state[history_key]:
        if st.button("🗑️ Limpar conversa"):
            st.session_state[history_key] = []
            st.rerun()


def show_help_negocios():
    """Página principal do Help Negócios."""
    # Limpar histórico e cache ao entrar na página (nova sessão de ajuda)
    if st.session_state.get("current_help_page") != "negocios":
        st.session_state["chat_history_usuario"] = []
        st.session_state["current_help_page"] = "negocios"
        # Limpar cache do engine para recarregar com OpenAI
        if "rag_engine_usuario" in st.session_state:
            del st.session_state["rag_engine_usuario"]
        # Limpar caches de chunks
        keys_to_delete = [k for k in st.session_state.keys() if k.startswith("rag_cache_")]
        for k in keys_to_delete:
            del st.session_state[k]

    abas = st.tabs(["💬 Assistente", "📖 Manual Completo"])

    with abas[0]:
        render_help_chat("usuario")

    with abas[1]:
        manual_file = HELP_DATA_DIR / "MANUAL_USUARIO.md"
        if manual_file.exists():
            content = manual_file.read_text(encoding="utf-8")
            # Substituir WBS por Product Backlog no conteúdo exibido
            content = content.replace("WBS", "Product Backlog")
            content = content.replace("wbs", "product backlog")
            st.markdown(content)
        else:
            st.error("Manual não encontrado")


def show_help_tecnico():
    """Página principal do Help Técnico."""
    # Limpar histórico e cache ao entrar na página (nova sessão de ajuda)
    if st.session_state.get("current_help_page") != "tecnico":
        st.session_state["chat_history_tecnico"] = []
        st.session_state["current_help_page"] = "tecnico"
        # Limpar cache do engine para recarregar com OpenAI
        if "rag_engine_tecnico" in st.session_state:
            del st.session_state["rag_engine_tecnico"]
        # Limpar caches de chunks
        keys_to_delete = [k for k in st.session_state.keys() if k.startswith("rag_cache_")]
        for k in keys_to_delete:
            del st.session_state[k]

    abas = st.tabs(["💬 Assistente", "📖 Manual Completo"])

    with abas[0]:
        render_help_chat("tecnico")

    with abas[1]:
        manual_file = HELP_DATA_DIR / "MANUAL_TECNICO.md"
        if manual_file.exists():
            content = manual_file.read_text(encoding="utf-8")
            st.markdown(content)
        else:
            st.error("Manual não encontrado")
