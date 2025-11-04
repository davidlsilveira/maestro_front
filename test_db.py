"""
Script de teste de conexão com o banco de dados.
Execute: python test_db.py
"""

import sys
import io

# Configurar encoding para UTF-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from database.connection import test_connection, get_db_connection
from repositories.epicos_repository import contar_epicos, listar_epicos
from repositories.analises_repository import contar_analises
from repositories.prompts_repository import contar_prompts


def main():
    print("=" * 60)
    print("TESTE DE CONEXAO - MAESTRO FRONT")
    print("=" * 60)

    # 1. Teste de conexão básica
    print("\n1. Testando conexao com PostgreSQL...")
    try:
        if test_connection():
            print("   [OK] Conexao estabelecida com sucesso!")
        else:
            print("   [ERRO] Falha na conexao")
            return
    except Exception as e:
        print(f"   [ERRO] {e}")
        return

    # 2. Teste de contagem de epicos
    print("\n2. Testando contagem de epicos...")
    try:
        total = contar_epicos()
        print(f"   [OK] Total de epicos cadastrados: {total}")
    except Exception as e:
        print(f"   [ERRO] ao contar epicos: {e}")

    # 3. Teste de listagem de epicos
    print("\n3. Testando listagem de epicos (primeiros 5)...")
    try:
        epicos = listar_epicos()
        if epicos:
            for epico in epicos[:5]:
                print(f"   - ID {epico['id_epico']}: {epico['titulo']}")
            if len(epicos) > 5:
                print(f"   ... e mais {len(epicos) - 5} epicos")
        else:
            print("   [AVISO] Nenhum epico encontrado")
    except Exception as e:
        print(f"   [ERRO] ao listar epicos: {e}")

    # 4. Teste de contagem de analises
    print("\n4. Testando contagem de analises...")
    try:
        total = contar_analises()
        print(f"   [OK] Total de analises executadas: {total}")
    except Exception as e:
        print(f"   [ERRO] ao contar analises: {e}")

    # 5. Teste de contagem de prompts
    print("\n5. Testando contagem de prompts...")
    try:
        total = contar_prompts()
        print(f"   [OK] Total de prompts ativos: {total}")
    except Exception as e:
        print(f"   [ERRO] ao contar prompts: {e}")

    # 6. Teste de consulta direta
    print("\n6. Testando consulta direta ao banco...")
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT version();")
                version = cur.fetchone()
                print(f"   [OK] PostgreSQL Version: {version['version'][:50]}...")
    except Exception as e:
        print(f"   [ERRO] na consulta: {e}")

    print("\n" + "=" * 60)
    print("TESTE CONCLUIDO!")
    print("=" * 60)


if __name__ == "__main__":
    main()
