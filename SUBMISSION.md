# Day 14 Submission

| Field | Value |
|---|---|
| Student | Trần Việt Trường |
| Student ID | 2A202601467 |
| Topic | AI Evaluation & Benchmarking Pipeline |
| Core tests | 42/42 passed |
| Golden dataset | PASS — 20 QA, 10/10 source documents |
| Real benchmark | 20 actual answers, 80.0% pass rate |
| Bonus | Framework comparison and retrieval reranking |

## Live demo

**https://truongtv0107.github.io/Day14_2A202601467_TranVietTruong/**

## Deliverables

- `solution/solution.py`: completed typed evaluation core.
- `golden_dataset.json`: 5 Easy + 7 Medium + 5 Hard + 3 Adversarial.
- `exercises.md`: worksheet, real benchmark, judge rubric, and both bonuses.
- `reflection.md`: trace-backed failure analysis, three 5 Whys, improvement
  log, regression strategy, and continuous-improvement plan.
- `artifacts/`: auditable generated answers and benchmark output. No API key
  or `.env` is stored.
- `demo.py` and `DEMO_GUIDE.md`: API-free interactive mentor demo and
  five-minute presentation script.

## Reproduce

```bash
python validate_golden_dataset.py
python -m pytest tests/ -v
python evaluate_answers.py
PYTHONPATH=. python scripts/analyze_reranking.py
python demo.py --all
```

Regenerating `artifacts/actual_answers.json` requires a local
`OPENAI_API_KEY` and `OPENAI_MODEL`; secrets must not be committed.
