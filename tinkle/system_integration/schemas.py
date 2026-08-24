from __future__ import annotations

from datetime import UTC, datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class CheckStatus(str,Enum): PASS='PASS';WARN='WARN';FAIL='FAIL';UNKNOWN='UNKNOWN';NOT_APPLICABLE='NOT_APPLICABLE'
class CapabilityStatus(str,Enum): IMPLEMENTED='IMPLEMENTED';PARTIAL='PARTIAL';EXTERNAL_DEPENDENCY='EXTERNAL_DEPENDENCY';NOT_AVAILABLE='NOT_AVAILABLE';NOT_VALIDATED='NOT_VALIDATED'
class ReleaseStatus(str,Enum): NOT_READY='NOT_READY';READY_FOR_INTERNAL_USE='READY_FOR_INTERNAL_USE';READY_FOR_DEVELOPER_TESTING='READY_FOR_DEVELOPER_TESTING';READY_FOR_CONTROLLED_RELEASE='READY_FOR_CONTROLLED_RELEASE'
class HealthCheck(BaseModel): name:str; status:CheckStatus; detail:str; evidence:list[str]=Field(default_factory=list); limitations:list[str]=Field(default_factory=list)
class SystemHealth(BaseModel): checks:list[HealthCheck]; status:CheckStatus; generated_at:datetime=Field(default_factory=lambda:datetime.now(UTC))
class Capability(BaseModel): phase:int; capability_id:str; description:str; owner_subsystem:str; status:CapabilityStatus; evidence:list[str]=Field(default_factory=list); limitations:list[str]=Field(default_factory=list); test_references:list[str]=Field(default_factory=list); epistemic_boundary:str
class CapabilityInventory(BaseModel): capabilities:list[Capability]; canonical_hash:str
class IntegrityReport(BaseModel): status:CheckStatus; orphaned_artifacts:list[str]=Field(default_factory=list); broken_references:list[str]=Field(default_factory=list); duplicate_edges:int=0; epistemic_findings:list[str]=Field(default_factory=list); provenance_findings:list[str]=Field(default_factory=list); canonical_hash:str
class ReproducibilityManifest(BaseModel): tinkle_version:str; git_commit:str; runtime:str; capabilities:list[str]; methods:dict[str,str]; test_result:str; environment_limitations:list[str]=Field(default_factory=list); canonical_hash:str
class ReadinessReport(BaseModel): status:ReleaseStatus; checks:list[HealthCheck]; limitations:list[str]=Field(default_factory=list); canonical_hash:str
class IntegrationEvent(BaseModel): event:str; details:dict[str,Any]=Field(default_factory=dict); timestamp:datetime=Field(default_factory=lambda:datetime.now(UTC))
