from __future__ import annotations
import math
from .schemas import ErgonomicsRequest, ErgonomicsResult

class ErgonomicsEngine:
    """Deterministic first-pass fit, ROM and mass-distribution checks."""
    def analyze(self, req: ErgonomicsRequest) -> ErgonomicsResult:
        if not all(math.isfinite(x) for x in [req.user_mass_kg, req.stature_m, req.suit_mass_kg]):
            raise ValueError('non-finite anthropometric input')
        for k, v in req.segment_lengths_m.items():
            if v <= 0 or not math.isfinite(v):
                raise ValueError(f'invalid segment length: {k}')
        total = sum(req.segment_lengths_m.values())
        scale = req.stature_m / max(total, 1e-9)
        estimates = {k: v * scale for k, v in req.segment_lengths_m.items()}
        checks=[]; warnings=[]
        for r in req.rom:
            if r.min_deg >= r.max_deg or r.user_min_deg >= r.user_max_deg:
                raise ValueError(f'invalid ROM for {r.name}')
            overlap_min=max(r.min_deg, r.user_min_deg); overlap_max=min(r.max_deg, r.user_max_deg)
            ok=overlap_min < overlap_max
            checks.append({'name':r.name,'compatible':ok,'overlap_min_deg':overlap_min,'overlap_max_deg':overlap_max})
            if not ok: warnings.append(f'ROM mismatch at {r.name}')
        total_mass=req.user_mass_kg+req.suit_mass_kg
        offset=sum(abs(v) for v in req.attachment_offsets_m.values())
        balance_index=offset/max(req.stature_m,1e-9)
        if balance_index > 0.25: warnings.append('Attachment offsets are large relative to stature; verify center-of-mass and gait effects.')
        return ErgonomicsResult(
            status='PRELIMINARY_ERGONOMICS_ANALYSIS', segment_estimates_m=estimates,
            rom_checks=checks, balance={'total_system_mass_kg':total_mass,'offset_index':balance_index},
            fit_warnings=warnings,
            verification_gates=['Measure user-specific anthropometry','Validate joint alignment and ROM with supervised testing','Check pressure/contact loads','Verify center of mass and gait dynamics','Independent human-safety review before physical use'],
            limitations=['Not a medical or biomechanical certification','No human-subject data is inferred beyond supplied inputs','Contact pressure, skin loading and dynamic gait require validated biomechanical models and supervised testing']
        )
