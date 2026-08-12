"""Reproduce Exercise 3.5 retrieval-reranking measurements."""

from __future__ import annotations

import json
from pathlib import Path

from template import RAGASEvaluator, rerank_by_overlap

ROOT = Path(__file__).resolve().parents[1]
CASE_IDS = ("E05", "M06", "A01", "A02", "H03")


def main() -> None:
    golden = json.loads((ROOT / "golden_dataset.json").read_text(encoding="utf-8"))
    actual = json.loads(
        (ROOT / "artifacts/actual_answers.json").read_text(encoding="utf-8")
    )
    pairs = {pair["id"]: pair for pair in golden["qa_pairs"]}
    answers = {answer["id"]: answer for answer in actual["answers"]}
    evaluator = RAGASEvaluator()
    rows: list[tuple[str, float, float, float, float]] = []

    for case_id in CASE_IDS:
        expected = pairs[case_id]["expected_answer"]
        contexts = [
            context["text"] for context in answers[case_id]["retrieved_contexts"]
        ]
        reranked = rerank_by_overlap(contexts, expected)
        rows.append(
            (
                case_id,
                evaluator.evaluate_context_recall(contexts, expected),
                evaluator.evaluate_context_recall(reranked, expected),
                evaluator.evaluate_context_precision(contexts, expected),
                evaluator.evaluate_context_precision(reranked, expected),
            )
        )

    print("| ID | Recall before | Recall after | Precision before | Precision after | Delta |")
    print("|---|---:|---:|---:|---:|---:|")
    for case_id, recall_before, recall_after, precision_before, precision_after in rows:
        print(
            f"| {case_id} | {recall_before:.3f} | {recall_after:.3f} | "
            f"{precision_before:.3f} | {precision_after:.3f} | "
            f"{precision_after - precision_before:+.3f} |"
        )
    averages = [
        sum(row[column] for row in rows) / len(rows) for column in range(1, 5)
    ]
    print(
        f"| **Avg** | {averages[0]:.3f} | {averages[1]:.3f} | "
        f"{averages[2]:.3f} | {averages[3]:.3f} | "
        f"{averages[3] - averages[2]:+.3f} |"
    )


if __name__ == "__main__":
    main()
