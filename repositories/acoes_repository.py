"""
Repositório para gerenciar Ações no banco de dados.
"""

from database.connection import get_db_connection
from typing import List, Dict, Optional


def listar_acoes(apenas_ativas: bool = True) -> List[Dict]:
    """
    Lista todas as ações disponíveis no sistema.

    Args:
        apenas_ativas: Se True, retorna apenas ações ativas

    Returns:
        Lista de ações como dicionários
    """
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            query = """
                SELECT
                    id_acao,
                    codigo,
                    nome,
                    descricao,
                    tipo,
                    ativo,
                    criado_em
                FROM acoes
            """

            if apenas_ativas:
                query += " WHERE ativo = true"

            query += " ORDER BY tipo, nome"

            cur.execute(query)
            results = cur.fetchall()

            # Contar usos de cada ação
            acoes = []
            for row in results:
                # Contar quantas vezes a ação está associada a tags
                cur.execute("""
                    SELECT COUNT(*) as total
                    FROM tag_acoes
                    WHERE id_acao = %s AND ativo = true
                """, (row['id_acao'],))

                uso_result = cur.fetchone()
                usos = uso_result['total'] if uso_result else 0

                acao = {
                    "id_acao": row['id_acao'],
                    "codigo": row['codigo'],
                    "nome": row['nome'],
                    "descricao": row['descricao'],
                    "tipo": row['tipo'],
                    "ativo": row['ativo'],
                    "criado_em": row['criado_em'],
                    "usos": usos
                }
                acoes.append(acao)

            return acoes


def buscar_acao_por_id(id_acao: int) -> Optional[Dict]:
    """
    Busca uma ação específica pelo ID.

    Args:
        id_acao: ID da ação

    Returns:
        Dicionário com dados da ação ou None se não encontrada
    """
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT
                    id_acao,
                    codigo,
                    nome,
                    descricao,
                    tipo,
                    ativo,
                    criado_em
                FROM acoes
                WHERE id_acao = %s
            """, (id_acao,))

            result = cur.fetchone()
            return dict(result) if result else None


def buscar_acao_por_codigo(codigo: str) -> Optional[Dict]:
    """
    Busca uma ação pelo código.

    Args:
        codigo: Código da ação

    Returns:
        Dicionário com dados da ação ou None se não encontrada
    """
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT
                    id_acao,
                    codigo,
                    nome,
                    descricao,
                    tipo,
                    ativo,
                    criado_em
                FROM acoes
                WHERE codigo = %s
            """, (codigo,))

            result = cur.fetchone()
            return dict(result) if result else None


def listar_acoes_por_tipo(tipo: str, apenas_ativas: bool = True) -> List[Dict]:
    """
    Lista ações de um tipo específico.

    Args:
        tipo: Tipo da ação (ai_analysis, workflow, integration, notification)
        apenas_ativas: Se True, retorna apenas ações ativas

    Returns:
        Lista de ações do tipo especificado
    """
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            query = """
                SELECT
                    id_acao,
                    codigo,
                    nome,
                    descricao,
                    tipo,
                    ativo,
                    criado_em
                FROM acoes
                WHERE tipo = %s
            """

            params = [tipo]

            if apenas_ativas:
                query += " AND ativo = true"

            query += " ORDER BY nome"

            cur.execute(query, params)
            results = cur.fetchall()

            return [dict(row) for row in results]


def listar_tipos_acoes() -> List[str]:
    """
    Lista todos os tipos de ações disponíveis.

    Returns:
        Lista de tipos únicos
    """
    return ['ai_analysis', 'workflow', 'integration', 'notification']


def contar_acoes(apenas_ativas: bool = True) -> int:
    """
    Conta o número total de ações.

    Args:
        apenas_ativas: Se True, conta apenas ações ativas

    Returns:
        Número de ações
    """
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            query = "SELECT COUNT(*) as total FROM acoes"

            if apenas_ativas:
                query += " WHERE ativo = true"

            cur.execute(query)
            result = cur.fetchone()
            return result['total']
