from fastapi import APIRouter, Header, HTTPException
from tinkle.core.auth import AuthService
from tinkle.provenance.schemas import ProvenanceQuery, ProvenanceRecord
from tinkle.provenance.service import ProvenanceService
from tinkle.provenance.store import ProvenanceStore

router = APIRouter(prefix="/api/v1/provenance")
auth = AuthService()
service = ProvenanceService(ProvenanceStore())

def principal(key):
    try:
        return auth.authenticate(key)
    except Exception as exc:
        raise HTTPException(401, "Invalid or missing API key") from exc

@router.post("/records")
def add(record: ProvenanceRecord, x_api_key: str|None = Header(default=None)):
    principal(x_api_key)
    return service.record(record)

@router.post("/report")
def report(query: ProvenanceQuery, x_api_key: str|None = Header(default=None)):
    principal(x_api_key)
    return service.report(query)
