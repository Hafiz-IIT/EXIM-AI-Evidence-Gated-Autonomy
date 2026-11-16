from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
COMMANDS = [
    ("policy regression tests", [sys.executable, "-m", "unittest", "discover", "-s", "tests", "-v"]),
    ("benchmark generation", [sys.executable, str(ROOT / "scripts/generate_benchmark.py")]),
    ("benchmark integrity verification", [sys.executable, str(ROOT / "scripts/verify_benchmark.py")]),
    ("new transparent experiment reconstruction v1 on benchmark v0.3", [sys.executable, str(ROOT / "scripts/run_reconstruction_v1.py")]),
    ("benchmark v0.4 generation", [sys.executable, str(ROOT / "scripts/generate_benchmark_v04.py")]),
    ("benchmark v0.4 integrity verification", [sys.executable, str(ROOT / "scripts/verify_benchmark_v04.py")]),
    ("benchmark v0.4 reconstruction and sensitivity analysis", [sys.executable, str(ROOT / "scripts/run_reconstruction_v2.py")]),
    ("document-root attestation threat experiments", [sys.executable, str(ROOT / "scripts/run_document_root_attestation.py")]),
    ("loading existing historical publication tables", [sys.executable, str(ROOT / "scripts/reproduce_tables.py")]),
]

for label, command in COMMANDS:
    print(f"\n=== {label} ===")
    subprocess.run(command, cwd=ROOT, check=True)

print("\nStructural checks completed: regression tests, v0.3 and v0.4 benchmark generation/verification, both reconstruction suites, sensitivity analysis, document-root attestation threat experiments, and historical table loading.")
print("Historical result CSVs are loaded unchanged. Reconstruction v1 and v2 outputs are stored separately.")
print("Both reconstructions use newly stated assumptions and are not reproductions of the historical result tables.")
