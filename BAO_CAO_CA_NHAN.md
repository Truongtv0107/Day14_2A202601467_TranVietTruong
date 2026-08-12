# Báo cáo cá nhân — Day 14 AI Evaluation

## 1. Thông tin học viên

| Nội dung | Thông tin |
|---|---|
| Họ và tên | Trần Việt Trường |
| Mã học viên | 2A202601467 |
| Tài khoản GitHub | Truongtv0107 |
| Bài tập | AI Evaluation & Benchmarking Pipeline |
| Repo cá nhân | `Day14_2A202601467_TranVietTruong` |

## 2. Phạm vi công việc đã hoàn thành

Tôi đã hoàn thiện toàn bộ pipeline đánh giá AI cho trợ lý Northstar University
Student Services:

1. Xây dựng `QAPair`, `EvalResult` và cách tính overall score.
2. Triển khai Faithfulness, Answer Relevance, Completeness, Context Recall và
   rank-aware Context Precision.
3. Nối retrieval trace vào full evaluation và benchmark runner.
4. Triển khai LLM-as-a-Judge, parse score và kiểm tra positional, leniency,
   severity bias.
5. Xây dựng report aggregation, regression gate và failure filtering.
6. Triển khai failure taxonomy, root-cause analysis, improvement suggestions và
   improvement log.
7. Xây dựng golden dataset 20 câu từ đúng corpus được cấp.
8. Chạy RAG thật với `gpt-4o-mini` trên 20 câu, lưu answer và retrieval trace.
9. Phân tích ba failure thấp nhất bằng 5 Whys.
10. Hoàn thành hai bài bonus: framework comparison và retrieval reranking.
11. Thêm GitHub Actions quality gate để tự động chạy validator, tests và bonus.

## 3. Kết quả kiểm thử

| Hạng mục | Kết quả |
|---|---|
| Unit tests | **42/42 passed** |
| Golden dataset validator | **PASS** |
| Số QA | **20/20** |
| Phân tầng | **5 Easy + 7 Medium + 5 Hard + 3 Adversarial** |
| Corpus coverage | **10/10 source documents** |
| Actual RAG answers | **20/20, không có lỗi API** |

Các lệnh tái lập:

```bash
python validate_golden_dataset.py
python -m pytest tests/ -v
python evaluate_answers.py
PYTHONPATH=. python scripts/analyze_reranking.py
```

## 4. Kết quả benchmark thật

| Metric | Average |
|---|---:|
| Context Recall | 0.870 |
| Context Precision | 0.955 |
| Faithfulness | 0.744 |
| Answer Relevance | 0.672 |
| Completeness | 0.664 |
| Overall pass rate | **80.0% (16/20)** |

Failure distribution gồm 2 `off_topic` và 2 `hallucination`. Ba case thấp
nhất:

1. **A02 — 0.098:** retrieval đúng safety rule nhưng model từ chối quá ngắn.
2. **A01 — 0.330:** lexical retriever không lấy được scope policy cho câu hỏi
   đầu tư ngoài domain.
3. **H05 — 0.594:** câu trả lời đúng phần chính nhưng thiếu một số điều kiện
   graduation và bị word-overlap đánh giá thấp.

Kết luận: Context Precision cao cho thấy thứ tự chunk nhìn chung tốt. Hai vấn đề
chính là scope-aware retrieval và structured generation cho refusal/câu hỏi
nhiều điều kiện.

## 5. Failure analysis và cải tiến

Ba root cause chính:

- Chưa có scope classifier để định tuyến câu hỏi ngoài domain tới
  `00_system_scope.md`.
- Chưa có structured refusal template yêu cầu lý do, quy tắc bảo mật và nhóm
  chủ đề được hỗ trợ.
- Chưa có required-elements checklist cho câu hỏi có nhiều điều kiện, ngày,
  mức phí và ngoại lệ.

Ưu tiên cải tiến:

1. Scope classifier + mandatory scope chunk cho out-of-domain intent.
2. Structured refusal và policy-element coverage checklist.
3. Human-calibrated semantic judge bên cạnh lexical metrics.

Quality gate production đề xuất: block khi Faithfulness < 0.80, required-policy
Context Recall < 0.80, có data disclosure, prompt-injection compliance, hoặc
aggregate metric giảm quá 0.05 so với baseline.

## 6. Phần bonus

### Framework comparison (+10)

Đã thiết kế so sánh có kiểm soát giữa RAGAS-inspired deterministic core và
DeepEval trên cùng 20 questions, answers và ordered retrieval contexts. Báo cáo
nêu setup, metrics, CI/CD integration, expected disagreement, protocol ba
seeds, Spearman correlation và human adjudication.

### Retrieval reranking (+5)

Đã triển khai `rerank_by_overlap()` và script tái lập trên 5 cases:

| Kết quả trung bình | Before | After |
|---|---:|---:|
| Context Recall | 0.727 | 0.727 |
| Context Precision | 0.821 | **1.000** |

Precision tăng **+0.179**, còn Recall không đổi vì reranking không thêm hoặc
xóa chunk. Kết quả cũng chứng minh reranking không giải quyết được missing
evidence; A01 và M06 vẫn cần sửa retriever/query routing.

## 7. Mapping với rubric

| Rubric | Bằng chứng |
|---|---|
| Core coding — 50đ | `solution/solution.py`, 42/42 tests |
| Golden dataset — 15đ | `golden_dataset.json`, validator PASS, 10/10 docs |
| Judge rubric — 10đ | `exercises.md` Exercise 3.3 |
| Benchmark/failure analysis — 15đ | `artifacts/`, `reflection.md` |
| Code quality/regression — 10đ | type hints, tests, quality gate, regression strategy |
| Bonus — tối đa +15 | Exercises 3.4, 3.5 và reranking script |

## 8. Danh sách file nộp

- `solution/solution.py`
- `golden_dataset.json`
- `exercises.md`
- `reflection.md`
- `artifacts/actual_answers.json`
- `artifacts/benchmark_results.json`
- `scripts/analyze_reranking.py`
- `.github/workflows/quality-gate.yml`
- `SUBMISSION.md`
- `BAO_CAO_CA_NHAN.md`

API key và file `.env` không được lưu trong repository.
