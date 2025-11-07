"""
Módulo de conexão com o banco de dados PostgreSQL.
Compatível com a estrutura do projeto Maestro.
"""

import os
from contextlib import contextmanager

import psycopg2
from dotenv import load_dotenv
from psycopg2.extras import RealDictCursor

from observability.metrics import db_connection_error, db_connection_opened

# Carrega variáveis de ambiente
load_dotenv()


def get_database_url():
    """Retorna a URL de conexão com o banco de dados."""
    if url := os.getenv("DATABASE_URL"):
        return url

    user = os.getenv("POSTGRES_USER", "postgres")
    password = os.getenv("POSTGRES_PASSWORD", "")
    host = os.getenv("POSTGRES_HOST", "localhost")
    port = os.getenv("POSTGRES_PORT", "5432")
    database = os.getenv("POSTGRES_DB", "postgres")

    credentials = f"{user}:{password}" if password else user
    return f"postgresql://{credentials}@{host}:{port}/{database}"


@contextmanager
def get_db_connection():
    """
    Context manager para conexão com o banco de dados.

    Uso:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM epicos")
                results = cur.fetchall()
    """
    conn = None
    try:
        conn = psycopg2.connect(
            get_database_url(),
            cursor_factory=RealDictCursor  # Retorna resultados como dicionários
        )
        db_connection_opened()
        yield conn
        conn.commit()
    except Exception as e:
        if conn is None:
            db_connection_error()
        else:
            conn.rollback()
        raise e
    finally:
        if conn:
            conn.close()


def test_connection():
    """Testa a conexão com o banco de dados."""
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1 as test")
                result = cur.fetchone()
                return result['test'] == 1
    except Exception as e:
        print(f"Erro ao conectar ao banco de dados: {e}")
        return False
