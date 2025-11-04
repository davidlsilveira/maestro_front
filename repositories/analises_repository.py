"""
Repositório para gerenciar Análises (prompt_execucoes) no banco de dados.
"""

import os
from datetime import datetime
from typing import Dict, List, Optional

from database.connection import get_db_connection
from observability.metrics import db_operation


def get_default_client_id() -> int:
    """Retorna o ID do cliente padrão configurado no .env."""
    return int(os.getenv("DEFAULT_CLIENT_ID", "1"))


@db_operation("listar_analises")
def listar_analises(id_cliente: Optional[int] = None, limite: int = 100) -> List[Dict]:
    """
    Lista as análises (execuções de prompts) de um cliente.

    Args:
        id_cliente: ID do cliente (usa DEFAULT_CLIENT_ID se não fornecido)
        limite: Número máximo de resultados

    Returns:
        Lista de análises como dicionários
    """
    if id_cliente is None:
        id_cliente = get_default_client_id()

    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT
                    pe.id_execucao,
                    e.titulo as epico,
                    e.id_epico,
                    p.nome as prompt_nome,
                    p.contexto as prompt_contexto,
                    pe.executado_em as data,
                    pe.resposta_gpt as resultado,
                    pe.status,
                    pe.tokens_consumidos,
                    pe.custo_estimado,
                    pe.tempo_execucao_ms,
                    'gpt-4o-mini' as modelo
                FROM prompt_execucoes pe
                INNER JOIN epicos e ON pe.id_epico = e.id_epico
                INNER JOIN prompts p ON pe.id_prompt = p.id_prompt
                WHERE e.id_cliente = %s
                  AND pe.status = 'sucesso'
                  AND pe.resposta_gpt IS NOT NULL
                ORDER BY pe.executado_em DESC
                LIMIT %s
            """, (id_cliente, limite))

            results = cur.fetchall()

            # Formatar os resultados para compatibilidade com o mock
            analises = []
            for row in results:
                analise = {
                    "id_execucao": row['id_execucao'],
                    "epico": row['epico'],
                    "id_epico": row['id_epico'],
                    "data": row['data'].strftime("%Y-%m-%d %H:%M") if isinstance(row['data'], datetime) else str(row['data']),
                    "modelo": row['modelo'],
                    "resultado": row['resultado'] or "Análise em processamento...",
                    "prompt_nome": row['prompt_nome'],
                    "prompt_contexto": row['prompt_contexto'],
                    "status": row['status'],
                    "tokens_consumidos": row['tokens_consumidos'],
                    "custo_estimado": float(row['custo_estimado']) if row['custo_estimado'] else 0.0,
                    "tempo_execucao_ms": row['tempo_execucao_ms'],
                }
                analises.append(analise)

            return analises


@db_operation("buscar_analises_por_epico")
def buscar_analises_por_epico(id_epico: int) -> List[Dict]:
    """
    Busca todas as análises de um épico específico.

    Args:
        id_epico: ID do épico

    Returns:
        Lista de análises do épico
    """
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT
                    pe.id_execucao,
                    p.nome as prompt_nome,
                    p.contexto as prompt_contexto,
                    pe.executado_em as data,
                    pe.resposta_gpt as resultado,
                    pe.status,
                    pe.tokens_consumidos,
                    pe.custo_estimado,
                    pe.tempo_execucao_ms,
                    'gpt-4o-mini' as modelo
                FROM prompt_execucoes pe
                INNER JOIN prompts p ON pe.id_prompt = p.id_prompt
                WHERE pe.id_epico = %s
                ORDER BY pe.executado_em DESC
            """, (id_epico,))

            results = cur.fetchall()

            # Formatar os resultados
            analises = []
            for row in results:
                analise = {
                    "id_execucao": row['id_execucao'],
                    "data": row['data'].strftime("%Y-%m-%d %H:%M") if isinstance(row['data'], datetime) else str(row['data']),
                    "modelo": row['modelo'],
                    "resultado": row['resultado'] or "Análise em processamento...",
                    "prompt_nome": row['prompt_nome'],
                    "prompt_contexto": row['prompt_contexto'],
                    "status": row['status'],
                    "tokens_consumidos": row['tokens_consumidos'],
                    "custo_estimado": float(row['custo_estimado']) if row['custo_estimado'] else 0.0,
                    "tempo_execucao_ms": row['tempo_execucao_ms'],
                }
                analises.append(analise)

            return analises


@db_operation("buscar_ultima_analise_epico")
def buscar_ultima_analise_epico(id_epico: int) -> Optional[Dict]:
    """
    Busca a última análise bem-sucedida de um épico.

    Args:
        id_epico: ID do épico

    Returns:
        Dicionário com a análise ou None se não encontrada
    """
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT
                    pe.id_execucao,
                    p.nome as prompt_nome,
                    p.contexto as prompt_contexto,
                    pe.executado_em as data,
                    pe.resposta_gpt as resultado,
                    pe.status,
                    pe.tokens_consumidos,
                    pe.custo_estimado,
                    pe.tempo_execucao_ms,
                    'gpt-4o-mini' as modelo
                FROM prompt_execucoes pe
                INNER JOIN prompts p ON pe.id_prompt = p.id_prompt
                WHERE pe.id_epico = %s
                  AND pe.status = 'sucesso'
                  AND pe.resposta_gpt IS NOT NULL
                ORDER BY pe.executado_em DESC
                LIMIT 1
            """, (id_epico,))

            result = cur.fetchone()

            if not result:
                return None

            return {
                "id_execucao": result['id_execucao'],
                "data": result['data'].strftime("%Y-%m-%d %H:%M") if isinstance(result['data'], datetime) else str(result['data']),
                "modelo": result['modelo'],
                "resultado": result['resultado'],
                "prompt_nome": result['prompt_nome'],
                "prompt_contexto": result['prompt_contexto'],
                "status": result['status'],
                "tokens_consumidos": result['tokens_consumidos'],
                "custo_estimado": float(result['custo_estimado']) if result['custo_estimado'] else 0.0,
                "tempo_execucao_ms": result['tempo_execucao_ms'],
            }


@db_operation("contar_analises")
def contar_analises(id_cliente: Optional[int] = None) -> int:
    """
    Conta o número total de análises executadas de um cliente.

    Args:
        id_cliente: ID do cliente (usa DEFAULT_CLIENT_ID se não fornecido)

    Returns:
        Número de análises
    """
    if id_cliente is None:
        id_cliente = get_default_client_id()

    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT COUNT(*) as total
                FROM prompt_execucoes pe
                INNER JOIN epicos e ON pe.id_epico = e.id_epico
                WHERE e.id_cliente = %s
                  AND pe.status = 'sucesso'
            """, (id_cliente,))

            result = cur.fetchone()
            return result['total']
