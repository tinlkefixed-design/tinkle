from __future__ import annotations
import hashlib, json, re, subprocess, sys
from pathlib import Path
from tinkle.core.blueprint_audit import build_audit
from tinkle.core.code_quality import run_quality_gate

ROOT = Path(__file__).resolve().parent

def tree_hash():
    h = hashlib.sha256()
    for p in sorted(ROOT.rglob('*')):
        if p.is_file() and '.git' not in p.parts and '__pycache__' not in p.parts and p.name != 'RELEASE_CANDIDATE_MANIFEST.json':
            h.update(str(p.relative_to(ROOT)).encode()); h.update(p.read_bytes())
    return h.hexdigest()

def collect_count():
    import pytest
    class Plugin:
        count = 0
        def pytest_collection_finish(self, session):
            self.count = len(session.items)
    plugin = Plugin()
    rc = pytest.main(['--collect-only', '-q'], plugins=[plugin])
    return plugin.count, rc

def main():
    collected, collect_rc = collect_count()
    tests = subprocess.run([sys.executable, '-m', 'pytest', '-q'], cwd=ROOT, text=True, capture_output=True, timeout=300)
    passed = tests.returncode == 0
    audit = build_audit(); quality = run_quality_gate()
    manifest = {
        'product': 'Tinkle', 'candidate_version': 'v2.44.0',
        'phase': '50.16', 'phase_name': 'Release Candidate',
        'base_version': 'v2.44.0', 'completed_subphases': [f'50.{i}' for i in range(1,17)],
        'stress_regression': {'phase': '50.15', 'pytest_passed': passed},
        'tests': {'collected': collected, 'collection_returncode': collect_rc, 'suite_returncode': tests.returncode, 'suite_passed': passed},
        'blueprint_audit': {'total': audit['total_items'], 'pass': audit['counts']['PASS'], 'partial': audit['counts']['PARTIAL'], 'not_verified': audit['counts']['NOT_VERIFIED']},
        'quality_gate': quality,
        'release_ready': bool(passed and audit['release_ready'] and quality['overall'] == 'PASS'),
        'status': 'BLOCKED' if not (passed and audit['release_ready'] and quality['overall'] == 'PASS') else 'READY_FOR_FINAL_RELEASE',
        'blocking_reasons': audit['blocking_summary'] + ([] if quality['overall'] == 'PASS' else ['Code quality gate is not fully verified in this environment.']),
        'source_tree_sha256': tree_hash(),
    }
    (ROOT/'RELEASE_CANDIDATE_MANIFEST.json').write_text(json.dumps(manifest, indent=2, ensure_ascii=False)+'\n', encoding='utf-8')
    (ROOT/'docs'/'PHASE_50_15_16_RESULTS.json').write_text(json.dumps(manifest, indent=2, ensure_ascii=False)+'\n', encoding='utf-8')
    print(json.dumps(manifest, indent=2, ensure_ascii=False))
    return 0 if passed else 1

if __name__ == '__main__': raise SystemExit(main())
