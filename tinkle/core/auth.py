from dataclasses import dataclass
import hmac
from .config import settings
from .errors import AuthenticationError, PermissionDeniedError
from .schemas import Permission
from .events import EventBus
from .schemas import Event

@dataclass(frozen=True)
class Principal:
    name: str
    permissions: frozenset[Permission]

class AuthService:
    def __init__(self, events: EventBus | None = None):
        self.events = events

    def _deny(self, reason: str, actor: str = "anonymous") -> None:
        if self.events:
            self.events.publish(Event(type="auth.denied", actor=actor, payload={"reason": reason}))

    def authenticate(self, api_key: str | None) -> Principal:
        if not api_key:
            self._deny("missing_api_key")
            raise AuthenticationError("Invalid or missing API key")
        matched = next((candidate for candidate in settings.valid_api_keys
                        if hmac.compare_digest(candidate, api_key)), None)
        if matched is None:
            self._deny("invalid_api_key")
            raise AuthenticationError("Invalid or missing API key")
        permissions = settings.permissions_for_key(matched)
        return Principal(settings.principal_for_key(matched), frozenset(permissions))

    def require(self, p: Principal, permission: Permission) -> None:
        if Permission.admin not in p.permissions and permission not in p.permissions:
            self._deny("permission_denied", p.name)
            raise PermissionDeniedError(f"Missing permission: {permission.value}")
