from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
import difflib
from tinkle.advanced.engines import ControlledImprovementRuntime

@dataclass
class ImprovementCandidate:
    proposal_id:str
    before:str
    after:str
    diff:str
    stage:str="PROPOSAL"

class SelfImprovementRuntime:
    """Controlled source-improvement lifecycle. Production writes require approval."""
    def __init__(self): self.lifecycle=ControlledImprovementRuntime()
    def propose(self,proposal_id:str,before:str,after:str)->ImprovementCandidate:
        diff="\n".join(difflib.unified_diff(before.splitlines(),after.splitlines(),lineterm=""))
        return ImprovementCandidate(proposal_id,before,after,diff)
    def apply(self,candidate:ImprovementCandidate,target:Path,approved:bool)->str:
        if not approved: raise PermissionError("human approval required")
        target.write_text(candidate.after,encoding="utf-8"); return str(target)
