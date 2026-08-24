from __future__ import annotations

import os
import platform
import shutil
from pathlib import Path


def _ram_gb() -> float | None:
    try:
        with open("/proc/meminfo", encoding="utf-8") as fh:
            for line in fh:
                if line.startswith("MemTotal:"):
                    return round(int(line.split()[1]) / 1024 / 1024, 2)
    except (OSError, ValueError):
        return None
    return None


def _gpu_observation() -> dict[str, object]:
    # We intentionally do not infer GPU/VRAM from software packages.
    # A missing nvidia-smi means "not observed", not "no GPU exists".
    import shutil as _shutil
    nvidia_smi = _shutil.which("nvidia-smi")
    if not nvidia_smi:
        return {"observed": False, "reason": "nvidia-smi unavailable; GPU/VRAM not measured in this environment."}
    return {"observed": True, "nvidia_smi": nvidia_smi}


def build_hardware_sizing() -> dict[str, object]:
    cpu = os.cpu_count() or 1
    ram = _ram_gb()
    free_disk = round(shutil.disk_usage("/").free / 1024**3, 2)
    return {
        "phase": 33,
        "current_phase": "50.17",
        "status": "sized",
        "phase_50_17_status": "sized_with_constraints",
        "observed_host": {
            "cpu_logical": cpu,
            "ram_gb": ram,
            "free_disk_gb": free_disk,
            "machine": platform.machine(),
            "platform": platform.platform(),
            "gpu": _gpu_observation(),
        },
        "tiers": {
            "current_tinkle_runtime": {
                "cpu_logical_min": 2,
                "ram_gb_min": 4,
                "storage_gb_min": 5,
                "gpu_required": False,
                "basis": "Legacy orchestration/UI runtime tier; external/local AI model execution is not assumed.",
            },
            "recommended_development": {
                "cpu_logical": 8,
                "ram_gb": 16,
                "storage_gb": 512,
                "gpu_required": False,
                "basis": "Development headroom tier.",
            },
            "local_ai_expansion": {
                "cpu_logical": 8,
                "ram_gb": 32,
                "storage_gb": 1000,
                "gpu_vram_gb": 12,
                "gpu_required": True,
                "basis": "Entry local-AI expansion tier; exact model selection may require more VRAM.",
            },
        },
        "constraints": [
            "The Blueprint does not specify one exact hardware configuration.",
            "GPU sizing depends on the selected local model(s), quantization, context length and concurrency.",
            "Production database and simulation workloads were not available in this runner for final measurement.",
        ],
        "measured_application_gate": {
            "pytest_suite": "PASS",
            "python_compile": "PASS",
            "local_model_workload": "NOT_MEASURED",
            "production_database_workload": "NOT_MEASURED",
            "real_simulation_workload": "NOT_MEASURED",
            "reason": "The current execution environment does not contain the production local model set, live PostgreSQL/Redis/Qdrant deployment, or production simulation workload. A final numeric GPU requirement cannot honestly be inferred from code alone.",
        },
        "recommended_target": {
            "cpu_logical": 16,
            "ram_gb": 64,
            "storage_gb_nvme": 2000,
            "gpu_vram_gb": 24,
            "gpu_required": True,
            "purpose": "Practical single-workstation target for Tinkle development plus local AI, retrieval, concurrent agents and moderate scientific workloads.",
            "caveat": "This is the recommended target, not a claim that every possible local model or 70B-class workload fits. Larger models may require 40GB+ VRAM or multiple GPUs.",
        },
        "minimum_non_local_runtime": {
            "cpu_logical": 8,
            "ram_gb": 16,
            "storage_gb_nvme": 512,
            "gpu_required": False,
            "purpose": "Tinkle orchestration/API/UI with cloud models and without heavy local inference.",
        },
        "local_ai_tiers": {
            "small_7_8b_quantized": {"vram_gb_target": "8-12", "ram_gb": 32},
            "medium_13_14b_quantized": {"vram_gb_target": "16-24", "ram_gb": 64},
            "large_70b_quantized": {"vram_gb_target": "40+", "ram_gb": 128, "note": "Often a multi-GPU/server-class workload; not the baseline workstation target."},
        },
        "finalization_rule": "Before purchasing hardware, rerun the sizing suite with the exact local models, context lengths, concurrency, retrieval corpus, databases and simulation workloads selected for production. The hardware is final only when those measurements fit the target with safety headroom.",
    }
