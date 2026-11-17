import csv
import hashlib
import statistics
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EXPECTED = {
    "legacy/experiment2_original/src/core.py": "7ea9cf1e9bcf878fbbc2011faed4cd0f16483c3ecef2b184c09bcc4fac516eca",
    "legacy/experiment2_original/src/provenance.py": "e5d07e5a8f1420699f3f969760bd6c32cedb0c14dedc06d87d0ec2710abc75be",
    "results/exp2/dual_lineage_compromise.csv": "8eaa6f1989dd347bb5f88d230b5cb0fbe0e094b7f3841cca7f2bc7a0267a0394",
    "results/exp2/trust_root_compromise.csv": "d100aaed6237a4b622b6a83a39e8a54fa6581d5eaf17a3f95c0d6708d54e1984",
    "results/exp2/dual_lineage_stochastic_summary.csv": "d9448bc2a7307f8070a349b3709940a76cb5d5a6d048356806815dbbba0a5e63",
    "results/exp2/dual_lineage_stochastic_per_seed.csv": "e6d1bc4042f052b61d3e7c675a1da5d786721e14f190738eb2c1c629fc7b27ae",
}


class RecoveredExperiment2ArchiveTests(unittest.TestCase):
    def test_recovered_file_hashes(self):
        for relative, expected in EXPECTED.items():
            with self.subTest(path=relative):
                actual = hashlib.sha256((ROOT / relative).read_bytes()).hexdigest()
                self.assertEqual(actual, expected)

    def test_dual_lineage_deterministic_table_has_original_seven_conditions(self):
        with (ROOT / "results/exp2/dual_lineage_compromise.csv").open(newline="") as handle:
            rows = {row["compromise"]: row for row in csv.DictReader(handle)}
        self.assertEqual(len(rows), 7)
        self.assertEqual(int(rows["both_lineage"]["unsafe_ACTs"]), 50)
        self.assertAlmostEqual(float(rows["both_lineage"]["ICAR_high"]), 0.1)
        self.assertEqual(int(rows["verifier_A"]["unsafe_ACTs"]), 0)

    def test_stochastic_summary_recomputes_from_original_per_seed_data(self):
        with (ROOT / "results/exp2/dual_lineage_stochastic_per_seed.csv").open(newline="") as handle:
            grouped = {}
            for row in csv.DictReader(handle):
                grouped.setdefault(row["compromise"], []).append(row)
        with (ROOT / "results/exp2/dual_lineage_stochastic_summary.csv").open(newline="") as handle:
            summary = {row["compromise"]: row for row in csv.DictReader(handle)}
        self.assertEqual(set(grouped), set(summary))
        for condition, rows in grouped.items():
            icar = [float(row["ICAR_high"]) for row in rows]
            act = [float(row["ACT_rate"]) for row in rows]
            self.assertEqual(len(rows), 30)
            self.assertAlmostEqual(statistics.mean(icar), float(summary[condition]["ICAR_mean"]), places=12)
            self.assertAlmostEqual(statistics.stdev(icar), float(summary[condition]["ICAR_sd"]), places=12)
            self.assertAlmostEqual(statistics.mean(act), float(summary[condition]["ACT_rate_mean"]), places=12)


if __name__ == "__main__":
    unittest.main()
