from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
STEPS = ["scripts/generate_benchmark.py", "scripts/verify_benchmark.py", "scripts/reproduce_tables.py"]
for script in STEPS:
    print(f"\n=== {script} ===")
    subprocess.run([sys.executable, str(ROOT / script)], cwd=ROOT, check=True)
print("\nReproducibility pipeline completed: benchmark generation, integrity verification, and table reproduction.")