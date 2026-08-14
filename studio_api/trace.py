from __future__ import annotations

from contextvars import ContextVar
from uuid import uuid4


trace_id_var: ContextVar[str] = ContextVar("trace_id", default="")


def new_trace_id() -> str:
    return f"tr_{uuid4().hex}"


def get_trace_id() -> str:
    trace_id = trace_id_var.get()
    if not trace_id:
        trace_id = new_trace_id()
        trace_id_var.set(trace_id)
    return trace_id
