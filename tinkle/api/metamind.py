from fastapi import APIRouter, Header, HTTPException
from tinkle.core.auth import AuthService
from tinkle.metamind.orchestrator import MetaMind
from tinkle.metamind.schemas import TaskRequest

router = APIRouter(prefix="/api/v1/metamind")
auth = AuthService()
mind = MetaMind()

def principal(key):
    try:
        return auth.authenticate(key)
    except Exception as exc:
        raise HTTPException(401, "Invalid or missing API key") from exc

@router.post("/plan")
def plan(req: TaskRequest, x_api_key: str|None = Header(default=None)):
    principal(x_api_key)
    return mind.plan(req)

@router.post("/route-hint")
def route_hint(req: TaskRequest, x_api_key: str|None = Header(default=None)):
    principal(x_api_key)
    p = mind.plan(req)
    return mind.route_hint(p)
