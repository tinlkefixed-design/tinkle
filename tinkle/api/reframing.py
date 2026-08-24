from fastapi import APIRouter, Header, HTTPException
from tinkle.core.auth import AuthService
from tinkle.reframing.engine import ProblemReframingEngine
from tinkle.reframing.schemas import ReframingRequest

router=APIRouter(prefix="/api/v1/reframing")
auth=AuthService()
engine=ProblemReframingEngine()

def principal(key):
    try: return auth.authenticate(key)
    except Exception as exc: raise HTTPException(401,"Invalid or missing API key") from exc

@router.post("")
def reframe(req: ReframingRequest, x_api_key: str|None=Header(default=None)):
    principal(x_api_key)
    return engine.reframe(req)
