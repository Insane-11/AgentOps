"""Optional self-hosted observability via LangFuse (open-source LangSmith alternative).

LangFuse is completely free, self-hostable, and MIT-licensed.
It provides: LLM tracing, spans, evaluation, feedback, cost tracking, dashboards.

To enable:
1. Add `langfuse` to requirements.txt (already present, commented out)
2. Uncomment the `langfuse` service in docker-compose.yml
3. Set LANGFUSE_SECRET_KEY and LANGFUSE_PUBLIC_KEY in environment

If not configured, all calls are no-ops and the app runs exactly the same.
"""

from app.config import settings

_langfuse_handler = None
_langfuse_available = False

try:
    from langfuse import Langfuse
    from langfuse.callback import CallbackHandler

    if settings.langfuse_secret_key and settings.langfuse_public_key:
        _langfuse = Langfuse(
            secret_key=settings.langfuse_secret_key,
            public_key=settings.langfuse_public_key,
            host=settings.langfuse_host or "http://localhost:3000",
        )
        _langfuse_handler = CallbackHandler(
            secret_key=settings.langfuse_secret_key,
            public_key=settings.langfuse_public_key,
            host=settings.langfuse_host or "http://localhost:3000",
        )
        _langfuse_available = True
except ImportError:
    pass


def get_langfuse_handler():
    return _langfuse_handler


def is_langfuse_available():
    return _langfuse_available


def get_trace_callbacks():
    if _langfuse_handler:
        return [_langfuse_handler]
    return []
