from __future__ import annotations
from contextlib import contextmanager
import time

class OpenTelemetryBridge:
    """Optional OpenTelemetry bridge with a deterministic local span fallback."""
    def __init__(self):
        self.spans=[]
        try:
            from opentelemetry import trace
            self._tracer=trace.get_tracer("tinkle")
        except Exception:
            self._tracer=None
    @contextmanager
    def span(self,name:str,attributes:dict|None=None):
        start=time.perf_counter()
        if self._tracer:
            with self._tracer.start_as_current_span(name,attributes=attributes or {}): yield
        else:
            try: yield
            finally: self.spans.append({"name":name,"duration_ms":(time.perf_counter()-start)*1000,"attributes":attributes or {}})
