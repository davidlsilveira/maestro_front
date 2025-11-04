"""
Repositório para gerenciar Prompts no banco de dados.
"""

import os
from datetime import datetime
from typing import Dict, List, Optional

from database.connection import get_db_connection
from observability.metrics import db_operation


def get_default_client_id() -> int:
    """Retorna o ID do cliente padrão configurado no .env."""
    return int(os.getenv("DEFAULT_CLIENT_ID", "1"))


@db_operation("listar_prompts")
def listar_prompts(id_cliente: Optional[int] = None, apenas_ativos: bool = True) -> List[Dict]:
    """
    Lista os prompts cadastrados de um cliente.

    Args:
        id_cliente: ID do cliente (usa DEFAULT_CLIENT_ID se não fornecido)
        apenas_ativos: Se True, retorna apenas prompts ativos

    Returns:
        Lista de prompts como dicionários
    """
    if id_cliente is None:
        id_cliente = get_default_client_id()

    with get_db_connection() as conn:
        with conn.cursor() as cur:
            query = """
                SELECT
                    id_prompt,
                    nome,
                    contexto as tag,
                    versao,
                    ativo,
                    template_prompt,
                    variaveis_esperadas,
                    temperatura,
                    max_tokens,
                    metadata,
                    criado_em,
                    atualizado_em as ultima_atualizacao
                FROM prompts
                WHERE id_cliente = %s
            """

            params = [id_cliente]

            if apenas_ativos:
                query += " AND ativo = true"

            query += " ORDER BY contexto, nome"

            cur.execute(query, params)
            results = cur.fetchall()

            # Calcular "em_uso" (número de vezes que o prompt foi executado)
            prompts = []
            for row in results:
                # Buscar contagem de uso
                cur.execute("""
                    SELECT COUNT(*) as total
                    FROM prompt_execucoes
                    WHERE id_prompt = %s
                """, (row['id_prompt'],))

                uso_result = cur.fetchone()
                em_uso = uso_result['total'] if uso_result else 0

                prompt = {
                    "id_prompt": row['id_prompt'],
                    "nome": row['nome'],
                    "tag": row['tag'],
                    "versao": row['versao'],
                    "ativo": row['ativo'],
                    "template_prompt": row['template_prompt'],
                    "variaveis_esperadas": row['variaveis_esperadas'],
                    "temperatura": float(row['temperatura']) if row['temperatura'] else 0.7,
                    "max_tokens": row['max_tokens'],
                    "metadata": row['metadata'],
                    "ultima_atualizacao": row['ultima_atualizacao'].strftime("%Y-%m-%d %H:%M") if isinstance(row['ultima_atualizacao'], datetime) else str(row['ultima_atualizacao']),
                    "em_uso": em_uso
                }
                prompts.append(prompt)

            return prompts


@db_operation("buscar_prompt_por_id")
def buscar_prompt_por_id(id_prompt: int) -> Optional[Dict]:
    """
    Busca um prompt específico pelo ID.

    Args:
        id_prompt: ID do prompt

    Returns:
        Dicionário com dados do prompt ou None se não encontrado
    """
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT
                    id_prompt,
                    id_cliente,
                    nome,
                    contexto as tag,
                    versao,
                    ativo,
                    template_prompt,
                    variaveis_esperadas,
                    temperatura,
                    max_tokens,
                    metadata,
                    criado_em,
                    atualizado_em
                FROM prompts
                WHERE id_prompt = %s
            """, (id_prompt,))

            result = cur.fetchone()
            return dict(result) if result else None


@db_operation("buscar_prompt_por_contexto")
def buscar_prompt_por_contexto(
    contexto: str,
    id_cliente: Optional[int] = None,
    apenas_ativos: bool = True
) -> Optional[Dict]:
    """
    Busca o prompt ativo mais recente de um contexto específico.

    Args:
        contexto: Contexto do prompt (ex: "pre_analise", "wbs_geracao")
        id_cliente: ID do cliente (usa DEFAULT_CLIENT_ID se não fornecido)
        apenas_ativos: Se True, busca apenas prompts ativos

    Returns:
        Dicionário com dados do prompt ou None se não encontrado
    """
    if id_cliente is None:
        id_cliente = get_default_client_id()

    with get_db_connection() as conn:
        with conn.cursor() as cur:
            query = """
                SELECT
                    id_prompt,
                    nome,
                    contexto as tag,
                    versao,
                    template_prompt,
                    variaveis_esperadas,
                    temperatura,
                    max_tokens,
                    metadata
                FROM prompts
                WHERE id_cliente = %s
                  AND contexto = %s
            """

            params = [id_cliente, contexto]

            if apenas_ativos:
                query += " AND ativo = true"

            query += " ORDER BY atualizado_em DESC LIMIT 1"

            cur.execute(query, params)
            result = cur.fetchone()

            return dict(result) if result else None


@db_operation("contar_prompts")
def contar_prompts(id_cliente: Optional[int] = None, apenas_ativos: bool = True) -> int:
    """
    Conta o número de prompts cadastrados de um cliente.

    Args:
        id_cliente: ID do cliente (usa DEFAULT_CLIENT_ID se não fornecido)
        apenas_ativos: Se True, conta apenas prompts ativos

    Returns:
        Número de prompts
    """
    if id_cliente is None:
        id_cliente = get_default_client_id()

    with get_db_connection() as conn:
        with conn.cursor() as cur:
            query = """
                SELECT COUNT(*) as total
                FROM prompts
                WHERE id_cliente = %s
            """

            params = [id_cliente]

            if apenas_ativos:
                query += " AND ativo = true"

            cur.execute(query, params)
            result = cur.fetchone()
            return result['total']


@db_operation("listar_contextos_prompts")
def listar_contextos_disponiveis() -> List[str]:
    """
    Lista os contextos de prompts disponíveis no sistema.

    Returns:
        Lista de contextos únicos
    """
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT DISTINCT contexto
                FROM prompts
                WHERE ativo = true
                ORDER BY contexto
            """)

            results = cur.fetchall()
            return [row['contexto'] for row in results]


