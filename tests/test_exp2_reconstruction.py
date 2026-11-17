import csv
import json
import tempfile
import unittest
from pathlib import Path

from legacy.experiment2_reconstruction.controller import (
    build_decision_cache,
    build_deterministic_comparison,
    build_dual_lineage_comparison,
    build_trust_root_comparison,
    generate_attested_cases,
    reconstruct_experiment2,
)


ROOT = Path(__file__).resolve().parents[1]


class Experiment2ControllerReconstructionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.benchmark = [json.loads(line) for line in (ROOT / "data/benchmark/cases.jsonl").read_text().splitlines() if line.strip()]
        cls.v2_cases, cls.v3_cases = generate_attested_cases(cls.benchmark)

    def test_generated_attestation_case_sets_match_archived_hashes(self):
        import hashlib
        with tempfile.TemporaryDirectory() as temp:
            out = Path(temp)
            (out / "v2.jsonl").write_text("".join(json.dumps(x) + "\n" for x in self.v2_cases))
            (out / "v3.jsonl").write_text("".join(json.dumps(x) + "\n" for x in self.v3_cases))
            h2 = hashlib.sha256((out / "v2.jsonl").read_bytes()).hexdigest()
            h3 = hashlib.sha256((out / "v3.jsonl").read_bytes()).hexdigest()
        self.assertEqual(h2, "a8ca354e9186e77837605b824945144b688d050e6a16635d7cfa70340f82ad55")
        self.assertEqual(h3, "1ed049b216255250cbec37c7501f920a9d9f3ab86b830fec2d951c8b62e0ed00")

    def test_reconstructed_decision_cache_matches_original_hash(self):
        import hashlib
        cache = build_decision_cache(self.v3_cases)
        digest = hashlib.sha256(json.dumps(cache).encode()).hexdigest()
        self.assertEqual(digest, "7f59b47d7b62c1747897feef0cb1adc0f7e5c92f4b671b180ca3317a3c266c33")

    def test_reconstructed_2b_2d_2e_tables_match_archived_csvs(self):
        from legacy.experiment2_reconstruction.controller import csv_text
        det = csv_text(build_deterministic_comparison(self.v3_cases),
                       ["attack", "policy", "unsafe_ACTs", "ICAR_high", "ACT_rate", "ESCALATE_rate", "VERIFY_rate", "REQUEST_rate"])
        trust = csv_text(build_trust_root_comparison(self.v3_cases),
                         ["compromise", "unsafe_ACTs", "ICAR_high", "ACT_rate", "ESCALATE_rate", "VERIFY_rate", "REQUEST_rate"])
        lineage = csv_text(build_dual_lineage_comparison(self.v3_cases),
                           ["compromise", "unsafe_ACTs", "ICAR_high", "ACT_rate", "ESCALATE_rate"])
        self.assertEqual(det, (ROOT / "results/exp2/deterministic_attack_comparison.csv").read_text())
        self.assertEqual(trust, (ROOT / "results/exp2/trust_root_compromise.csv").read_text())
        self.assertEqual(lineage, (ROOT / "results/exp2/dual_lineage_compromise.csv").read_text())

    def test_full_reconstruction_manifest_is_exact(self):
        with tempfile.TemporaryDirectory() as temp:
            manifest = reconstruct_experiment2(
                ROOT / "data/benchmark/cases.jsonl",
                ROOT / "results/exp2",
                Path(temp) / "reconstructed",
            )
        self.assertEqual(manifest["status"], "exact_reconstruction_verified")
        self.assertEqual(manifest["high_risk_cases"], 500)
        self.assertTrue(all(manifest["result_table_exact_matches"].values()))


if __name__ == "__main__":
    unittest.main()
