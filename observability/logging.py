"""
Logging estruturado para Maestro Front (Streamlit)

Integração com Loki via handler JSON para coleta centralizada de logs.
"""

import json
import logging
import os
import sys
from datetime import datetime
from typing import Any, Dict, Optional


class JSONFormatter(logging.Formatter):
    """Formatter que produz logs em formato JSON estruturado"""

    def format(self, record: logging.LogRecord) -> str:
        """Formata o log record como JSON"""
        log_data: Dict[str, Any] = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        # Adiciona labels de serviço
        log_data["service"] = "streamlit"
        log_data["component"] = "backoffice"
        log_data["environment"] = os.getenv("ENVIRONMENT", "production")

        # Adiciona contexto adicional se disponível
        if hasattr(record, "page"):
            log_data["page"] = record.page

        if hasattr(record, "user"):
            log_data["user"] = record.user

        if hasattr(record, "operation"):
            log_data["operation"] = record.operation

        if hasattr(record, "tenant_id"):
            log_data["tenant_id"] = record.tenant_id

        if hasattr(record, "trace_id"):
            log_data["trace_id"] = record.trace_id

        if hasattr(record, "span_id"):
            log_data["span_id"] = record.span_id

        # Adiciona informações de exceção se houver
        if record.exc_info:
            log_data["exception"] = {
                "type": record.exc_info[0].__name__ if record.exc_info[0] else None,
                "message": str(record.exc_info[1]) if record.exc_info[1] else None,
                "traceback": self.formatException(record.exc_info),
            }

        # Adiciona campos extras
        if hasattr(record, "extra"):
            log_data.update(record.extra)

        return json.dumps(log_data, default=str)


def setup_logging(
    level: Optional[str] = None,
    log_format: Optional[str] = None,
) -> logging.Logger:
    """
    Configura logging estruturado para o Streamlit

    Args:
        level: Nível de log (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_format: Formato de log ('json' ou 'text')

    Returns:
        Logger configurado
    """
    # Configurações padrão
    log_level = level or os.getenv("LOG_LEVEL", "INFO")
    format_type = log_format or os.getenv("LOG_FORMAT", "json")

    # Remove handlers existentes
    root_logger = logging.getLogger()
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # Cria handler para stdout
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(getattr(logging, log_level.upper()))

    # Define formatter baseado no tipo
    if format_type == "json":
        formatter = JSONFormatter()
    else:
        formatter = logging.Formatter(
            fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

    handler.setFormatter(formatter)

    # Configura root logger
    root_logger.addHandler(handler)
    root_logger.setLevel(getattr(logging, log_level.upper()))

    # Retorna logger específico para maestro_front
    logger = logging.getLogger("maestro_front")
    logger.setLevel(getattr(logging, log_level.upper()))

    return logger


def get_logger(name: str) -> logging.Logger:
    """
    Obtém logger com nome específico

    Args:
        name: Nome do logger (geralmente __name__)

    Returns:
        Logger configurado
    """
    return logging.getLogger(name)


class LoggerAdapter(logging.LoggerAdapter):
    """Adapter que adiciona contexto aos logs"""

    def process(self, msg: str, kwargs: Dict[str, Any]) -> tuple:
        """Adiciona contexto extra aos logs"""
        extra = kwargs.get("extra", {})

        # Adiciona contexto do adapter
        if self.extra:
            extra.update(self.extra)

        kwargs["extra"] = extra
        return msg, kwargs


def get_contextual_logger(
    name: str,
    page: Optional[str] = None,
    user: Optional[str] = None,
    operation: Optional[str] = None,
    **extra_context,
) -> LoggerAdapter:
    """
    Cria logger com contexto adicional

    Args:
        name: Nome do logger
        page: Página atual do Streamlit
        user: Usuário logado
        operation: Operação sendo executada
        **extra_context: Contexto adicional

    Returns:
        LoggerAdapter com contexto
    """
    logger = get_logger(name)

    context = {}
    if page:
        context["page"] = page
    if user:
        context["user"] = user
    if operation:
        context["operation"] = operation

    context.update(extra_context)

    return LoggerAdapter(logger, context)


# Inicializa logging ao importar o módulo
_default_logger = setup_logging()
