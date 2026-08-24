from tinkle.core.schemas import ModelCapabilities, ModelProfile

def default_catalog() -> list[ModelProfile]:
    return [
        ModelProfile(
            id="small-local", provider="local",
            capabilities=ModelCapabilities(reasoning=.45,coding=.45,vision=.10,tool_use=.40,context_size=8192),
            cost_per_1k_tokens=0.0, latency_ms=80, local=True),
        ModelProfile(
            id="fast-cloud", provider="cloud",
            capabilities=ModelCapabilities(reasoning=.65,coding=.55,vision=.65,tool_use=.75,context_size=32768),
            cost_per_1k_tokens=.002, latency_ms=250, local=False),
        ModelProfile(
            id="reasoning-cloud", provider="cloud",
            capabilities=ModelCapabilities(reasoning=.98,coding=.85,vision=.75,tool_use=.90,context_size=128000),
            cost_per_1k_tokens=.02, latency_ms=900, local=False),
        ModelProfile(
            id="coding-cloud", provider="cloud",
            capabilities=ModelCapabilities(reasoning=.82,coding=.98,vision=.55,tool_use=.95,context_size=128000),
            cost_per_1k_tokens=.01, latency_ms=500, local=False),
        ModelProfile(
            id="research-cloud", provider="cloud",
            capabilities=ModelCapabilities(reasoning=.92,coding=.75,vision=.70,tool_use=.98,context_size=128000),
            cost_per_1k_tokens=.015, latency_ms=650, local=False),
    ]
