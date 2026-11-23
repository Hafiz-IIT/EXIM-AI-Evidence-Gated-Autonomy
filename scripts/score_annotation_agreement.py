"""Compute Krippendorff's alpha (nominal) for completed annotation CSVs."""
from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from pathlib import Path

FIELDS = (
    "evidence_sufficiency",
    "source_integrity",
    "document_freshness",
    "cross_document_consistency",
    "recommended_disposition",
)


def load_annotations(path):
    with Path(path).open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    if not rows:
        raise ValueError("Annotation file is empty")
    required = {"annotation_id", "annotator_id", *FIELDS}
    missing = required - set(rows[0])
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")
    seen = set()
    for row in rows:
        row["annotation_id"] = row["annotation_id"].strip()
        row["annotator_id"] = row["annotator_id"].strip()
        if not row["annotation_id"] or not row["annotator_id"]:
            raise ValueError("annotation_id and annotator_id must be non-empty")
        key = (row["annotation_id"], row["annotator_id"])
        if key in seen:
            raise ValueError(f"Duplicate annotation from same annotator: {key}")
        seen.add(key)
    return rows


def krippendorff_alpha_nominal(values_by_item):
    """Nominal Krippendorff alpha; supports variable numbers of ratings per item."""
    coincidence = Counter()
    category_counts = Counter()
    total_ratings = 0
    usable_items = 0
    pair_count = 0
    agreement_pairs = 0

    for ratings in values_by_item:
        ratings = [value for value in ratings if value not in (None, "")]
        n = len(ratings)
        if n < 2:
            continue
        usable_items += 1
        counts = Counter(ratings)
        total_ratings += n
        pair_count += n * (n - 1) // 2
        agreement_pairs += sum(count * (count - 1) // 2 for count in counts.values())
        category_counts.update(counts)
        for left, left_count in counts.items():
            for right, right_count in counts.items():
                if left == right:
                    coincidence[(left, right)] += left_count * (left_count - 1) / (n - 1)
                else:
                    coincidence[(left, right)] += left_count * right_count / (n - 1)

    if usable_items == 0 or total_ratings < 2:
        return {
            "alpha": None, "observed_agreement": None,
            "expected_disagreement": None, "usable_items": 0,
            "total_ratings": total_ratings,
        }

    total_coincidences = sum(coincidence.values())
    observed_disagreement = sum(
        count for (left, right), count in coincidence.items() if left != right
    ) / total_coincidences
    expected_disagreement = 1.0 - sum(
        (count / total_ratings) ** 2 for count in category_counts.values()
    )
    alpha = (
        None if expected_disagreement == 0
        else 1.0 - observed_disagreement / expected_disagreement
    )
    return {
        "alpha": alpha,
        "observed_agreement": agreement_pairs / pair_count if pair_count else None,
        "observed_disagreement": observed_disagreement,
        "expected_disagreement": expected_disagreement,
        "usable_items": usable_items,
        "total_ratings": total_ratings,
    }


def score_rows(rows):
    by_item = {}
    annotators = set()
    for row in rows:
        annotators.add(row["annotator_id"])
        by_item.setdefault(row["annotation_id"], []).append(row)
    result = {
        "annotators": sorted(annotators),
        "annotation_rows": len(rows),
        "unique_items": len(by_item),
        "fields": {},
    }
    for field in FIELDS:
        values = [
            [row[field].strip() for row in item_rows if row[field].strip()]
            for item_rows in by_item.values()
        ]
        result["fields"][field] = krippendorff_alpha_nominal(values)
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("annotations_csv")
    parser.add_argument("--output", default="agreement_summary.json")
    args = parser.parse_args()
    rows = load_annotations(args.annotations_csv)
    result = score_rows(rows)
    Path(args.output).write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
