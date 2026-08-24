from __future__ import annotations

from tinkle.core.errors import NoCompatibleModelError
from tinkle.core.schemas import ProviderRequest, ProviderResponse, RoutingRequest
from tinkle.router.providers import ProviderUnavailableError, build_provider_map
from tinkle.router.router import ModelRouter


class ModelRuntime:
    """Turns routing decisions into actual provider execution."""

    def __init__(self, router: ModelRouter) -> None:
        self.router = router
        self.providers = build_provider_map()

    def generate(self, request: RoutingRequest) -> ProviderResponse:
        decision = self.router.route(request)
        provider = self.providers.get(decision.provider)
        if provider is None:
            raise ProviderUnavailableError(
                f"No provider adapter is registered for '{decision.provider}'."
            )
        try:
            return provider.generate(
                ProviderRequest(model_id=decision.selected_model, prompt=request.prompt)
            )
        except ProviderUnavailableError:
            # Do not silently switch privacy boundaries. A private request may
            # only fall back to another local model.
            for fallback_id in decision.fallback_models:
                profile = next((m for m in self.router.catalog if m.id == fallback_id), None)
                if profile is None or profile.provider != decision.provider:
                    continue
                try:
                    return provider.generate(
                        ProviderRequest(model_id=profile.id, prompt=request.prompt)
                    )
                except ProviderUnavailableError:
                    continue
            raise