@db_operation("criar_prompt")
def criar_prompt(
    nome: str,
    contexto: str,
    template_prompt: str,
    versao: str = "1.0.0",
    temperatura: float = 0.7,
    max_tokens: int = 4000,
    variaveis_esperadas: Optional[Dict] = None,
    metadata: Optional[Dict] = None,
    id_cliente: Optional[int] = None
) -> int:
    """
    Cria um novo prompt no banco de dados.

    Args:
        nome: Nome do prompt
        contexto: Contexto de uso (ex: "pre_analise", "wbs_geracao")
        template_prompt: Template do prompt em texto
        versao: Versão do prompt (padrão: "1.0.0")
        temperatura: Temperatura para geração (0.0 a 1.0)
        max_tokens: Número máximo de tokens
        variaveis_esperadas: JSON com variáveis esperadas
        metadata: Metadados adicionais em JSON
        id_cliente: ID do cliente (usa DEFAULT_CLIENT_ID se não fornecido)

    Returns:
        ID do prompt criado
    """
    if id_cliente is None:
        id_cliente = get_default_client_id()

    import json

    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO prompts (
                    id_cliente,
                    nome,
                    contexto,
                    versao,
                    template_prompt,
                    variaveis_esperadas,
                    temperatura,
                    max_tokens,
                    metadata,
                    ativo
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, true
                )
                RETURNING id_prompt
            """, (
                id_cliente,
                nome,
                contexto,
                versao,
                template_prompt,
                json.dumps(variaveis_esperadas) if variaveis_esperadas else None,
                temperatura,
                max_tokens,
                json.dumps(metadata) if metadata else None
            ))

            result = cur.fetchone()
            return result['id_prompt']


@db_operation("atualizar_prompt")
def atualizar_prompt(
    id_prompt: int,
    nome: Optional[str] = None,
    contexto: Optional[str] = None,
    template_prompt: Optional[str] = None,
    versao: Optional[str] = None,
    temperatura: Optional[float] = None,
    max_tokens: Optional[int] = None,
    variaveis_esperadas: Optional[Dict] = None,
    metadata: Optional[Dict] = None,
    ativo: Optional[bool] = None
) -> bool:
    """
    Atualiza um prompt existente.

    Args:
        id_prompt: ID do prompt
        nome: Novo nome (opcional)
        contexto: Novo contexto (opcional)
        template_prompt: Novo template (opcional)
        versao: Nova versão (opcional)
        temperatura: Nova temperatura (opcional)
        max_tokens: Novo max_tokens (opcional)
        variaveis_esperadas: Novas variáveis esperadas (opcional)
        metadata: Novos metadados (opcional)
        ativo: Novo status (opcional)

    Returns:
        True se atualizou, False se não encontrou
    """
    import json

    updates = []
    params = []

    if nome is not None:
        updates.append("nome = %s")
        params.append(nome)

    if contexto is not None:
        updates.append("contexto = %s")
        params.append(contexto)

    if template_prompt is not None:
        updates.append("template_prompt = %s")
        params.append(template_prompt)

    if versao is not None:
        updates.append("versao = %s")
        params.append(versao)

    if temperatura is not None:
        updates.append("temperatura = %s")
        params.append(temperatura)

    if max_tokens is not None:
        updates.append("max_tokens = %s")
        params.append(max_tokens)

    if variaveis_esperadas is not None:
        updates.append("variaveis_esperadas = %s")
        params.append(json.dumps(variaveis_esperadas))

    if metadata is not None:
        updates.append("metadata = %s")
        params.append(json.dumps(metadata))

    if ativo is not None:
        updates.append("ativo = %s")
        params.append(ativo)

    if not updates:
        return False

    # Adicionar atualizado_em
    updates.append("atualizado_em = NOW()")
    params.append(id_prompt)

    query = f"""
        UPDATE prompts
        SET {', '.join(updates)}
        WHERE id_prompt = %s
    """

    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, params)
            return cur.rowcount > 0


def excluir_prompt(id_prompt: int) -> bool:
    """
    Exclui um prompt (soft delete - marca como inativo).

    Args:
        id_prompt: ID do prompt

    Returns:
        True se excluiu, False se não encontrou
    """
    return atualizar_prompt(id_prompt, ativo=False)


@db_operation("excluir_prompt_permanente")
def excluir_prompt_permanente(id_prompt: int) -> bool:
    """
    Exclui um prompt permanentemente do banco de dados.
    ATENÇÃO: Esta ação é irreversível e pode afetar associações tag_acoes!

    Args:
        id_prompt: ID do prompt

    Returns:
        True se excluiu, False se não encontrou
    """
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            # Verificar se há associações tag_acoes usando este prompt
            cur.execute("""
                SELECT COUNT(*) as total
                FROM tag_acoes
                WHERE id_prompt = %s
            """, (id_prompt,))

            result = cur.fetchone()
            if result['total'] > 0:
                # Não permitir exclusão se houver associações
                return False

            # Excluir o prompt
            cur.execute("DELETE FROM prompts WHERE id_prompt = %s", (id_prompt,))
            return cur.rowcount > 0
