import logging
import sys

import structlog

from app.core.config import Settings


def configure_logging(settings: Settings) -> None:
    """Send all logs (ours and the libraries') through one structlog pipeline."""

    # Steps applied to every log entry, whoever created it
    shared_processors = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.processors.TimeStamper(fmt="iso", utc=True),
    ]

    # Final output: JSON lines in production, readable coloured lines in development
    if settings.is_production:
        final_processors = [
            structlog.stdlib.ProcessorFormatter.remove_processors_meta,
            structlog.processors.format_exc_info,
            structlog.processors.JSONRenderer(),
        ]
    else:
        final_processors = [
            structlog.stdlib.ProcessorFormatter.remove_processors_meta,
            structlog.dev.ConsoleRenderer(),
        ]

    structlog.configure(
        processors=shared_processors + [structlog.stdlib.ProcessorFormatter.wrap_for_formatter],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(
        structlog.stdlib.ProcessorFormatter(
            foreign_pre_chain=shared_processors,
            processors=final_processors,
        )
    )

    root = logging.getLogger()
    root.handlers.clear()
    root.addHandler(handler)
    root.setLevel(settings.effective_log_level.upper())

    # Keep chatty libraries quiet even in debug mode
    for noisy in ("asyncio", "httpx", "httpcore", "watchfiles"):
        logging.getLogger(noisy).setLevel(logging.WARNING)

    # Uvicorn's own logs flow through our handler instead of its default format
    for name in ("uvicorn", "uvicorn.error"):
        uvicorn_logger = logging.getLogger(name)
        uvicorn_logger.handlers.clear()
        uvicorn_logger.propagate = True

    # Our middleware logs every request, so silence Uvicorn's duplicate access log
    access_logger = logging.getLogger("uvicorn.access")
    access_logger.handlers.clear()
    access_logger.propagate = False


def get_logger(name: str | None = None) -> structlog.stdlib.BoundLogger:
    """Return a logger. Pass a name such as 'docuchat.auth' to label its entries."""
    return structlog.get_logger(name)