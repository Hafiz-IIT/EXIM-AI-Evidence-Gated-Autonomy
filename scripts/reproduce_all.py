from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
COMMANDS = [
    ("policy regression tests", [sys.executable, "-m", "unittest", "discover", "-s", "tests", "-v"]),
    ("benchmark generation", [sys.executable, str(ROOT / "scripts/generate_benchmark.py")]),
    ("benchmark integrity verification", [sys.executable, str(ROOT / "scripts/verify_benchmark.py")]),
    ("new transparent experiment reconstruction", [sys.executable, str(ROOT / "scripts/run_reconstruction_v1.py")]),
    ("loading existing historical publication tables", [sys.executable, str(ROOT / "scripts/reproduce_tables.py")]),
]

for label, command in COMMANDS:
    print(f"\n=== {label} ===")
    subprocess.run(command, cwd=ROOT, check=True)

print("\nStructural checks completed: policy tests, benchmark generation, integrity verification, and loading of existing result tables.")
print("Historical result CSVs are loaded unchanged. New reconstruction outputs are written separately under results/reconstruction_v1/.")
print("The new reconstruction uses explicit assumptions and is not a reproduction of the historical v1 numbers.")
