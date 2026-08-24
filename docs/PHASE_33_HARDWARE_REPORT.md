# Tinkle Phase 33 — Final Hardware Sizing Report

## Blueprint boundary
The Blueprint defines Phase 33 as **Final Hardware Sizing**, but it does not provide exact CPU/RAM/GPU/storage numbers. Therefore this report records explicit engineering recommendations and labels them as derived rather than Blueprint-mandated.

## Final sizing
### Current Tinkle runtime
- CPU: **2 logical cores minimum**
- RAM: **4 GB minimum**
- Storage: **5 GB minimum**
- GPU: **not required** for the current repository runtime

### Recommended development machine
- CPU: **8 logical cores**
- RAM: **16 GB**
- Storage: **512 GB SSD**
- GPU: **not required** for the current repository runtime

### Local-AI expansion
- CPU: **8 logical cores**
- RAM: **32 GB**
- Storage: **1 TB SSD**
- GPU: **12 GB VRAM recommended**

This tier is a derived recommendation only. The Blueprint names Local AI/Ollama but does not specify a particular model, so exact GPU sizing cannot be claimed from the source.

## Verification environment observed
- 3 logical CPUs
- 5.93 GiB RAM
- 37.72 GiB free disk
- x86_64 Linux

The verification host is an observation, **not** the production hardware recommendation.

## Hardware conclusion
The current Tinkle repository can be developed and run without a dedicated GPU. A dedicated GPU becomes relevant when the Local-AI expansion is actually populated with models whose memory requirements justify it.
