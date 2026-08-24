from __future__ import annotations

import math
from typing import Callable

from tinkle.science_engine.schemas import (
    ScienceDomain,
    ScienceModule,
    ScienceRequest,
    ScienceResult,
    ScienceSolveRequest,
)


class ScienceEngine:
    """Deterministic scientific primitives with explicit assumptions and units.

    The engine intentionally solves a small, auditable set of textbook models.
    It does not fabricate empirical facts or substitute for experimental evidence.
    """

    G = 6.67430e-11
    R = 8.31446261815324
    KELVIN_OFFSET = 273.15

    _MODULES = {
        ScienceDomain.physics: ScienceModule(
            domain=ScienceDomain.physics,
            status="BOUNDARY_READY",
            capabilities=["domain routing", "kinematics", "newtonian mechanics", "gravity", "projectile range", "pendulum period"],
        ),
        ScienceDomain.chemistry: ScienceModule(
            domain=ScienceDomain.chemistry,
            status="BOUNDARY_READY",
            capabilities=["domain routing", "ideal gas law", "molar concentration", "pH", "dilution"],
        ),
        ScienceDomain.biology: ScienceModule(
            domain=ScienceDomain.biology,
            status="BOUNDARY_READY",
            capabilities=["domain routing", "exponential growth", "doubling time", "logistic growth"],
        ),
        ScienceDomain.materials_science: ScienceModule(
            domain=ScienceDomain.materials_science,
            status="BOUNDARY_READY",
            capabilities=["domain routing", "stress", "strain", "young's modulus", "thermal expansion"],
        ),
        ScienceDomain.energy: ScienceModule(
            domain=ScienceDomain.energy,
            status="BOUNDARY_READY",
            capabilities=["domain routing", "power", "efficiency", "kinetic energy", "potential energy", "heat energy"],
        ),
        ScienceDomain.astronomy: ScienceModule(
            domain=ScienceDomain.astronomy,
            status="BOUNDARY_READY",
            capabilities=["domain routing", "two-body orbital period", "escape velocity"],
        ),
    }

    _SOLVERS: dict[tuple[ScienceDomain, str], Callable[[dict[str, float]], dict[str, float]]] = {}

    def __init__(self) -> None:
        self._SOLVERS = {
            (ScienceDomain.physics, "kinematics_v1"): self._kinematics,
            (ScienceDomain.physics, "gravity_v1"): self._gravity,
            (ScienceDomain.chemistry, "ideal_gas_v1"): self._ideal_gas,
            (ScienceDomain.chemistry, "concentration_v1"): self._concentration,
            (ScienceDomain.biology, "exponential_growth_v1"): self._growth,
            (ScienceDomain.biology, "doubling_time_v1"): self._doubling_time,
            (ScienceDomain.materials_science, "stress_strain_v1"): self._stress_strain,
            (ScienceDomain.energy, "power_v1"): self._power,
            (ScienceDomain.energy, "efficiency_v1"): self._efficiency,
            (ScienceDomain.energy, "kinetic_energy_v1"): self._kinetic_energy,
            (ScienceDomain.astronomy, "orbital_period_v1"): self._orbital_period,
            (ScienceDomain.physics, "projectile_range_v1"): self._projectile_range,
            (ScienceDomain.physics, "pendulum_period_v1"): self._pendulum_period,
            (ScienceDomain.chemistry, "ph_v1"): self._ph,
            (ScienceDomain.chemistry, "dilution_v1"): self._dilution,
            (ScienceDomain.biology, "logistic_growth_v1"): self._logistic_growth,
            (ScienceDomain.materials_science, "thermal_expansion_v1"): self._thermal_expansion,
            (ScienceDomain.energy, "potential_energy_v1"): self._potential_energy,
            (ScienceDomain.energy, "heat_energy_v1"): self._heat_energy,
            (ScienceDomain.astronomy, "escape_velocity_v1"): self._escape_velocity,
        }

    def inspect(self, request: ScienceRequest) -> ScienceResult:
        module = self._MODULES[request.domain]
        return ScienceResult(
            question=request.question.strip(),
            domain=request.domain,
            status="MODULE_READY",
            module=module,
            answer=None,
            evidence_required=True,
            limitations=[
                "Deterministic scientific primitives are available through the solve operation.",
                "A calculation is a model result, not experimental evidence; assumptions and units must be checked for the real system.",
            ],
        )

    def solve(self, request: ScienceSolveRequest) -> ScienceResult:
        module = self._MODULES[request.domain]
        key = (request.domain, request.model)
        solver = self._SOLVERS.get(key)
        if solver is None:
            raise ValueError(f"Unsupported scientific model: {request.domain.value}/{request.model}")
        inputs = self._validate_inputs(request.inputs)
        try:
            values = solver(inputs)
        except (KeyError, ValueError, ZeroDivisionError, OverflowError) as exc:
            raise ValueError(str(exc)) from exc
        for name, value in values.items():
            if not math.isfinite(value):
                raise ValueError(f"Non-finite scientific result: {name}")
        calculation = {
            "model": request.model,
            "inputs": inputs,
            "outputs": values,
            "assumptions": self._assumptions(request.model),
            "evidence_required": True,
        }
        answer = ", ".join(f"{name}={value:.12g}" for name, value in values.items())
        return ScienceResult(
            question=request.problem.strip(),
            domain=request.domain,
            status="CALCULATED",
            module=module,
            answer=answer,
            evidence_required=True,
            calculation=calculation,
            limitations=["This is a deterministic textbook-model calculation, not empirical validation."],
        )

    @staticmethod
    def _validate_inputs(inputs: dict[str, float]) -> dict[str, float]:
        if len(inputs) > 32:
            raise ValueError("Too many inputs")
        out = {}
        for name, value in inputs.items():
            if not isinstance(name, str) or not name.isidentifier() or name.startswith("_"):
                raise ValueError(f"Invalid input name: {name!r}")
            if not isinstance(value, (int, float)) or not math.isfinite(float(value)):
                raise ValueError(f"Input {name!r} must be finite")
            out[name] = float(value)
        return out

    @staticmethod
    def _require(i: dict[str, float], *names: str) -> list[float]:
        return [i[name] for name in names]

    @classmethod
    def _kinematics(cls, i: dict[str, float]) -> dict[str, float]:
        u, a, t = cls._require(i, "initial_velocity", "acceleration", "time")
        return {"final_velocity": u + a * t, "displacement": u * t + 0.5 * a * t * t}

    @classmethod
    def _gravity(cls, i: dict[str, float]) -> dict[str, float]:
        m1, m2, r = cls._require(i, "mass1", "mass2", "distance")
        if r <= 0:
            raise ValueError("distance must be positive")
        return {"force_newtons": cls.G * m1 * m2 / (r * r)}

    @classmethod
    def _ideal_gas(cls, i: dict[str, float]) -> dict[str, float]:
        n, temperature, volume = cls._require(i, "moles", "temperature_k", "volume_m3")
        if temperature <= 0 or volume <= 0:
            raise ValueError("temperature_k and volume_m3 must be positive")
        return {"pressure_pa": n * cls.R * temperature / volume}

    @staticmethod
    def _concentration(i: dict[str, float]) -> dict[str, float]:
        moles, volume_l = ScienceEngine._require(i, "moles", "volume_l")
        if volume_l <= 0:
            raise ValueError("volume_l must be positive")
        return {"molarity_mol_per_l": moles / volume_l}

    @staticmethod
    def _growth(i: dict[str, float]) -> dict[str, float]:
        n0, rate, time = ScienceEngine._require(i, "initial_population", "growth_rate", "time")
        return {"population": n0 * math.exp(rate * time)}

    @staticmethod
    def _doubling_time(i: dict[str, float]) -> dict[str, float]:
        rate = i["growth_rate"]
        if rate <= 0:
            raise ValueError("growth_rate must be positive")
        return {"doubling_time": math.log(2) / rate}

    @staticmethod
    def _stress_strain(i: dict[str, float]) -> dict[str, float]:
        force, area, length, delta_length = ScienceEngine._require(i, "force_n", "area_m2", "length_m", "delta_length_m")
        if area <= 0 or length <= 0:
            raise ValueError("area_m2 and length_m must be positive")
        if delta_length == 0:
            raise ValueError("delta_length_m must be non-zero to calculate Young's modulus")
        return {"stress_pa": force / area, "strain": delta_length / length, "youngs_modulus_pa": (force / area) / (delta_length / length)}

    @staticmethod
    def _power(i: dict[str, float]) -> dict[str, float]:
        energy, time = ScienceEngine._require(i, "energy_j", "time_s")
        if time <= 0:
            raise ValueError("time_s must be positive")
        return {"power_w": energy / time}

    @staticmethod
    def _efficiency(i: dict[str, float]) -> dict[str, float]:
        useful, input_energy = ScienceEngine._require(i, "useful_energy_j", "input_energy_j")
        if input_energy <= 0:
            raise ValueError("input_energy_j must be positive")
        return {"efficiency": useful / input_energy, "efficiency_percent": 100 * useful / input_energy}

    @staticmethod
    def _kinetic_energy(i: dict[str, float]) -> dict[str, float]:
        mass, velocity = ScienceEngine._require(i, "mass_kg", "velocity_m_s")
        return {"kinetic_energy_j": 0.5 * mass * velocity * velocity}

    @classmethod
    def _orbital_period(cls, i: dict[str, float]) -> dict[str, float]:
        radius, central_mass = cls._require(i, "orbital_radius_m", "central_mass_kg")
        if radius <= 0 or central_mass <= 0:
            raise ValueError("orbital_radius_m and central_mass_kg must be positive")
        period = 2 * math.pi * math.sqrt(radius**3 / (cls.G * central_mass))
        return {"orbital_period_s": period}

    @classmethod
    def _projectile_range(cls, i: dict[str, float]) -> dict[str, float]:
        v, angle_deg = cls._require(i, "initial_speed_m_s", "launch_angle_deg")
        gravity = i.get("gravity_m_s2", 9.81)
        angle = math.radians(angle_deg)
        return {"range_m": (v * v) * math.sin(2 * angle) / gravity}

    @classmethod
    def _pendulum_period(cls, i: dict[str, float]) -> dict[str, float]:
        length = i["length_m"]
        gravity = i.get("gravity_m_s2", 9.81)
        if length <= 0:
            raise ValueError("length_m must be positive")
        return {"period_s": 2 * math.pi * math.sqrt(length / gravity)}

    @staticmethod
    def _ph(i: dict[str, float]) -> dict[str, float]:
        h_conc = i["hydrogen_ion_concentration_mol_l"]
        if h_conc <= 0:
            raise ValueError("hydrogen_ion_concentration_mol_l must be positive")
        return {"ph": -math.log10(h_conc)}

    @staticmethod
    def _dilution(i: dict[str, float]) -> dict[str, float]:
        c1, v1, v2 = ScienceEngine._require(i, "initial_concentration", "initial_volume", "final_volume")
        if v2 <= 0:
            raise ValueError("final_volume must be positive")
        return {"final_concentration": c1 * v1 / v2}

    @staticmethod
    def _logistic_growth(i: dict[str, float]) -> dict[str, float]:
        capacity, p0, rate, time = ScienceEngine._require(i, "carrying_capacity", "initial_population", "growth_rate", "time")
        if capacity <= 0 or p0 <= 0:
            raise ValueError("carrying_capacity and initial_population must be positive")
        return {"population": capacity / (1 + ((capacity - p0) / p0) * math.exp(-rate * time))}

    @staticmethod
    def _thermal_expansion(i: dict[str, float]) -> dict[str, float]:
        alpha, length, delta_t = ScienceEngine._require(i, "expansion_coefficient", "length_m", "delta_temperature_k")
        if length <= 0:
            raise ValueError("length_m must be positive")
        return {"delta_length_m": alpha * length * delta_t}

    @staticmethod
    def _potential_energy(i: dict[str, float]) -> dict[str, float]:
        mass, height = ScienceEngine._require(i, "mass_kg", "height_m")
        gravity = i.get("gravity_m_s2", 9.81)
        return {"potential_energy_j": mass * gravity * height}

    @staticmethod
    def _heat_energy(i: dict[str, float]) -> dict[str, float]:
        mass, specific_heat, delta_t = ScienceEngine._require(i, "mass_kg", "specific_heat_j_per_kgk", "delta_temperature_k")
        return {"heat_energy_j": mass * specific_heat * delta_t}

    @classmethod
    def _escape_velocity(cls, i: dict[str, float]) -> dict[str, float]:
        mass, radius = cls._require(i, "central_mass_kg", "radius_m")
        if radius <= 0:
            raise ValueError("radius_m must be positive")
        return {"escape_velocity_m_s": math.sqrt(2 * cls.G * mass / radius)}

    @staticmethod
    def _assumptions(model: str) -> list[str]:
        common = ["Inputs are interpreted in the units stated by their names.", "The model is deterministic and idealized."]
        specific = {
            "kinematics_v1": "Constant acceleration in one dimension.",
            "gravity_v1": "Newtonian point-mass approximation.",
            "ideal_gas_v1": "Ideal gas behavior with SI units.",
            "concentration_v1": "Solution volume is treated as the stated final volume.",
            "exponential_growth_v1": "Constant exponential growth rate.",
            "doubling_time_v1": "Constant positive exponential growth rate.",
            "stress_strain_v1": "Uniform axial loading and small-strain interpretation.",
            "power_v1": "Average power equals energy divided by elapsed time.",
            "efficiency_v1": "Useful/input energy ratio defines efficiency.",
            "kinetic_energy_v1": "Classical, non-relativistic kinetic energy.",
            "orbital_period_v1": "Circular two-body Newtonian orbit.",
            "projectile_range_v1": "Flat ground, no air resistance, launch and landing at the same height.",
            "pendulum_period_v1": "Simple pendulum, small-angle approximation.",
            "ph_v1": "Dilute aqueous solution; activity approximated by concentration.",
            "dilution_v1": "Conservation of solute moles across dilution (C1V1=C2V2).",
            "logistic_growth_v1": "Constant carrying capacity and intrinsic growth rate.",
            "thermal_expansion_v1": "Linear thermal expansion of an isotropic solid over a small temperature range.",
            "potential_energy_v1": "Uniform gravitational field near a surface.",
            "heat_energy_v1": "Constant specific heat capacity, no phase change.",
            "escape_velocity_v1": "Newtonian point-mass approximation, no atmosphere.",
        }
        return common + [specific[model]]

    def modules(self) -> list[ScienceModule]:
        return list(self._MODULES.values())
