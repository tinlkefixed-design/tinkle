from tinkle.science_engine import ScienceDomain, ScienceEngine, ScienceRequest, ScienceSolveRequest


def test_all_blueprint_science_modules_exist():
    modules = ScienceEngine().modules()
    assert {module.domain for module in modules} == {
        ScienceDomain.physics,
        ScienceDomain.chemistry,
        ScienceDomain.biology,
        ScienceDomain.materials_science,
        ScienceDomain.energy,
        ScienceDomain.astronomy,
    }


def test_science_request_preserves_boundary_without_inventing_answer():
    result = ScienceEngine().inspect(
        ScienceRequest(question="How does this work?", domain=ScienceDomain.physics)
    )
    assert result.status == "MODULE_READY"
    assert result.answer is None
    assert result.evidence_required is True
    assert result.module.status == "BOUNDARY_READY"

import pytest


def test_physics_kinematics_is_deterministic():
    result = ScienceEngine().solve(ScienceSolveRequest(
        domain=ScienceDomain.physics,
        problem="Find final velocity and displacement",
        model="kinematics_v1",
        inputs={"initial_velocity": 10, "acceleration": 2, "time": 5},
    ))
    assert result.status == "CALCULATED"
    assert result.calculation["outputs"]["final_velocity"] == 20
    assert result.calculation["outputs"]["displacement"] == 75


def test_chemistry_ideal_gas():
    result = ScienceEngine().solve(ScienceSolveRequest(
        domain=ScienceDomain.chemistry,
        problem="Ideal gas pressure",
        model="ideal_gas_v1",
        inputs={"moles": 1, "temperature_k": 273.15, "volume_m3": 0.022414},
    ))
    assert result.status == "CALCULATED"
    assert result.calculation["outputs"]["pressure_pa"] > 100000


def test_invalid_scientific_model_is_rejected():
    with pytest.raises(ValueError, match="Unsupported scientific model"):
        ScienceEngine().solve(ScienceSolveRequest(
            domain=ScienceDomain.physics,
            problem="x",
            model="made_up_model",
            inputs={},
        ))


def test_invalid_domain_input_is_rejected():
    with pytest.raises(ValueError):
        ScienceEngine().solve(ScienceSolveRequest(
            domain=ScienceDomain.energy,
            problem="power",
            model="power_v1",
            inputs={"energy_j": 10, "time_s": 0},
        ))

def test_physics_projectile_range():
    result = ScienceEngine().solve(ScienceSolveRequest(
        domain=ScienceDomain.physics,
        problem="Projectile range",
        model="projectile_range_v1",
        inputs={"initial_speed_m_s": 20, "launch_angle_deg": 45},
    ))
    assert result.status == "CALCULATED"
    assert 40.7 < result.calculation["outputs"]["range_m"] < 40.8


def test_physics_pendulum_period():
    result = ScienceEngine().solve(ScienceSolveRequest(
        domain=ScienceDomain.physics,
        problem="Pendulum period",
        model="pendulum_period_v1",
        inputs={"length_m": 1.0},
    ))
    assert abs(result.calculation["outputs"]["period_s"] - 2.006) < 0.01


def test_chemistry_ph():
    result = ScienceEngine().solve(ScienceSolveRequest(
        domain=ScienceDomain.chemistry,
        problem="pH from concentration",
        model="ph_v1",
        inputs={"hydrogen_ion_concentration_mol_l": 1e-4},
    ))
    assert result.calculation["outputs"]["ph"] == 4.0


def test_chemistry_dilution():
    result = ScienceEngine().solve(ScienceSolveRequest(
        domain=ScienceDomain.chemistry,
        problem="Dilution",
        model="dilution_v1",
        inputs={"initial_concentration": 2.0, "initial_volume": 0.5, "final_volume": 2.0},
    ))
    assert result.calculation["outputs"]["final_concentration"] == 0.5


def test_biology_logistic_growth_bounded_by_carrying_capacity():
    result = ScienceEngine().solve(ScienceSolveRequest(
        domain=ScienceDomain.biology,
        problem="Logistic growth",
        model="logistic_growth_v1",
        inputs={"carrying_capacity": 1000, "initial_population": 10, "growth_rate": 0.5, "time": 10},
    ))
    population = result.calculation["outputs"]["population"]
    assert 10 < population < 1000


def test_materials_thermal_expansion():
    result = ScienceEngine().solve(ScienceSolveRequest(
        domain=ScienceDomain.materials_science,
        problem="Thermal expansion",
        model="thermal_expansion_v1",
        inputs={"expansion_coefficient": 12e-6, "length_m": 2.0, "delta_temperature_k": 50},
    ))
    assert abs(result.calculation["outputs"]["delta_length_m"] - 0.0012) < 1e-9


def test_energy_potential_and_heat():
    pe = ScienceEngine().solve(ScienceSolveRequest(
        domain=ScienceDomain.energy, problem="PE", model="potential_energy_v1",
        inputs={"mass_kg": 5, "height_m": 10},
    ))
    assert abs(pe.calculation["outputs"]["potential_energy_j"] - 490.5) < 0.01

    heat = ScienceEngine().solve(ScienceSolveRequest(
        domain=ScienceDomain.energy, problem="Q", model="heat_energy_v1",
        inputs={"mass_kg": 2, "specific_heat_j_per_kgk": 4186, "delta_temperature_k": 10},
    ))
    assert heat.calculation["outputs"]["heat_energy_j"] == 83720.0


def test_astronomy_escape_velocity_matches_earth():
    result = ScienceEngine().solve(ScienceSolveRequest(
        domain=ScienceDomain.astronomy, problem="Escape velocity", model="escape_velocity_v1",
        inputs={"central_mass_kg": 5.972e24, "radius_m": 6.371e6},
    ))
    # Earth's real escape velocity is ~11186 m/s
    assert abs(result.calculation["outputs"]["escape_velocity_m_s"] - 11186) < 5
