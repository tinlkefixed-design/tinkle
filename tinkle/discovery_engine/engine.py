from __future__ import annotations
from collections import defaultdict
from tinkle.discovery_engine.schemas import (
    DiscoveryCandidate, DiscoveryRequest, DiscoveryResult, DiscoveryStatus,
)

class DiscoveryEngine:
    """Phase 19 bounded discovery boundary.

    The Blueprint names Phase 19 Discovery Engine. Its detailed supported
    discovery concept is the Emergent Discovery Engine: search for shared
    patterns across fields, combine patterns with mathematical structure,
    produce a new hypothesis, and never treat it as fact before verification.
    This implementation performs that operation only on caller-supplied,
    explicit observations; it does not invent evidence or claim autonomous
    scientific discovery beyond the supplied inputs.
    """
    def discover(self, request: DiscoveryRequest) -> DiscoveryResult:
        by_pattern: dict[str, list] = defaultdict(list)
        for obs in request.observations:
            key = obs.pattern.strip().lower()
            if key:
                by_pattern[key].append(obs)

        candidates: list[DiscoveryCandidate] = []
        # A cross-domain candidate requires the same normalized pattern to be
        # observed in at least two distinct domains.
        for idx, (pattern_key, observations) in enumerate(by_pattern.items(), 1):
            domains = list(dict.fromkeys(o.domain.strip() for o in observations if o.domain.strip()))
            if len(domains) < 2:
                continue
            patterns = list(dict.fromkeys(o.pattern.strip() for o in observations))
            evidence = [e for o in observations for e in o.evidence]
            local_conf = sum(o.confidence for o in observations) / len(observations)
            math_bonus = 0.1 if request.mathematical_structures else 0.0
            confidence = min(1.0, round(local_conf + math_bonus, 4))
            statement = f"A shared pattern may connect: {'; '.join(domains)}"
            candidates.append(DiscoveryCandidate(
                id=f'D{idx}', statement=statement, source_domains=domains,
                patterns=patterns, mathematical_structures=request.mathematical_structures,
                status=DiscoveryStatus.NEEDS_VERIFICATION,
                confidence=confidence, evidence=evidence,
                metadata={'normalized_pattern': pattern_key, 'hypothesis_only': True},
            ))

        # If explicit verification is supplied, it changes status only; no
        # verification is invented by this engine.
        if request.verify and request.verification_result:
            result = request.verification_result.strip().lower()
            target = DiscoveryStatus.VERIFIED if result == 'verified' else DiscoveryStatus.REJECTED if result == 'rejected' else DiscoveryStatus.NEEDS_VERIFICATION
            for candidate in candidates:
                candidate.status = target

        return DiscoveryResult(
            question=request.question,
            candidates=candidates,
            status='DISCOVERY_CANDIDATES_FOUND' if candidates else 'NO_CROSS_DOMAIN_PATTERN_FOUND',
            cross_domain=bool(candidates),
            limitations=[
                'Discovery is bounded to caller-supplied pattern observations.',
                'A candidate is a hypothesis and is not a fact until independently verified.',
                'The Blueprint does not specify an autonomous discovery model, external search provider, or scientific truth oracle.',
            ],
        )
