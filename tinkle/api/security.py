from fastapi import APIRouter, Depends
from tinkle.api.deps import principal_from_key, require
from tinkle.core.auth import Principal
from tinkle.core.container import audit, security_policy
from tinkle.core.schemas import Permission

router = APIRouter(prefix="/api/v1/security", tags=["security"])

@router.get("/status")
def security_status(p: Principal = Depends(principal_from_key)):
    require(p, Permission.read)
    return {
        "policy": {
            "rate_limit_per_minute": security_policy.max_requests_per_minute,
            "max_tool_input_bytes": security_policy.max_tool_input_bytes,
            "sandbox_required_for_sensitive_tools": security_policy.require_sandbox_for_sensitive_tools,
        },
        "audit_entries": len(audit.entries),
        "phase": 25,
    }
