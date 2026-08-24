# Tinkle Observability

Tinkle exposes a dependency-free Prometheus exposition endpoint at `/api/v1/observer/metrics` behind the normal read permission. `prometheus.yml` and `docker-compose.observability.yml` provide a deployment path for Prometheus and Grafana.

The Observer records supplied observations; it does not fabricate CPU, RAM, model-drift, or accuracy measurements. OpenTelemetry remains an integration target for a deployment that installs the corresponding collector/SDK.
