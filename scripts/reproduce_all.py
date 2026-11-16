from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
COMMANDS = [
    ("policy regression tests", [sys.executable, "-m", "unittest", "discover", "-s", "tests", "-v"]),
    ("benchmark generation", [sys.executable, str(ROOT / "scripts/generate_benchmark.py")]),
    ("benchmark integrity verification", [sys.executable, str(ROOT / "scripts/verify_benchmark.py")]),
    ("loading existing publication tables", [sys.executable, str(ROOT / "scripts/reproduce_tables.py")]),
]

for label, command in COMMANDS:
    print(f"\n=== {label} ===")
    subprocess.run(command, cwd=ROOT, check=True)

print("\nStructural checks completed: policy tests, benchmark generation, integrity verification, and loading of existing result tables.")
print("NOTE: this command does not rerun the stochastic, OOD, provenance-attack, trust-root, or separation-of-duties experiments.")
