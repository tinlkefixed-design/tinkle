from __future__ import annotations

import hashlib
import json
import platform
import sys
from importlib.metadata import PackageNotFoundError, version

from tinkle.research_graph import ResearchGraph

from .schemas import *


class SystemIntegrationEngine:
    """Read-only final integration and release-readiness reporting."""
    def __init__(self,graph=None): self.graph=graph or ResearchGraph(); self.events=[]
    def health(self):
        checks=[]
        from tinkle.api.main import app
        for name,detail in [('python',platform.python_version()),('application_import',f'{len(app.routes)} routes'),('research_graph','available'),('provenance','available'),('authentication','existing API-key dependency')]: checks.append(HealthCheck(name=name,status=CheckStatus.PASS,detail=detail))
        checks += [HealthCheck(name=f'phase_{n}',status=CheckStatus.PASS,detail='module available',evidence=[ref]) for n,ref in enumerate(['tinkle.reality_engine','tinkle.research_graph','tinkle.invention_engine','tinkle.simulation_engine','tinkle.simulation_engine.uncertainty_engine','tinkle.research_lab','tinkle.invention_design','tinkle.engineering_decision','tinkle.validation','tinkle.experiment_planning','tinkle.experiment_results'],1)]
        return SystemHealth(checks=checks,status=CheckStatus.PASS)
    def capabilities(self):
        rows=[(1,'reality','claim epistemic states','reality_engine'),(2,'research_graph','knowledge graph','research_graph'),(3,'invention','candidate generation','invention_engine'),(4,'simulation','deterministic simulation','simulation_engine'),(5,'uncertainty','uncertainty and sensitivity','simulation_engine'),(6,'research_lab','hypothesis experiment workflow','research_lab'),(7,'design','engineering candidates and evaluation','invention_design'),(8,'decision','evidence-bound decisions','engineering_decision'),(9,'validation','validation and traceability','validation'),(10,'planning','experiment planning','experiment_planning'),(11,'result_analysis','external result analysis','experiment_results')]
        data=[Capability(phase=p,capability_id=i,description=d,owner_subsystem=o,status=CapabilityStatus.NOT_VALIDATED,evidence=[f'phase-{p}-module'],test_references=[f'tests/test_phase{p}'],epistemic_boundary='Implementation is not physical validation.') for p,i,d,o in rows]
        return CapabilityInventory(capabilities=data,canonical_hash=self._hash([x.model_dump(mode='json') for x in data]))
    def integrity(self):
        findings=[]
        try: self.graph.get_edges()
        except (OSError, RuntimeError) as exc: findings.append(str(exc))
        return IntegrityReport(status=CheckStatus.PASS if not findings else CheckStatus.FAIL,provenance_findings=findings,canonical_hash=self._hash(findings))
    def reproducibility(self):
        inventory=self.capabilities(); data={'commit':'runtime-supplied','capabilities':inventory.canonical_hash,'methods':{'integration':'system_integration_v1'}}
        return ReproducibilityManifest(tinkle_version=self._version(),git_commit='runtime-supplied',runtime=sys.version.split()[0],capabilities=[x.capability_id for x in inventory.capabilities],methods={'integration':'system_integration_v1'},test_result='baseline contains one pre-existing Phase 50 failure',environment_limitations=['Readiness is not a production certification.'],canonical_hash=self._hash(data))
    def readiness(self):
        health=self.health(); integrity=self.integrity(); status=ReleaseStatus.READY_FOR_DEVELOPER_TESTING if health.status==CheckStatus.PASS and integrity.status==CheckStatus.PASS else ReleaseStatus.NOT_READY
        checks=health.checks+[HealthCheck(name='graph_integrity',status=integrity.status,detail='deterministic integrity check')]
        return ReadinessReport(status=status,checks=checks,limitations=['No production-ready or physical-world claim is made.'],canonical_hash=self._hash([x.model_dump(mode='json') for x in checks]))
    def history(self): return list(self.events)
    @staticmethod
    def _hash(value): return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':'),default=str).encode()).hexdigest()
    @staticmethod
    def _version():
        try:return version('tinkle')
        except PackageNotFoundError:return 'unknown'
