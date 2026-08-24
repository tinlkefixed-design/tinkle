from fastapi import Header, HTTPException, status
from tinkle.core.auth import AuthService, Principal
from tinkle.core.container import events, rate_limiter
from tinkle.core.errors import AuthenticationError, PermissionDeniedError
from tinkle.core.schemas import Event, Permission

auth = AuthService(events)

def principal_from_key(x_api_key: str | None = Header(default=None)) -> Principal:
    if not rate_limiter.allow(x_api_key or "anonymous"):
        events.publish(Event(type="security.rate_limited", actor="anonymous", payload={"scope":"api_key"}))
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail="Rate limit exceeded")
    try:
        return auth.authenticate(x_api_key)
    except AuthenticationError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or missing API key") from exc

def require(principal: Principal, permission: Permission) -> None:
    try:
        auth.require(principal, permission)
    except PermissionDeniedError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc
