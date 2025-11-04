"""
Repositório para gerenciar Tags no banco de dados.
"""

import os
from datetime import datetime
from typing import Dict, List, Optional

from database.connection import get_db_connection
from observability.metrics import db_operation


def get_default_client_id() -> int:
    """Retorna o ID do cliente padrão configurado no .env."""
    return int(os.getenv("DEFAULT_CLIENT_ID", "1"))


@db_operation("listar_tags")
def listar_tags(id_cliente: Optional[int] = None, apenas_ativas: bool = True) -> List[Dict]:
    """
    Lista todas as tags de um cliente.

    Args:
        id_cliente: ID do cliente (usa DEFAULT_CLIENT_ID se não fornecido)
        apenas_ativas: Se True, retorna apenas tags ativas

    Returns:
        Lista de tags como dicionários
    """
    if id_cliente is None:
        id_cliente = get_default_client_id()

    with get_db_connection() as conn:
        with conn.cursor() as cur:
            query = """
                SELECT
                    id_tag,
                    nome,
                    descricao,
                    cor_hex,
                    ativo,
                    criado_em,
                    atualizado_em
                FROM tags
                WHERE id_cliente = %s
            """

            params = [id_cliente]

            if apenas_ativas:
                query += " AND ativo = true"

            query += " ORDER BY nome"

            cur.execute(query, params)
            results = cur.fetchall()

            # Contar usos de cada tag
            tags = []
            for row in results:
                # Contar quantas vezes a tag foi usada em épicos
                cur.execute("""
                    SELECT COUNT(*) as total
                    FROM epicos
                    WHERE tag_atual = %s AND id_cliente = %s
                """, (row['nome'], id_cliente))

                uso_result = cur.fetchone()
                usos = uso_result['total'] if uso_result else 0

                # Contar ações associadas
                cur.execute("""
                    SELECT COUNT(*) as total
                    FROM tag_acoes
                    WHERE id_tag = %s AND ativo = true
                """, (row['id_tag'],))

                acoes_result = cur.fetchone()
                acoes_associadas = acoes_result['total'] if acoes_result else 0

                tag = {
                    "id_tag": row['id_tag'],
                    "nome": row['nome'],
                    "descricao": row['descricao'],
                    "cor_hex": row['cor_hex'],
                    "ativo": row['ativo'],
                    "criado_em": row['criado_em'],
                    "atualizado_em": row['atualizado_em'],
                    "usos": usos,
                    "acoes_associadas": acoes_associadas
                }
                tags.append(tag)

            return tags


@db_operation("buscar_tag_por_id")
def buscar_tag_por_id(id_tag: int) -> Optional[Dict]:
    """
    Busca uma tag específica pelo ID.

    Args:
        id_tag: ID da tag

    Returns:
        Dicionário com dados da tag ou None se não encontrada
    """
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT
                    id_tag,
                    id_cliente,
                    nome,
                    descricao,
                    cor_hex,
                    ativo,
                    criado_em,
                    atualizado_em
                FROM tags
                WHERE id_tag = %s
            """, (id_tag,))

            result = cur.fetchone()
            return dict(result) if result else None


@db_operation("buscar_tag_por_nome")
def buscar_tag_por_nome(nome: str, id_cliente: Optional[int] = None) -> Optional[Dict]:
    """
    Busca uma tag pelo nome.

    Args:
        nome: Nome da tag
        id_cliente: ID do cliente (usa DEFAULT_CLIENT_ID se não fornecido)

    Returns:
        Dicionário com dados da tag ou None se não encontrada
    """
    if id_cliente is None:
        id_cliente = get_default_client_id()

    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT
                    id_tag,
                    id_cliente,
                    nome,
                    descricao,
                    cor_hex,
                    ativo,
                    criado_em,
                    atualizado_em
                FROM tags
                WHERE nome = %s AND id_cliente = %s
            """, (nome, id_cliente))

            result = cur.fetchone()
            return dict(result) if result else None


