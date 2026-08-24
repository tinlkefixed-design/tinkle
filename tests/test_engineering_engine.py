from tinkle.engineering_engine import EngineeringDomain, EngineeringEngine, EngineeringRequest


def test_all_blueprint_engineering_modules_exist():
    modules = EngineeringEngine().modules()
    assert {module.domain for module in modules} == {
        EngineeringDomain.mechanical_engineering,
        EngineeringDomain.electrical_engineering,
        EngineeringDomain.electronics,
        EngineeringDomain.robotics,
        EngineeringDomain.control_systems,
        EngineeringDomain.thermal_engineering,
        EngineeringDomain.materials_engineering,
        EngineeringDomain.energy_systems,
        EngineeringDomain.software_engineering,
    }


def test_engineering_boundary_does_not_invent_solution():
    result = EngineeringEngine().inspect(
        EngineeringRequest(
            problem="Design a system",
            domain=EngineeringDomain.robotics,
        )
    )
    assert result.status == "MODULE_READY"
    assert result.solution is None
    assert result.module.status == "BOUNDARY_READY"
    assert result.requirements == []
    assert result.limitations
from tinkle.engineering_engine import (
    EngineeringDomain,
    EngineeringEngine,
    EngineeringRequest,
    EngineeringSolveRequest,
)
import pytest


def test_electrical_ohms_law_solves_for_missing_quantity():
    result = EngineeringEngine().solve(EngineeringSolveRequest(
        problem="Find current", domain=EngineeringDomain.electrical_engineering,
        model="ohms_law_v1", inputs={"voltage_v": 12, "resistance_ohm": 6},
    ))
    assert result.status == "CALCULATED"
    assert result.calculation["outputs"]["current_a"] == 2


def test_mechanical_beam_deflection():
    result = EngineeringEngine().solve(EngineeringSolveRequest(
        problem="Central-load beam deflection", domain=EngineeringDomain.mechanical_engineering,
        model="beam_deflection_v1",
        inputs={"force_n": 1000, "length_m": 2, "elastic_modulus_pa": 200e9, "moment_of_inertia_m4": 8e-6},
    ))
    assert result.calculation["outputs"]["deflection_m"] > 0


def test_electrical_capacitor_energy():
    result = EngineeringEngine().solve(EngineeringSolveRequest(
        problem="Stored energy", domain=EngineeringDomain.electrical_engineering,
        model="capacitor_energy_v1", inputs={"capacitance_f": 100e-6, "voltage_v": 12},
    ))
    assert abs(result.calculation["outputs"]["energy_j"] - 0.0072) < 1e-9


def test_electronics_voltage_divider():
    result = EngineeringEngine().solve(EngineeringSolveRequest(
        problem="Divider output", domain=EngineeringDomain.electronics,
        model="voltage_divider_v1", inputs={"input_voltage_v": 12, "resistance1_ohm": 1000, "resistance2_ohm": 2000},
    ))
    assert result.calculation["outputs"]["output_voltage_v"] == 8


def test_robotics_torque():
    result = EngineeringEngine().solve(EngineeringSolveRequest(
        problem="Applied torque", domain=EngineeringDomain.robotics,
        model="torque_v1", inputs={"force_n": 50, "radius_m": 0.3, "angle_deg": 90},
    ))
    assert result.calculation["outputs"]["torque_n_m"] == 15


def test_control_systems_natural_frequency_and_damping():
    result = EngineeringEngine().solve(EngineeringSolveRequest(
        problem="Mass-spring-damper", domain=EngineeringDomain.control_systems,
        model="second_order_natural_frequency_v1",
        inputs={"stiffness_n_per_m": 4000, "mass_kg": 10, "damping_n_s_per_m": 80},
    ))
    assert result.calculation["outputs"]["natural_frequency_rad_s"] == 20
    assert abs(result.calculation["outputs"]["damping_ratio"] - 0.2) < 1e-9


def test_thermal_convection():
    result = EngineeringEngine().solve(EngineeringSolveRequest(
        problem="Convective heat loss", domain=EngineeringDomain.thermal_engineering,
        model="convection_v1", inputs={"convection_coefficient_w_m2k": 25, "area_m2": 2, "delta_temperature_k": 30},
    ))
    assert result.calculation["outputs"]["heat_rate_w"] == 1500


def test_materials_thermal_expansion():
    result = EngineeringEngine().solve(EngineeringSolveRequest(
        problem="Rod expansion", domain=EngineeringDomain.materials_engineering,
        model="thermal_expansion_v1", inputs={"expansion_coefficient": 12e-6, "length_m": 2, "delta_temperature_k": 50},
    ))
    assert abs(result.calculation["outputs"]["delta_length_m"] - 0.0012) < 1e-9


def test_energy_systems_battery_capacity():
    result = EngineeringEngine().solve(EngineeringSolveRequest(
        problem="Battery energy", domain=EngineeringDomain.energy_systems,
        model="battery_capacity_v1", inputs={"amp_hours": 2.5, "voltage_v": 3.7},
    ))
    assert abs(result.calculation["outputs"]["energy_wh"] - 9.25) < 1e-9


def test_software_engineering_littles_law():
    result = EngineeringEngine().solve(EngineeringSolveRequest(
        problem="Items in system", domain=EngineeringDomain.software_engineering,
        model="littles_law_v1", inputs={"arrival_rate_per_s": 5, "average_wait_time_s": 2},
    ))
    assert result.calculation["outputs"]["average_items_in_system"] == 10


def test_invalid_engineering_model_is_rejected():
    with pytest.raises(ValueError, match="Unsupported engineering model"):
        EngineeringEngine().solve(EngineeringSolveRequest(
            problem="x", domain=EngineeringDomain.robotics, model="made_up_model", inputs={},
        ))
