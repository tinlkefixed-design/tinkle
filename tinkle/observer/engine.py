from __future__ import annotations
from collections import defaultdict
from threading import Lock
from .schemas import METRICS, ObserverEvent, ObserverEventRequest, ObserverMetric, ObserverSnapshot

class TinkleObserver:
    """Independent observation boundary for Tinkle's own operating indicators.

    The Blueprint names the metrics but does not prescribe telemetry collectors,
    statistical estimators, thresholds, or anomaly algorithms. This engine records
    explicit observations and aggregates them without inventing measurements.
    """
    def __init__(self) -> None:
        self._events: list[ObserverEvent] = []
        self._lock = Lock()

    def observe(self, request: ObserverEventRequest) -> ObserverEvent:
        event = ObserverEvent(**request.model_dump())
        with self._lock:
            self._events.append(event)
        return event

    def snapshot(self) -> ObserverSnapshot:
        with self._lock:
            events_snapshot = list(self._events)
        grouped = defaultdict(list)
        for event in events_snapshot:
            grouped[event.metric].append(event)
        metrics = []
        for metric in METRICS:
            events = grouped.get(metric, [])
            latest = events[-1] if events else None
            metrics.append(ObserverMetric(
                metric=metric,
                count=len(events),
                latest_value=latest.value if latest else None,
                latest_status=latest.status if latest else None,
                latest_source=latest.source if latest else None,
            ))
        return ObserverSnapshot(
            metrics=metrics,
            total_events=len(events_snapshot),
            limitations=[
                'The Blueprint specifies the monitored metrics but does not define telemetry collectors or anomaly thresholds.',
                'Values are observations supplied by integrated components; the Observer does not fabricate measurements.',
                'Model Drift and other higher-order metrics require future evidence/telemetry providers when their implementation is specified.'
            ],
        )

    def events(self, metric: str | None = None) -> list[ObserverEvent]:
        with self._lock:
            events = list(self._events)
        if metric is None:
            return events
        return [e for e in events if e.metric == metric]

    def prometheus(self) -> str:
        """Render a dependency-free Prometheus exposition snapshot."""
        snap = self.snapshot()
        lines = [
            "# HELP tinkle_observer_events_total Number of observed Tinkle events.",
            "# TYPE tinkle_observer_events_total counter",
            f"tinkle_observer_events_total {snap.total_events}",
        ]
        for item in snap.metrics:
            label = item.metric.replace(' ', '_').replace('-', '_').lower()
            lines.append(f'tinkle_observer_metric_events{{metric="{label}"}} {item.count}')
            if item.latest_value is not None:
                lines.append(f'tinkle_observer_metric_value{{metric="{label}"}} {item.latest_value}')
        return "\n".join(lines) + "\n"
