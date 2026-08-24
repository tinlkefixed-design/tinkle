from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from tinkle.api.deps import principal_from_key, require
from tinkle.core.auth import Principal
from tinkle.core.schemas import Permission

router = APIRouter(prefix="/api/v1/integration", tags=["full-integration"])


class IntegrationSmokeRequest(BaseModel):
    prompt: str = Field(min_length=1, max_length=5000)


@router.get("/status")
def status(p: Principal = Depends(principal_from_key)):
    require(p, Permission.read)
    from tinkle.api.main import integration
    return integration.status()


@router.post("/smoke")
def smoke(req: IntegrationSmokeRequest, p: Principal = Depends(principal_from_key)):
    require(p, Permission.execute)
    from tinkle.api.main import integration
    return integration.smoke(p.name, req.prompt, set(p.permissions))
