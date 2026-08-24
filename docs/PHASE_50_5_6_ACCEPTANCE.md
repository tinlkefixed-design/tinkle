# Tinkle — PHASE 50.5–50.6 Acceptance

## PHASE 50.5 — Knowledge ingestion and retrieval
- Supported parsers: TXT, Markdown, CSV, PDF, DOCX, XLSX/XLSM.
- Normalized source metadata and parser metadata.
- Deterministic bounded chunking.
- BM25 lexical retrieval baseline.
- Project-scoped filtering preserved.
- Retrieval is explicitly labeled lexical; it is not represented as an embedding model.

## PHASE 50.6 — External research provider
- Provider interface remains injectable.
- Built-in no-key DuckDuckGo HTML adapter is available.
- External results are marked as external leads.
- Provider failures are captured as explicit limitations and never converted into evidence.
- Provenance/verification remains separate from search retrieval.

## Verification
- Full pytest suite: PASS.
- Python compilation: PASS.
- Ruff: NOT VERIFIED in this runtime because the executable is unavailable.
- mypy: NOT VERIFIED in this runtime because the executable is unavailable.
- Live external web connectivity: NOT VERIFIED in this runtime because outbound DNS/network is unavailable.

## Not claimed
- Qdrant/vector embeddings are not claimed as complete until a real backend is installed and integration-tested.
- Live web search is not claimed as successfully exercised in this offline runtime.
