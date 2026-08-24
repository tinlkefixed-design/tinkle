# Tinkle — PHASE 50.17 Hardware Sizing

## Status

**COMPLETE as a sizing gate; final purchase remains conditional on production-model measurements.**

## Measured execution environment

The supplied v2.44.0 source tree was executed on the current Linux runner. The repository test suite passed and Python compilation passed. The runner exposed 3 logical CPUs, about 5.93 GiB RAM and about 37.68 GiB free disk. GPU/VRAM was not observed because `nvidia-smi` is unavailable in this environment.

These are measurements of the test runner, **not** the user's future production machine.

## Recommended workstation target

- 16 logical CPU threads or better
- 64 GB RAM
- 2 TB NVMe SSD
- 24 GB VRAM minimum for a serious local-AI workstation target
- Linux/Ubuntu 24.04 LTS

This target is intentionally a practical baseline rather than a claim that every model fits. Ollama's current documentation shows GPU support across modern NVIDIA families and explains that concurrent model loading depends on available VRAM; its FAQ also notes that parallel requests increase context-related memory use. citeturn0search0turn0search1

## Local-model tiers

Approximate planning tiers:

| Workload | VRAM target | System RAM |
|---|---:|---:|
| 7–8B quantized | 8–12 GB | 32 GB |
| 13–14B quantized | 16–24 GB | 64 GB |
| 70B quantized | 40+ GB | 128 GB |

The 70B tier is a server/multi-GPU class workload rather than the recommended single-workstation baseline. Published Ollama guidance confirms that model size and concurrency materially affect GPU memory requirements. citeturn0search1

## What is NOT honestly final yet

The following were not measurable in the supplied execution environment:

- exact local model(s) and quantization
- production context lengths
- concurrent local-model requests
- live PostgreSQL/Redis/Qdrant workload
- production simulation workload
- real GPU/VRAM utilization

Therefore, **50.17 does not invent a fake exact GPU requirement**. The recommended 24-GB target is a planning target; the purchase specification must be re-run after the exact production model set is selected.

## Hardware decision rule

`Production models + context + concurrency + retrieval corpus + databases + simulation`  
`→ measure CPU/RAM/VRAM/storage`  
`→ add safety headroom`  
`→ approve final hardware.

## Important distinction

Completing Phase 50.17 does **not** turn the remaining 29 Blueprint `PARTIAL` items into PASS. Hardware sizing is a separate release gate. The Release Candidate remains blocked until those implementation gaps are actually closed.
