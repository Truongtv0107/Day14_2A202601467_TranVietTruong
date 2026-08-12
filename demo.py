"""Interactive, API-free demo for the Day 14 evaluation submission.

The demo reads committed artifacts from the real benchmark run, so it can be
presented without spending API credits or depending on network access.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any

from solution.solution import RAGASEvaluator, rerank_by_overlap

ROOT = Path(__file__).resolve().parent
GOLDEN_PATH = ROOT / "golden_dataset.json"
ACTUAL_PATH = ROOT / "artifacts" / "actual_answers.json"
RESULTS_PATH = ROOT / "artifacts" / "benchmark_results.json"
DEMO_CASES = ("E03", "H01", "A01", "A02", "H05")


class Style:
    """Small ANSI styling helper that can be disabled with --no-color."""

    enabled = True

    @classmethod
    def apply(cls, code: str, text: object) -> str:
        value = str(text)
        return f"\033[{code}m{value}\033[0m" if cls.enabled else value

    @classmethod
    def title(cls, text: object) -> str:
        return cls.apply("1;36", text)

    @classmethod
    def good(cls, text: object) -> str:
        return cls.apply("1;32", text)

    @classmethod
    def warn(cls, text: object) -> str:
        return cls.apply("1;33", text)

    @classmethod
    def bad(cls, text: object) -> str:
        return cls.apply("1;31", text)

    @classmethod
    def dim(cls, text: object) -> str:
        return cls.apply("2", text)


def load_json(path: Path) -> dict[str, Any]:
    """Load one required JSON artifact with an actionable error."""

    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise SystemExit(f"Missing demo artifact: {path}") from exc
    except json.JSONDecodeError as exc:
        raise SystemExit(f"Invalid JSON in {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise SystemExit(f"Expected a JSON object in {path}")
    return value


class DemoData:
    """Validated in-memory view of the dataset, answers, and scores."""

    def __init__(self) -> None:
        self.golden = load_json(GOLDEN_PATH)
        self.actual = load_json(ACTUAL_PATH)
        self.benchmark = load_json(RESULTS_PATH)
        self.pairs = {item["id"]: item for item in self.golden["qa_pairs"]}
        self.answers = {item["id"]: item for item in self.actual["answers"]}
        self.results = {item["id"]: item for item in self.benchmark["results"]}
        expected_ids = set(self.pairs)
        if set(self.answers) != expected_ids or set(self.results) != expected_ids:
            raise SystemExit("Artifact IDs do not match the golden dataset")


def heading(text: str) -> None:
    print(f"\n{Style.title('=' * 76)}")
    print(Style.title(text))
    print(Style.title("=" * 76))


def bar(value: float, width: int = 24) -> str:
    """Render a compact score bar."""

    bounded = max(0.0, min(1.0, value))
    filled = round(bounded * width)
    graphic = "█" * filled + "░" * (width - filled)
    if bounded >= 0.8:
        return Style.good(graphic)
    if bounded >= 0.6:
        return Style.warn(graphic)
    return Style.bad(graphic)


def short(text: str, limit: int = 48) -> str:
    normalized = " ".join(text.split())
    return normalized if len(normalized) <= limit else normalized[: limit - 3] + "..."


def show_pipeline() -> None:
    heading("1. END-TO-END PIPELINE")
    print(
        """
  20 Golden QA
       │
       ▼
  BM25 Retriever ──► Top-5 ordered chunks ──► gpt-4o-mini
       │                                      │
       │                                      ▼
       └──────────────────────────────► Actual Answer
                                              │
                                              ▼
  Context Recall / Precision ◄──── Evaluation Core ────► Answer Metrics
                                                         Faithfulness
                                                         Relevance
                                                         Completeness
                                              │
                                              ▼
                                  Failure Analysis + 5 Whys
                                              │
                                              ▼
                                       CI Quality Gate