@db_operation("criar_tag")
def criar_tag(
    nome: str,
    descricao: Optional[str] = None,
    cor_hex: Optional[str] = None,
    id_cliente: Optional[int] = None
) -> int:
    """
    Cria uma nova tag no banco de dados.

    Args:
        nome: Nome da tag
        descricao: Descrição da tag
        cor_hex: Cor em hexadecimal (ex: #FF5733)
        id_cliente: ID do cliente (usa DEFAULT_CLIENT_ID se não fornecido)

    Returns:
        ID da tag criada
    """
    if id_cliente is None:
        id_cliente = get_default_client_id()

    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO tags (
                    id_cliente,
                    nome,
                    descricao,
                    cor_hex,
                    ativo
                ) VALUES (
                    %s, %s, %s, %s, true
                )
                RETURNING id_tag
            """, (id_cliente, nome, descricao, cor_hex))

            result = cur.fetchone()
            return result['id_tag']


@db_operation("atualizar_tag")
def atualizar_tag(
    id_tag: int,
    nome: Optional[str] = None,
    descricao: Optional[str] = None,
    cor_hex: Optional[str] = None,
    ativo: Optional[bool] = None
) -> bool:
    """
    Atualiza uma tag existente.

    Args:
        id_tag: ID da tag
        nome: Novo nome (opcional)
        descricao: Nova descrição (opcional)
        cor_hex: Nova cor (opcional)
        ativo: Novo status (opcional)

    Returns:
        True se atualizou, False se não encontrou
    """
    # Montar query dinâmica apenas com campos fornecidos
    updates = []
    params = []

    if nome is not None:
        updates.append("nome = %s")
        params.append(nome)

    if descricao is not None:
        updates.append("descricao = %s")
        params.append(descricao)

    if cor_hex is not None:
        updates.append("cor_hex = %s")
        params.append(cor_hex)

    if ativo is not None:
        updates.append("ativo = %s")
        params.append(ativo)

    if not updates:
        return False

    # Adicionar updated_at
    updates.append("atualizado_em = NOW()")
    params.append(id_tag)

    query = f"""
        UPDATE tags
        SET {', '.join(updates)}
        WHERE id_tag = %s
    """

    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, params)
            return cur.rowcount > 0


def excluir_tag(id_tag: int) -> bool:
    """
    Exclui uma tag (soft delete - marca como inativa).

    Args:
        id_tag: ID da tag

    Returns:
        True se excluiu, False se não encontrou
    """
    return atualizar_tag(id_tag, ativo=False)


@db_operation("excluir_tag_permanente")
def excluir_tag_permanente(id_tag: int) -> bool:
    """
    Exclui uma tag permanentemente do banco de dados.
    ATENÇÃO: Esta ação é irreversível!

    Args:
        id_tag: ID da tag

    Returns:
        True se excluiu, False se não encontrou
    """
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            # Primeiro, excluir todas as associações tag_acoes
            cur.execute("DELETE FROM tag_acoes WHERE id_tag = %s", (id_tag,))

            # Depois, excluir a tag
            cur.execute("DELETE FROM tags WHERE id_tag = %s", (id_tag,))
            return cur.rowcount > 0


@db_operation("contar_tags")
def contar_tags(id_cliente: Optional[int] = None, apenas_ativas: bool = True) -> int:
    """
    Conta o número total de tags de um cliente.

    Args:
        id_cliente: ID do cliente (usa DEFAULT_CLIENT_ID se não fornecido)
        apenas_ativas: Se True, conta apenas tags ativas

    Returns:
        Número de tags
    """
    if id_cliente is None:
        id_cliente = get_default_client_id()

    with get_db_connection() as conn:
        with conn.cursor() as cur:
            query = """
                SELECT COUNT(*) as total
                FROM tags
                WHERE id_cliente = %s
            """

            params = [id_cliente]

            if apenas_ativas:
                query += " AND ativo = true"

            cur.execute(query, params)
            result = cur.fetchone()
            return result['total']
