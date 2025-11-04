"""
Script para testar e verificar os relacionamentos entre tags, ações e prompts.
"""

import sys
import io

# Configurar encoding para UTF-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from database.connection import get_db_connection


def main():
    print("=" * 80)
    print("TESTE DE RELACIONAMENTOS TAG-AÇÃO-PROMPT")
    print("=" * 80)

    with get_db_connection() as conn:
        with conn.cursor() as cur:
            # 1. Listar todas as tags
            print("\n1. TAGS CADASTRADAS:")
            print("-" * 80)
            cur.execute("""
                SELECT id_tag, nome, descricao, cor_hex, ativo
                FROM tags
                ORDER BY id_tag
            """)
            tags = cur.fetchall()

            for tag in tags:
                status = "✅ Ativa" if tag['ativo'] else "❌ Inativa"
                print(f"   Tag {tag['id_tag']}: {tag['nome']} - {status}")
                if tag['descricao']:
                    print(f"      Descrição: {tag['descricao']}")

            # 2. Listar todas as ações
            print("\n2. AÇÕES CADASTRADAS:")
            print("-" * 80)
            cur.execute("""
                SELECT id_acao, codigo, nome, tipo, ativo
                FROM acoes
                ORDER BY id_acao
            """)
            acoes = cur.fetchall()

            for acao in acoes:
                status = "✅ Ativa" if acao['ativo'] else "❌ Inativa"
                print(f"   Ação {acao['id_acao']}: {acao['nome']} ({acao['codigo']}) - {acao['tipo']} - {status}")

            # 3. Listar todos os prompts
            print("\n3. PROMPTS CADASTRADOS:")
            print("-" * 80)
            cur.execute("""
                SELECT id_prompt, nome, contexto, versao, ativo
                FROM prompts
                ORDER BY id_prompt
            """)
            prompts = cur.fetchall()

            for prompt in prompts:
                status = "✅ Ativo" if prompt['ativo'] else "❌ Inativo"
                print(f"   Prompt {prompt['id_prompt']}: {prompt['nome']} (v{prompt['versao']}) - Contexto: {prompt['contexto']} - {status}")

            # 4. Listar todas as associações tag_acoes
            print("\n4. ASSOCIAÇÕES TAG → AÇÃO → PROMPT:")
            print("-" * 80)
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
                    ta.ativo,
                    ta.condicoes_extras,
                    ta.parametros
                FROM tag_acoes ta
                INNER JOIN tags t ON ta.id_tag = t.id_tag
                INNER JOIN acoes a ON ta.id_acao = a.id_acao
                LEFT JOIN prompts p ON ta.id_prompt = p.id_prompt
                ORDER BY ta.id_tag, ta.prioridade
            """)
            associacoes = cur.fetchall()

            if not associacoes:
                print("   ⚠️ Nenhuma associação encontrada!")
            else:
                for assoc in associacoes:
                    status = "✅ Ativa" if assoc['ativo'] else "❌ Inativa"
                    print(f"\n   ID {assoc['id_tag_acao']} - {status}")
                    print(f"      Tag {assoc['id_tag']}: {assoc['tag_nome']}")
                    print(f"      → Ação {assoc['id_acao']}: {assoc['acao_nome']} ({assoc['acao_codigo']})")
                    print(f"      → Prompt {assoc['id_prompt']}: {assoc['prompt_nome']}")
                    print(f"      Prioridade: {assoc['prioridade']}")
                    if assoc['condicoes_extras']:
                        print(f"      Condições: {assoc['condicoes_extras']}")
                    if assoc['parametros']:
                        print(f"      Parâmetros: {assoc['parametros']}")

            # 5. Verificar especificamente a tag "Maestro Revisar"
            print("\n5. VERIFICAÇÃO ESPECÍFICA: Tag 'Maestro Revisar':")
            print("-" * 80)
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
                    p.contexto as prompt_contexto,
                    ta.prioridade,
                    ta.ativo
                FROM tag_acoes ta
                INNER JOIN tags t ON ta.id_tag = t.id_tag
                INNER JOIN acoes a ON ta.id_acao = a.id_acao
                LEFT JOIN prompts p ON ta.id_prompt = p.id_prompt
                WHERE t.nome = 'Maestro Revisar'
                ORDER BY ta.prioridade
            """)
            maestro_revisar = cur.fetchall()

            if not maestro_revisar:
                print("   ⚠️ Nenhuma associação encontrada para 'Maestro Revisar'!")
            else:
                for assoc in maestro_revisar:
                    status = "✅ Ativa" if assoc['ativo'] else "❌ Inativa"
                    print(f"\n   Associação ID {assoc['id_tag_acao']} - {status}")
                    print(f"      Tag ID {assoc['id_tag']}: {assoc['tag_nome']}")
                    print(f"      Ação ID {assoc['id_acao']}: {assoc['acao_nome']} ({assoc['acao_codigo']})")
                    print(f"      Prompt ID {assoc['id_prompt']}: {assoc['prompt_nome']} (contexto: {assoc['prompt_contexto']})")
                    print(f"      Prioridade: {assoc['prioridade']}")

    print("\n" + "=" * 80)
    print("TESTE CONCLUÍDO!")
    print("=" * 80)


if __name__ == "__main__":
    main()
