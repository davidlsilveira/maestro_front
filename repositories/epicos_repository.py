"""
Repositório para gerenciar Épicos no banco de dados.
"""

import os
from typing import Dict, List, Optional

from database.connection import get_db_connection
from observability.metrics import db_operation


def get_default_client_id() -> int:
    """Retorna o ID do cliente padrão configurado no .env."""
    return int(os.getenv("DEFAULT_CLIENT_ID", "1"))


@db_operation("listar_epicos")
def listar_epicos(id_cliente: Optional[int] = None) -> List[Dict]:
    """
    Lista todos os épicos de um cliente.

    Args:
        id_cliente: ID do cliente (usa DEFAULT_CLIENT_ID se não fornecido)

    Returns:
        Lista de épicos como dicionários
    """
    if id_cliente is None:
        id_cliente = get_default_client_id()

    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT
                    id_epico,
                    titulo,
                    descricao_inicial as descricao,
                    status,
                    tag_atual as tag,
                    origem,
                    external_id,
                    azure_id,
                    criado_em,
                    atualizado_em
                FROM epicos
                WHERE id_cliente = %s
                ORDER BY atualizado_em DESC
            """, (id_cliente,))

            results = cur.fetchall()

            # Converter para lista de dicionários (já vem como RealDictRow)
            return [dict(row) for row in results]


@db_operation("buscar_epico_por_id")
def buscar_epico_por_id(id_epico: int) -> Optional[Dict]:
    """
    Busca um épico específico pelo ID.

    Args:
        id_epico: ID do épico

    Returns:
        Dicionário com dados do épico ou None se não encontrado
    """
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT
                    e.id_epico,
                    e.titulo,
                    e.descricao_inicial as descricao,
                    e.discussao,
                    e.status,
                    e.tag_atual as tag,
                    e.origem,
                    e.external_id,
                    e.azure_id,
                    e.criado_em,
                    e.atualizado_em,
                    e.id_cliente
                FROM epicos e
                WHERE e.id_epico = %s
            """, (id_epico,))

            result = cur.fetchone()
            return dict(result) if result else None


@db_operation("criar_epico")
def criar_epico(
    titulo: str,
    descricao: str,
    origem: str = "manual",
    tag: str = "analise_pre",
    external_id: Optional[str] = None,
    contexto: Optional[str] = None,
    id_cliente: Optional[int] = None
) -> int:
    """
    Cria um novo épico no banco de dados.

    Args:
        titulo: Título do épico
        descricao: Descrição inicial do épico
        origem: Origem do épico (manual, azure, jira)
        tag: Tag inicial (analise_pre, wbs, refino)
        external_id: ID externo (Azure DevOps, Jira, etc.)
        contexto: Contexto adicional
        id_cliente: ID do cliente (usa DEFAULT_CLIENT_ID se não fornecido)

    Returns:
        ID do épico criado
    """
    if id_cliente is None:
        id_cliente = get_default_client_id()

    # Se não houver external_id, gerar um baseado no timestamp
    if not external_id:
        import time
        external_id = f"EP{int(time.time())}"

    # Combinar descrição e contexto se houver contexto
    descricao_completa = descricao
    if contexto:
        descricao_completa = f"{descricao}\n\nContexto adicional:\n{contexto}"

    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO epicos (
                    id_cliente,
                    origem,
                    external_id,
                    titulo,
                    descricao_inicial,
                    tag_atual,
                    status
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, 'em_analise'
                )
                RETURNING id_epico
            """, (id_cliente, origem, external_id, titulo, descricao_completa, tag))

            result = cur.fetchone()
            return result['id_epico']


@db_operation("atualizar_epico")
def atualizar_epico(
    id_epico: int,
    titulo: Optional[str] = None,
    descricao: Optional[str] = None,
    status: Optional[str] = None,
    tag: Optional[str] = None
) -> bool:
    """
    Atualiza um épico existente.

    Args:
        id_epico: ID do épico
        titulo: Novo título (opcional)
        descricao: Nova descrição (opcional)
        status: Novo status (opcional)
        tag: Nova tag (opcional)

    Returns:
        True se atualizou, False se não encontrou
    """
    # Montar query dinâmica apenas com campos fornecidos
    updates = []
    params = []

    if titulo is not None:
        updates.append("titulo = %s")
        params.append(titulo)

    if descricao is not None:
        updates.append("descricao_inicial = %s")
        params.append(descricao)

    if status is not None:
        updates.append("status = %s")
        params.append(status)

    if tag is not None:
        updates.append("tag_atual = %s")
        params.append(tag)

    if not updates:
        return False

    # Adicionar updated_at
    updates.append("atualizado_em = NOW()")
    params.append(id_epico)

    query = f"""
        UPDATE epicos
        SET {', '.join(updates)}
        WHERE id_epico = %s
    """

    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, params)
            return cur.rowcount > 0


@db_operation("contar_epicos")
def contar_epicos(id_cliente: Optional[int] = None) -> int:
    """
    Conta o número total de épicos de um cliente.

    Args:
        id_cliente: ID do cliente (usa DEFAULT_CLIENT_ID se não fornecido)

    Returns:
        Número de épicos
    """
    if id_cliente is None:
        id_cliente = get_default_client_id()

    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT COUNT(*) as total
                FROM epicos
                WHERE id_cliente = %s
            """, (id_cliente,))

            result = cur.fetchone()
            return result['total']
