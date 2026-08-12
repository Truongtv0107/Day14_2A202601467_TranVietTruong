# Hướng dẫn demo Day 14

## Demo web đã deploy

Dashboard web dành cho mentor được deploy bằng GitHub Pages. Nó hiển thị KPI,
5 metrics, toàn bộ 20 cases, expected/actual answer, retrieval trace, failure
analysis và reranking:

**https://truongtv0107.github.io/Day14_2A202601467_TranVietTruong/**

Chạy web demo ở máy:

```bash
python3 -m http.server 8000
```

Mở `http://localhost:8000/docs/`.

## Chạy demo

```bash
cd /Users/Vtruongtech/Downloads/rar/Day14_2A202601467_TranVietTruong
python3 demo.py
```

Demo đọc các artifact đã tạo từ benchmark thật nên không cần API key hoặc mạng.

Các chế độ chạy nhanh:

```bash
python3 demo.py --overview
python3 demo.py --case A02
python3 demo.py --failures
python3 demo.py --reranking
python3 demo.py --all
```

## Kịch bản trình bày 5 phút

### Phút 0:00–0:30 — Giới thiệu

> Em là Trần Việt Trường, mã học viên 2A202601467. Bài của em xây dựng một
> pipeline đánh giá trợ lý RAG cho Northstar Student Services, từ golden
> dataset, retrieval trace, năm metrics đến failure analysis và CI quality gate.

Chọn menu **1 — Pipeline**.

### Phút 0:30–1:15 — Chứng minh phần bắt buộc

Chọn **2 — Overview** và nêu:

- Core đạt 42/42 tests.
- Dataset có 20 QA đúng 5/7/5/3.
- Evidence phủ đủ 10/10 tài liệu.
- Validator và GitHub Actions đều pass.

### Phút 1:15–2:00 — Kết quả benchmark thật

Chọn **3 — Metrics**:

- Pass rate 80%.
- Context Precision 0.955 và Recall 0.870.
- Completeness 0.664 là metric yếu nhất.
- Điều này cho thấy ranking tốt nhưng generation còn bỏ sót điều kiện.

### Phút 2:00–3:15 — Trace một failure

Chọn **C**, nhập **A02**:

- Chỉ ra chunk `NU-00-P04` đứng rank 1 và chứa đúng safety rule.
- Context Recall đạt 0.913, chứng minh retriever đã làm đúng.
- Actual answer chỉ là “I cannot fulfill that request.”
- Kết luận lỗi ở generation: safe nhưng quá ngắn.
- Đề xuất structured refusal gồm lý do, privacy rule và chủ đề hỗ trợ.

Nếu mentor muốn xem lỗi retrieval, mở **A01**:

- Context Recall chỉ 0.185.
- Không có `00_system_scope.md` trong retrieved trace.
- Đề xuất scope classifier và mandatory scope routing.

### Phút 3:15–4:15 — Bonus reranking

Chọn **6 — Reranking bonus**:

- Context Precision tăng 0.821 → 1.000.
- Context Recall giữ nguyên 0.727.
- Giải thích: reranking chỉ đổi thứ tự, không thêm evidence.
- A01 vẫn cần sửa retriever vì evidence bị thiếu hoàn toàn.

### Phút 4:15–5:00 — CI và kết luận

Chọn **7 — Quality gate**:

- Validator, tests và reranking chạy tự động trên GitHub Actions.
- Regression drop lớn hơn 0.05 sẽ block.
- Privacy disclosure, prompt-injection compliance và sai policy version là
  zero-tolerance gates.

Kết luận:

> Bài không chỉ tạo điểm số mà nối được chu trình Evaluate → Analyze → Improve
> → Regression Gate. Artifact và trace cho phép xác định rõ lỗi nằm ở retrieval
> hay generation.

## Câu hỏi mentor có thể hỏi

**Vì sao Context Recall không nằm trong Overall Score?**

Vì Recall/Precision đo retriever, còn Overall Score gốc đo chất lượng answer.
Tách hai nhóm giúp xác định lỗi thuộc retrieval hay generation.

**Tại sao pass rate chỉ 80% mà vẫn hợp lệ?**

Đề chấm pipeline, evidence và phân tích chứ không yêu cầu một pass rate cố
định. Các failure thật chính là dữ liệu để thực hiện 5 Whys và đề xuất cải tiến.

**Tại sao A02 bị gắn hallucination dù câu trả lời an toàn?**

Failure taxonomy dùng lexical threshold và first-match rule. Câu từ chối quá
ngắn có Faithfulness thấp nên bị gắn nhãn này. Đây là giới hạn của heuristic;
production cần semantic safety judge và loại failure riêng cho safe refusal.

**Reranking khác retrieval thế nào?**

Retrieval chọn tập chunks; reranking chỉ sắp lại tập đã chọn. Vì vậy reranking
cải thiện Precision nhưng không thể phục hồi evidence chưa được retrieve.

**Làm sao chống data leakage?**

`domain_assistant.py` chỉ đọc ID và question để sinh answer. Expected answer
và gold contexts chỉ được evaluator đọc sau khi answer đã được lưu.
