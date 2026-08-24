from tinkle.core.schemas import ProviderRequest, RoutingRequest
from tinkle.router.providers import OpenAICompatibleProvider, ProviderUnavailableError


def test_unconfigured_cloud_provider_fails_explicitly():
    provider = OpenAICompatibleProvider('cloud', 'http://127.0.0.1:1', '')
    try:
        provider.generate(ProviderRequest(model_id='x', prompt='hello'))
    except ProviderUnavailableError as exc:
        assert 'API key' in str(exc)
    else:
        raise AssertionError('expected explicit provider failure')
