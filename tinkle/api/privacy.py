from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from tinkle.api.deps import principal_from_key, require
from tinkle.core.auth import Principal
from tinkle.core.container import privacy
from tinkle.core.schemas import Permission

router = APIRouter(prefix="/api/v1/privacy", tags=["privacy"])

class PrivacyUpdate(BaseModel):
    store_data: bool | None = None
    allow_cloud_models: bool | None = None
    local_only: bool | None = None
    allow_delete: bool | None = None
    allow_export: bool | None = None

@router.get("")
def get_privacy(p: Principal = Depends(principal_from_key)):
    require(p, Permission.read)
    return {"owner": p.name, "settings": privacy.get(p.name).__dict__}

@router.put("")
def update_privacy(req: PrivacyUpdate, p: Principal = Depends(principal_from_key)):
    require(p, Permission.write)
    changes = {k: v for k, v in req.model_dump().items() if v is not None}
    settings = privacy.update(p.name, **changes)
    return {"owner": p.name, "settings": settings.__dict__}

@router.post("/local-mode")
def enable_local_mode(p: Principal = Depends(principal_from_key)):
    require(p, Permission.write)
    settings = privacy.update(p.name, local_only=True, allow_cloud_models=False)
    return {"owner": p.name, "local_mode": True, "settings": settings.__dict__}
