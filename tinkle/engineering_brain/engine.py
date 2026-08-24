from __future__ import annotations
import re
from .schemas import *

class EngineeringBrain:
    """Deterministic engineering decomposition layer.

    It converts a natural-language engineering intent into explicit domains,
    measurable requirements, decisions and verification gates. It deliberately
    does not pretend that a classification is a validated engineering design.
    """
    _DOMAIN_TERMS = {
        "Mechanical Engineering": ("structure", "frame", "load", "stress", "joint", "hinge", "gear", "torque", "mass"),
        "Electrical Engineering": ("voltage", "current", "wiring", "power", "battery", "bms", "motor"),
        "Electronics": ("sensor", "imu", "microcontroller", "pcb", "signal", "encoder"),
        "Robotics": ("robot", "actuator", "exoskeleton", "prosthetic", "servo", "motion"),
        "Control Systems": ("control", "feedback", "pid", "stability", "trajectory", "loop"),
        "Thermal Engineering": ("heat", "cooling", "temperature", "thermal", "radiator"),
        "Materials Engineering": ("material", "alloy", "carbon", "composite", "titanium", "strength"),
        "Energy Systems": ("energy", "battery", "runtime", "efficiency", "charging", "power"),
        "Software Engineering": ("software", "firmware", "api", "algorithm", "computer", "real-time"),
    }

    def analyze(self, req: EngineeringBrainRequest) -> EngineeringBrainResult:
        text = req.problem.strip()
        low = text.lower()
        domains: list[str] = []
        for domain, terms in self._DOMAIN_TERMS.items():
            if any(re.search(r"\b" + re.escape(term) + r"\b", low) for term in terms):
                domains.append(domain)
        if not domains:
            domains = ["Mechanical Engineering", "Robotics", "Control Systems"] if req.intent in {DesignIntent.DESIGN, DesignIntent.OPTIMIZE} else ["Mechanical Engineering"]

        requirements = self._requirements(req, low, domains)
        decisions = self._decisions(req, domains)
        unresolved = self._unresolved(req, low)
        confidence = max(0.35, min(0.92, 0.45 + 0.07 * len(domains) - 0.04 * len(unresolved)))
        return EngineeringBrainResult(
            status="ANALYSIS_COMPLETE",
            intent=req.intent,
            normalized_problem=" ".join(text.split()),
            requirements=requirements,
            domains=domains,
            decisions=decisions,
            verification_plan=self._verification(domains, req.intent),
            assumptions=["Requirements inferred from the supplied text are provisional.", "Engineering values must be replaced by measured, manufacturer, standard or validated data before real hardware use."],
            unresolved_items=unresolved,
            confidence=confidence,
            provenance={"engine": "ENGINEERING_BRAIN_2.0", "deterministic": True, "validated_design": False},
        )

    def _requirements(self, req, low, domains):
        out = [EngineeringRequirement(name="functional_goal", description=req.problem.strip(), category="function", priority=5)]
        if "weight" not in low and "mass" not in low:
            out.append(EngineeringRequirement(name="mass_budget", description="Define total system mass and subsystem mass budgets.", category="mechanical", priority=4))
        if "power" not in low and "battery" not in low:
            out.append(EngineeringRequirement(name="power_budget", description="Define peak and continuous electrical power limits.", category="energy", priority=4))
        if "safety" not in low:
            out.append(EngineeringRequirement(name="safety_limits", description="Define safe operating limits, emergency stop and failure behavior.", category="safety", priority=5))
        if "test" not in low and "validate" not in low:
            out.append(EngineeringRequirement(name="verification", description="Define measurable acceptance tests for each critical requirement.", category="validation", priority=5))
        if "human" in low or "wear" in low or "exoskeleton" in low:
            out.append(EngineeringRequirement(name="human_interface", description="Define anthropometric fit, range of motion and allowable human interaction loads.", category="ergonomics", priority=5))
        return out

    def _decisions(self, req, domains):
        return [EngineeringDecision(decision=f"Include {domain}", rationale="The problem language or design intent indicates this domain is relevant.", domains=[domain], confidence=0.72) for domain in domains]

    def _unresolved(self, req, low):
        missing=[]
        for key, label in (("dimensions", "principal dimensions"), ("mass", "mass target"), ("power", "power budget"), ("material", "material specification")):
            if key not in req.constraints and key not in low:
                missing.append(f"Define {label}.")
        return missing

    @staticmethod
    def _verification(domains, intent):
        checks=["Requirement traceability review", "Independent calculation review", "Boundary-condition review", "Failure-mode and safety review"]
        if "Mechanical Engineering" in domains: checks.append("Structural load and deflection verification")
        if "Control Systems" in domains: checks.append("Closed-loop stability and response verification")
        if "Energy Systems" in domains: checks.append("Peak/continuous power and thermal budget verification")
        if intent == DesignIntent.VALIDATE: checks.append("Physical test correlation against measured data")
        return checks