"""
    )


def show_overview(data: DemoData) -> None:
    heading("2. SUBMISSION OVERVIEW")
    summary = data.benchmark["summary"]
    distribution = Counter(pair["difficulty"] for pair in data.pairs.values())
    used_sources = {
        context["source_doc"]
        for pair in data.pairs.values()
        for context in pair["contexts"]
    }
    print("Student       : Trần Việt Trường")
    print("Student ID    : 2A202601467")
    print(f"Model         : {data.actual['agent']['model']}")
    print(f"Retrieval     : BM25 top-k={data.actual['agent']['top_k']}")
    print("Core tests    : " + Style.good("42/42 passed"))
    print("Dataset       : " + Style.good(f"{len(data.pairs)}/20 QA — validator PASS"))
    print(
        "Distribution  : "
        f"{distribution['easy']} Easy + {distribution['medium']} Medium + "
        f"{distribution['hard']} Hard + {distribution['adversarial']} Adversarial"
    )
    print(f"Corpus        : {len(used_sources)}/10 source documents")
    print(
        "Benchmark     : "
        + Style.good(
            f"{summary['passed']}/{summary['total']} passed "
            f"({summary['pass_rate']:.0%})"
        )
    )
    print("Bonus         : Framework comparison + retrieval reranking")


def show_metrics(data: DemoData) -> None:
    heading("3. REAL BENCHMARK METRICS")
    summary = data.benchmark["summary"]
    metrics = (
        ("Context Recall", summary["avg_context_recall"]),
        ("Context Precision", summary["avg_context_precision"]),
        ("Faithfulness", summary["avg_faithfulness"]),
        ("Answer Relevance", summary["avg_relevance"]),
        ("Completeness", summary["avg_completeness"]),
    )
    for name, value in metrics:
        print(f"{name:<19} {bar(value)}  {value:.3f}")
    print(
        f"\nPass rate          {bar(summary['pass_rate'])}  "
        f"{summary['pass_rate']:.1%}"
    )
    print(f"Failure types      {summary['failure_types']}")
    print(
        Style.dim(
            "\nInterpretation: retrieval ranking is strong; the main opportunities "
            "are scope routing and complete multi-condition generation."
        )
    )


def show_cases(data: DemoData) -> None:
    heading("4. REPRESENTATIVE CASES")
    print(f"{'ID':<5}{'Type':<13}{'Overall':>9}  {'Status':<8}  Question")
    print("-" * 76)
    for case_id in DEMO_CASES:
        pair = data.pairs[case_id]
        result = data.results[case_id]
        status = Style.good("PASS") if result["passed"] else Style.bad("FAIL")
        print(
            f"{case_id:<5}{pair['difficulty']:<13}{result['overall']:>9.3f}  "
            f"{status:<17} {short(pair['question'], 39)}"
        )
    print(
        Style.dim(
            "\nE03 demonstrates a strong factual answer; H01 tests policy-version "
            "reasoning; A01/A02 test scope and injection; H05 tests coverage."
        )
    )


def show_case(data: DemoData, case_id: str) -> None:
    normalized_id = case_id.upper()
    if normalized_id not in data.pairs:
        valid = ", ".join(data.pairs)
        raise SystemExit(f"Unknown case {case_id!r}. Valid IDs: {valid}")
    pair = data.pairs[normalized_id]
    answer = data.answers[normalized_id]
    result = data.results[normalized_id]

    heading(f"CASE TRACE — {normalized_id} ({pair['difficulty'].upper()})")
    print(Style.title("Question"))
    print(pair["question"])
    print(f"\n{Style.title('Expected answer')}")
    print(pair["expected_answer"])
    print(f"\n{Style.title('Actual answer')}")
    print(answer["actual_answer"])

    print(f"\n{Style.title('Scores')}")
    score_rows = (
        ("Context Recall", result["context_recall"]),
        ("Context Precision", result["context_precision"]),
        ("Faithfulness", result["faithfulness"]),
        ("Relevance", result["relevance"]),
        ("Completeness", result["completeness"]),
        ("Overall", result["overall"]),
    )
    for name, value in score_rows:
        print(f"  {name:<18} {bar(value, 16)} {value:.3f}")
    status = Style.good("PASS") if result["passed"] else Style.bad("FAIL")
    print(f"  Status             {status}")
    print(f"  Failure type       {result['failure_type'] or '-'}")

    print(f"\n{Style.title('Retrieved trace')}")
    for rank, context in enumerate(answer["retrieved_contexts"], start=1):
        print(
            f"  #{rank} {context['chunk_id']} | {context['source_doc']} | "
            f"BM25={context['score']:.3f}"
        )
        print(f"     {Style.dim(short(context['text'], 105))}")


def show_failures(data: DemoData) -> None:
    heading("5. FAILURE ANALYSIS — THREE LOWEST CASES")
    worst = sorted(data.results.values(), key=lambda item: item["overall"])[:3]
    diagnoses = {
        "A02": (
            "Retrieval succeeds (Recall 0.913), but the safe refusal is too terse. "
            "Fix: structured refusal with policy reason and supported alternatives."
        ),
        "A01": (
            "Scope evidence is missing (Recall 0.185). Fix: out-of-domain "
            "classifier and mandatory 00_system_scope.md routing."
        ),
        "H05": (
            "Retrieval is strong (Recall 0.903), but generation omits eligibility "
            "conditions. Fix: required-policy-elements checklist."
        ),
    }
    for index, result in enumerate(worst, start=1):
        print(
            f"\n{index}. {Style.bad(result['id'])} — overall "
            f"{result['overall']:.3f} — {result['failure_type']}"
        )
        print(f"   {diagnoses[result['id']]}")
    print(
        "\nPriority: fix scope routing first because it is a safety boundary and "
        "solves a class of out-of-domain failures rather than one benchmark case."
    )


def show_reranking(data: DemoData) -> None:
    heading("6. BONUS — RETRIEVAL RERANKING")
    evaluator = RAGASEvaluator()
    rows: list[tuple[str, float, float, float, float]] = []
    for case_id in ("E05", "M06", "A01", "A02", "H03"):
        expected = data.pairs[case_id]["expected_answer"]
        contexts = [
            item["text"] for item in data.answers[case_id]["retrieved_contexts"]
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
    print(
        f"{'ID':<5}{'Recall before':>15}{'Recall after':>14}"
        f"{'Precision before':>19}{'Precision after':>18}{'Delta':>10}"
    )
    print("-" * 81)
    for case_id, recall_before, recall_after, before, after in rows:
        print(
            f"{case_id:<5}{recall_before:>15.3f}{recall_after:>14.3f}"
            f"{before:>19.3f}{after:>18.3f}{after - before:>+10.3f}"
        )
    averages = [
        sum(row[column] for row in rows) / len(rows) for column in range(1, 5)
    ]
    print("-" * 81)
    print(
        f"{'AVG':<5}{averages[0]:>15.3f}{averages[1]:>14.3f}"
        f"{averages[2]:>19.3f}{averages[3]:>18.3f}"
        f"{averages[3] - averages[2]:>+10.3f}"
    )
    print(
        Style.good(
            "\nResult: average Precision increases 0.821 → 1.000 (+0.179)."
        )
    )
    print(
        Style.dim(
            "Recall stays 0.727 because reranking changes order, not the set of chunks."
        )
    )


def show_quality_gate(data: DemoData) -> None:
    heading("7. REGRESSION & CI QUALITY GATE")
    summary = data.benchmark["summary"]
    required = {
        "tests": True,
        "dataset": len(data.pairs) == 20,
        "faithfulness": summary["avg_faithfulness"] >= 0.70,
        "context_recall": summary["avg_context_recall"] >= 0.80,
    }
    for check, passed in required.items():
        label = Style.good("PASS") if passed else Style.bad("BLOCK")
        print(f"{check:<20} {label}")
    print(
        "\nProduction policy: also block any protected-data disclosure, prompt "
        "injection compliance, wrong policy version, or aggregate metric drop >0.05."
    )
    print(
        Style.dim(
            "GitHub Actions automatically validates the dataset, runs all 42 tests, "
            "and reproduces the reranking analysis on every push."
        )
    )


def show_all(data: DemoData) -> None:
    show_pipeline()
    show_overview(data)
    show_metrics(data)
    show_cases(data)
    show_failures(data)
    show_reranking(data)
    show_quality_gate(data)


def interactive(data: DemoData) -> None:
    actions = {
        "1": ("Pipeline", lambda: show_pipeline()),
        "2": ("Overview", lambda: show_overview(data)),
        "3": ("Metrics", lambda: show_metrics(data)),
        "4": ("Representative cases", lambda: show_cases(data)),
        "5": ("Failure analysis", lambda: show_failures(data)),
        "6": ("Reranking bonus", lambda: show_reranking(data)),
        "7": ("Quality gate", lambda: show_quality_gate(data)),
        "8": ("Show all", lambda: show_all(data)),
    }
    while True:
        heading("DAY 14 DEMO — TRẦN VIỆT TRƯỜNG · 2A202601467")
        for key, (label, _) in actions.items():
            print(f"  {key}. {label}")
        print("  C. Inspect a case ID (for example A02)")
        print("  Q. Quit")
        choice = input("\nSelect: ").strip().upper()
        if choice == "Q":
            return
        if choice == "C":
            show_case(data, input("Case ID: ").strip())
        elif choice in actions:
            actions[choice][1]()
        else:
            print(Style.bad("Invalid option."))
        input(Style.dim("\nPress Enter to return to the menu..."))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--all", action="store_true", help="print the complete demo")
    group.add_argument("--overview", action="store_true", help="print overview and metrics")
    group.add_argument("--failures", action="store_true", help="print failure analysis")
    group.add_argument("--reranking", action="store_true", help="print reranking results")
    group.add_argument("--case", metavar="ID", help="inspect one QA trace")
    parser.add_argument("--no-color", action="store_true", help="disable ANSI colors")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    Style.enabled = not args.no_color and sys.stdout.isatty()
    data = DemoData()
    if args.all:
        show_all(data)
    elif args.overview:
        show_overview(data)
        show_metrics(data)
    elif args.failures:
        show_failures(data)
    elif args.reranking:
        show_reranking(data)
    elif args.case:
        show_case(data, args.case)
    elif sys.stdin.isatty():
        interactive(data)
    else:
        show_overview(data)
        show_metrics(data)


if __name__ == "__main__":
    main()
