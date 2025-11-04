"""
Repositório para gerenciar associações entre Tags e Ações (tag_acoes).
"""

from database.connection import get_db_connection
from typing import List, Dict, Optional
import json


def listar_tag_acoes(id_tag: Optional[int] = None, apenas_ativas: bool = True) -> List[Dict]:
    """
    Lista todas as associações tag-ação.

    Args:
        id_tag: Filtrar por ID da tag (opcional)
        apenas_ativas: Se True, retorna apenas associações ativas

    Returns:
        Lista de associações como dicionários
    """
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            query = """
                SELECT
                    ta.id_tag_acao,
                    ta.id_tag,
                    t.nome as tag_nome,
                    t.cor_hex as tag_cor,
                    ta.id_acao,
                    a.nome as acao_nome,
                    a.codigo as acao_codigo,
                    a.tipo as acao_tipo,
                    ta.id_prompt,
                    p.nome as prompt_nome,
                    ta.prioridade,
                    ta.condicoes_extras,
                    ta.parametros,
                    ta.ativo,
                    ta.criado_em
                FROM tag_acoes ta
                INNER JOIN tags t ON ta.id_tag = t.id_tag
                INNER JOIN acoes a ON ta.id_acao = a.id_acao
                LEFT JOIN prompts p ON ta.id_prompt = p.id_prompt
                WHERE 1=1
            """

            params = []

            if id_tag is not None:
                query += " AND ta.id_tag = %s"
                params.append(id_tag)

            if apenas_ativas:
                query += " AND ta.ativo = true"

            query += " ORDER BY ta.prioridade ASC, t.nome, a.nome"

            cur.execute(query, params)
            results = cur.fetchall()

            return [dict(row) for row in results]


def buscar_tag_acao_por_id(id_tag_acao: int) -> Optional[Dict]:
    """
    Busca uma associação específica pelo ID.

    Args:
        id_tag_acao: ID da associação

    Returns:
        Dicionário com dados da associação ou None se não encontrada
    """
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT
                    ta.id_tag_acao,
                    ta.id_tag,
                    t.nome as tag_nome,
                    ta.id_acao,
                    a.nome as acao_nome,
                    a.codigo as acao_codigo,
                    ta.id_prompt,
                    p.nome as prompt_nome,
                    ta.prioridade,
                    ta.condicoes_extras,
                    ta.parametros,
                    ta.ativo,
                    ta.criado_em
                FROM tag_acoes ta
                INNER JOIN tags t ON ta.id_tag = t.id_tag
                INNER JOIN acoes a ON ta.id_acao = a.id_acao
                LEFT JOIN prompts p ON ta.id_prompt = p.id_prompt
                WHERE ta.id_tag_acao = %s
            """, (id_tag_acao,))

            result = cur.fetchone()
            return dict(result) if result else None


def criar_tag_acao(
    id_tag: int,
    id_acao: int,
    id_prompt: int,
    prioridade: int = 1,
    condicoes_extras: Optional[Dict] = None,
    parametros: Optional[Dict] = None
) -> int:
    """
    Cria uma nova associação entre tag e ação.

    Args:
        id_tag: ID da tag
        id_acao: ID da ação
        id_prompt: ID do prompt a ser executado
        prioridade: Prioridade de execução (menor = mais prioritário)
        condicoes_extras: Condições extras em JSON
        parametros: Parâmetros adicionais em JSON

    Returns:
        ID da associação criada
    """
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO tag_acoes (
                    id_tag,
                    id_acao,
                    id_prompt,
                    prioridade,
                    condicoes_extras,
                    parametros,
                    ativo
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, true
                )
                RETURNING id_tag_acao
            """, (
                id_tag,
                id_acao,
                id_prompt,
                prioridade,
                json.dumps(condicoes_extras) if condicoes_extras else None,
                json.dumps(parametros) if parametros else None
            ))

            result = cur.fetchone()
            return result['id_tag_acao']


def atualizar_tag_acao(
    id_tag_acao: int,
    prioridade: Optional[int] = None,
    condicoes_extras: Optional[Dict] = None,
    parametros: Optional[Dict] = None,
    ativo: Optional[bool] = None
) -> bool:
    """
    Atualiza uma associação existente.

    Args:
        id_tag_acao: ID da associação
        prioridade: Nova prioridade (opcional)
        condicoes_extras: Novas condições extras (opcional)
        parametros: Novos parâmetros (opcional)
        ativo: Novo status (opcional)

    Returns:
        True se atualizou, False se não encontrou
    """
    updates = []
    params = []

    if prioridade is not None:
        updates.append("prioridade = %s")
        params.append(prioridade)

    if condicoes_extras is not None:
        updates.append("condicoes_extras = %s")
        params.append(json.dumps(condicoes_extras))

    if parametros is not None:
        updates.append("parametros = %s")
        params.append(json.dumps(parametros))

    if ativo is not None:
        updates.append("ativo = %s")
        params.append(ativo)

    if not updates:
        return False

    params.append(id_tag_acao)

    query = f"""
        UPDATE tag_acoes
        SET {', '.join(updates)}
        WHERE id_tag_acao = %s
    """

    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, params)
            return cur.rowcount > 0


def excluir_tag_acao(id_tag_acao: int) -> bool:
    """
    Exclui uma associação (soft delete - marca como inativa).

    Args:
        id_tag_acao: ID da associação

    Returns:
        True se excluiu, False se não encontrou
    """
    return atualizar_tag_acao(id_tag_acao, ativo=False)


def excluir_tag_acao_permanente(id_tag_acao: int) -> bool:
    """
    Exclui uma associação permanentemente do banco de dados.
    ATENÇÃO: Esta ação é irreversível!

    Args:
        id_tag_acao: ID da associação

    Returns:
        True se excluiu, False se não encontrou
    """
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM tag_acoes WHERE id_tag_acao = %s", (id_tag_acao,))
            return cur.rowcount > 0


def listar_acoes_por_tag(id_tag: int) -> List[Dict]:
    """
    Lista todas as ações associadas a uma tag específica.

    Args:
        id_tag: ID da tag

    Returns:
        Lista de ações com detalhes da associação
    """
    return listar_tag_acoes(id_tag=id_tag, apenas_ativas=True)


def contar_tag_acoes(id_tag: Optional[int] = None, apenas_ativas: bool = True) -> int:
    """
    Conta o número total de associações tag-ação.

    Args:
        id_tag: Filtrar por ID da tag (opcional)
        apenas_ativas: Se True, conta apenas associações ativas

    Returns:
        Número de associações
    """
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            query = "SELECT COUNT(*) as total FROM tag_acoes WHERE 1=1"
            params = []

            if id_tag is not None:
                query += " AND id_tag = %s"
                params.append(id_tag)

            if apenas_ativas:
                query += " AND ativo = true"

            cur.execute(query, params)
            result = cur.fetchone()
            return result['total']


def verificar_duplicata(id_tag: int, id_acao: int, id_prompt: int) -> bool:
    """
    Verifica se já existe uma associação ativa entre tag, ação e prompt.

    Args:
        id_tag: ID da tag
        id_acao: ID da ação
        id_prompt: ID do prompt

    Returns:
        True se já existe, False caso contrário
    """
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT COUNT(*) as total
                FROM tag_acoes
                WHERE id_tag = %s AND id_acao = %s AND id_prompt = %s AND ativo = true
            """, (id_tag, id_acao, id_prompt))

            result = cur.fetchone()
            return result['total'] > 0
