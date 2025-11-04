import os
import time
from contextlib import contextmanager
from functools import wraps
from threading import Lock
from typing import Callable, Optional

from prometheus_client import Counter, Gauge, Histogram, start_http_server

_METRICS_STARTED = False
_METRICS_LOCK = Lock()

PAGE_VIEWS = Counter(
    "maestro_streamlit_page_views_total",
    "Total de visualizações de páginas no Maestro Front",
    ["page"],
)

STREAMLIT_EVENTS = Counter(
    "maestro_streamlit_user_events_total",
    "Eventos disparados por interação do usuário",
    ["event"],
)

RENDER_DURATION = Histogram(
    "maestro_streamlit_render_duration_seconds",
    "Tempo de renderização de seções do Streamlit",
    ["section"],
    buckets=(0.05, 0.1, 0.25, 0.5, 1, 2, 4, 8),
)

DB_OPERATIONS = Counter(
    "maestro_db_operations_total",
    "Operações de banco de dados bem-sucedidas",
    ["operation"],
)

DB_ERRORS = Counter(
    "maestro_db_operation_errors_total",
    "Erros ao executar operações no banco de dados",
    ["operation", "error_type"],
)

DB_DURATION = Histogram(
    "maestro_db_operation_duration_seconds",
    "Tempo de execução das operações de banco de dados",
    ["operation"],
    buckets=(0.01, 0.05, 0.1, 0.25, 0.5, 1, 2, 5),
)

DB_CONNECTIONS = Counter(
    "maestro_db_connections_total",
    "Número total de conexões estabelecidas com o banco",
)

DB_CONNECTION_ERRORS = Counter(
    "maestro_db_connection_errors_total",
    "Erros ao abrir conexão com o banco de dados",
)

STREAMLIT_LAST_RUN = Gauge(
    "maestro_streamlit_last_success_timestamp",
    "Timestamp da última renderização concluída com sucesso",
)


def init_metrics() -> None:
    """Inicializa o servidor de métricas Prometheus (idempotente)."""
    global _METRICS_STARTED
    with _METRICS_LOCK:
        if _METRICS_STARTED:
            return

        port = int(os.getenv("PROMETHEUS_METRICS_PORT", "9464"))
        addr = os.getenv("PROMETHEUS_METRICS_ADDR", "0.0.0.0")
        start_http_server(port, addr=addr)
        _METRICS_STARTED = True


def track_page_view(page: str) -> None:
    """Incrementa contador de visualização da página."""
    PAGE_VIEWS.labels(page=page).inc()


def track_streamlit_event(event: str) -> None:
    """Registra um evento do usuário (cliques, downloads, etc.)."""
    STREAMLIT_EVENTS.labels(event=event).inc()


@contextmanager
def observe_render(section: str):
    """Context manager para medir tempo de renderização e sinalizar sucesso/erro."""
    start = time.perf_counter()
    try:
        yield
    except Exception as exc:
        RENDER_DURATION.labels(section=section).observe(time.perf_counter() - start)
        raise exc
    else:
        duration = time.perf_counter() - start
        RENDER_DURATION.labels(section=section).observe(duration)
        STREAMLIT_LAST_RUN.set_to_current_time()


def db_operation(name: Optional[str] = None) -> Callable:
    """Decorador para medir operações de banco de dados."""

    def decorator(func: Callable) -> Callable:
        operation_name = name or func.__name__

        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.perf_counter()
            try:
                result = func(*args, **kwargs)
                DB_OPERATIONS.labels(operation=operation_name).inc()
                return result
            except Exception as exc:
                DB_ERRORS.labels(
                    operation=operation_name,
                    error_type=exc.__class__.__name__,
                ).inc()
                raise
            finally:
                duration = time.perf_counter() - start_time
                DB_DURATION.labels(operation=operation_name).observe(duration)

        return wrapper

    return decorator


def db_connection_opened() -> None:
    """Registra uma conexão de banco aberta com sucesso."""
    DB_CONNECTIONS.inc()


def db_connection_error() -> None:
    """Registra um erro ao abrir conexão com o banco."""
    DB_CONNECTION_ERRORS.inc()
