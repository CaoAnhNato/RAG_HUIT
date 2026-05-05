# Kế hoạch kiến trúc Chatbot RAG HUFI

File: `plan_chatbot.md`

## 1. Mục tiêu hệ thống

- Xây dựng chatbot hỏi đáp về quy định và thông tin trong **Sổ tay sinh viên HUFI 2020** (một file PDF cố định).
- Độ chính xác cao, tránh bịa thông tin ngoài tài liệu.
- Latency cho mỗi câu trả lời ≤ 5 giây trong điều kiện triển khai on‑prem/local.
- Hỗ trợ câu hỏi văn bản và câu hỏi liên quan đến **bảng**, có trả về bảng kèm highlight cell liên quan.
- Phát hiện câu hỏi **ngoài phạm vi tài liệu** và trả về thông báo phù hợp.
- Ghi nhớ bối cảnh hội thoại (memory) ở mức user/session.

## 2. Tổng quan kiến trúc

Hệ thống chia thành nhiều module độc lập, có thể triển khai trong cùng một repo nhưng tách rõ trách nhiệm:

1. `ingestion_parser`: Tiền xử lý & parse PDF (LlamaParse + Docling).
2. `indexing_retrieval`: Sinh embedding, lưu trữ vào Qdrant, thực hiện hybrid retrieval + reranker.
3. `answer_engine`: Orchestrator dùng LlamaIndex + Gemini 2.5‑Flash để tạo câu trả lời, gồm cả lớp detect OOD.
4. `memory_store`: Tầng quản lý profile người dùng và memory hội thoại trên Redis.
5. `api_backend`: REST API dùng FastAPI, đóng vai trò gateway cho front‑end và client khác.
6. `web_frontend`: Ứng dụng Flask render giao diện web và gọi API từ `api_backend`.
7. `monitoring_logging`: Thu thập log, metric latency, lỗi.
8. `testing`: Bộ test unit, integration, GUI.

Tất cả module chạy trên môi trường local; Redis phục vụ tại `localhost:6379`.

## 3. Module `ingestion_parser`

### 3.1. Nhiệm vụ

- Nhận file PDF cố định `So-tay-sinh-vien-nam-2020.pdf` từ thư mục cấu hình (ví dụ `data/`).
- Parse song song bằng LlamaParse và Docling, sau đó hợp nhất kết quả.
- Tạo **document store nội bộ** dạng JSON hoặc lưu trong DB (ví dụ SQLite) với cấu trúc:
  - Đoạn text theo section.
  - Bảng (table) với cấu trúc hàng/cột, header, cell, bounding box, số trang.
  - Metadata: `doc_id`, `section_path`, `page_start`, `page_end`, `is_table`, `table_id`, v.v.

### 3.2. Đầu vào / đầu ra

- Đầu vào: `So-tay-sinh-vien-nam-2020.pdf`.
- Đầu ra:
  - `parsed_sections.json`: danh sách đoạn text đã chuẩn hóa + metadata.
  - `parsed_tables.json`: danh sách bảng canonical.
  - `media_index.json` (tùy chọn): thông tin hình ảnh, sơ đồ.

### 3.3. Interface gợi ý

- Hàm CLI chính: `parse_pdf()`.
- Có thể chạy một lần khi deploy, không expose API.

## 4. Module `indexing_retrieval`

### 4.1. Nhiệm vụ

- Từ dữ liệu đã parse, tạo các **chunk ngữ nghĩa** cho text và **chunk bảng**.
- Sinh dense embeddings bằng `thanhtantran/Vietnamese_Embedding_v2`.
- Thiết lập sparse index BM25.
- Khởi tạo Qdrant local, tạo collection với named vectors `dense` và `sparse`.
- Cung cấp API nội bộ để:
  - Index lại từ đầu (cho mục đích bảo trì).
  - Thực hiện hybrid search (BM25 + dense + reranker).

### 4.2. Chi tiết chunking

- Text chunk:
  - 150–300 từ, cắt theo heading/mục lục, không cắt ngang câu.
  - Metadata: `chunk_id`, `section_path`, `page_start`, `page_end`, `roles_applicable`, v.v.

- Table chunk:
  - Mỗi bảng là 1 chunk; với bảng lớn có thể tách thành nhiều sub‑chunk theo nhóm dòng, vẫn kèm header.
  - Metadata: `table_id`, `subtable_id`, `page_start`, `page_end`, `header_rows`.

### 4.3. Hybrid retrieval + reranker

- API nội bộ `retrieve_candidates(query, user_profile, top_k)`:
  - Nhận query đã được tiền xử lý và bổ sung ngữ cảnh từ memory.
  - Sinh dense embedding.
  - Gửi song song:
    - Dense search (top N1).
    - Sparse BM25 search (top N2).
  - Hợp nhất danh sách bằng RRF hoặc score fusion.
  - Chạy BGE reranker trên danh sách hợp nhất, trả về top K candidate context (text + bảng) kèm score.

- Kết quả trả về:
  - `contexts`: list context (chunk text/bảng + metadata).
  - `scores`: score tương ứng.

## 5. Module `answer_engine`

### 5.1. Nhiệm vụ

- Đóng vai trò **orchestrator** cho một lượt hỏi đáp.
- Dùng `indexing_retrieval` để lấy context.
- Đánh giá **answerability / OOD**.
- Gọi LLM (Gemini 2.5‑Flash) qua LlamaIndex để sinh câu trả lời có cấu trúc.

### 5.2. Luồng xử lý

1. Nhận `user_query`, `user_id`, `session_id`.
2. Gọi `memory_store` để lấy profile + memory ngắn hạn.
3. Tạo `effective_query` (ví dụ: tiền tố thêm "người hỏi là sinh viên chính quy" nếu có thông tin).
4. Gọi `retrieve_candidates()` để lấy top context + score.
5. Chạy module `answerability_estimator`:
   - Input: các score từ reranker + đặc trưng khác.
   - Output: `is_answerable`, `confidence`.
6. Nếu `is_answerable = False`:
   - Trả về message chuẩn hoá cho OOD.
7. Nếu `is_answerable = True`:
   - Chuẩn bị prompt cho Gemini 2.5‑Flash, yêu cầu output dạng JSON:
     - `answer_text` (markdown/plain).
     - `answer_type` (`TEXT` | `TABLE` | `MIXED`).
     - `source_spans`.
     - Nếu có bảng: `table_id`, `highlight_cells`.
8. Lưu lại snippet hội thoại mới vào `memory_store`.
9. Trả kết quả cho `api_backend`.

### 5.3. Cấu hình LLM

- Lưu `base_url` và `api_key` trong config (ENV) để user cung cấp sau.
- Cho phép chỉnh các tham số:
  - `max_tokens`, `temperature`, `top_p`.

## 6. Module `memory_store`

### 6.1. Nhiệm vụ

- Quản lý **profile người dùng** và **memory hội thoại**.
- Sử dụng Redis local tại `localhost:6379`.

### 6.2. Kiểu dữ liệu chính

1. **User profile** (khoá `user:{user_id}:profile`):
   - `role` (sinh viên, học viên cao học, giảng viên,…).
   - `program_type` (đại học chính quy, vừa làm vừa học,…).
   - Các tuỳ chọn khác (ngôn ngữ UI, mức chi tiết câu trả lời,…).

2. **Session memory** (khoá `session:{session_id}:history`):
   - Lưu vài lượt QA gần nhất hoặc bản tóm tắt.
   - Dạng chuỗi hoặc danh sách JSON (question, answer, timestamp).

### 6.3. API nội bộ

- `get_user_profile(user_id)` / `set_user_profile(user_id, profile)`.
- `append_session_message(session_id, message_obj)`.
- `get_recent_session_context(session_id, limit)`.

## 7. Module `api_backend` (FastAPI)

### 7.1. Nhiệm vụ

- Cung cấp REST API cho front‑end và client khác.
- Thực hiện xác thực nhẹ (nếu cần) và kiểm soát rate‑limit.

### 7.2. Endpoint chính

1. `POST /chat`
   - Input: `user_id`, `session_id`, `message`.
   - Gọi `answer_engine`.
   - Output: JSON:
     - `answer_text`.
     - `answer_type`.
     - `sources` (section, page, table_id,…).
     - `table_html` / `table_json` (nếu có).
     - `highlight_cells`.
     - `latency_breakdown` (retrieval, llm, tổng).

2. `GET /session/{session_id}` (tùy chọn)
   - Trả về tóm tắt session và meta cho debug.

3. `GET /health`
   - Kiểm tra trạng thái Qdrant, Redis, LLM.

### 7.3. Cấu trúc module

- Tách router thành file riêng: `routers/chat.py`, `routers/health.py`.
- Inject dependencies qua FastAPI (clients của Redis, Qdrant, AnswerEngine).

## 8. Module `web_frontend` (Flask)

### 8.1. Mục tiêu

- Cung cấp giao diện web đơn giản cho người dùng cuối.
- Flask chỉ render HTML/template và gọi API FastAPI ở backend.

### 8.2. Bố cục trang

1. **Trang chính `/`**
   - Khung chat:
     - Box nhập câu hỏi.
     - Nút gửi.
     - Hiển thị history hội thoại (user/bot bubbles).
   - Panel thông tin nguồn:
     - Liệt kê các nguồn được dùng (mục, trang, bảng).

2. **Panel bảng kết quả**
   - Khi câu trả lời có `table_html`:
     - Render bảng với CSS.
     - Highlight cell theo `highlight_cells` (background color vàng nhạt).
   - Nút "Xem trên PDF" (nếu muốn) mở viewer ngoài hoặc link tới trang tương ứng.

3. **Khu vực cấu hình cơ bản (tùy chọn)**
   - Form cho phép user khai báo profile: loại hình học, vai trò,…
   - Gửi thông tin lên API để cập nhật `user_profile`.

### 8.3. Luồng front‑end

- Client Flask dùng JavaScript (fetch/AJAX) gọi `POST /chat` lên FastAPI.
- Nhận JSON, cập nhật UI:
  - Tin nhắn bot.
  - Nếu có bảng: render bảng + highlight.
  - Hiển thị thời gian trả lời.

## 9. Module `monitoring_logging`

### 9.1. Nhiệm vụ

- Ghi log ứng dụng (truy vấn, context top‑k, quyết định OOD, lỗi).
- Thu thập metric latency từng bước: parsing, retrieval, reranker, LLM, tổng.

### 9.2. Thành phần chính

- Middleware ở FastAPI để đo thời gian xử lý `/chat`.
- Logger chuẩn (struct log) gửi ra file hoặc stdout.
- Tùy chọn thêm exporter Prometheus.

## 10. Module `testing`

### 10.1. Unit test

- Test `ingestion_parser`:
  - Parse một số trang mẫu chứa bảng, text, hình.
  - Kiểm tra số bảng, số dòng/cột, metadata trang.

- Test `indexing_retrieval`:
  - Kiểm tra số lượng chunk sinh ra.
  - Test retrieval với một số câu hỏi mẫu: kết quả top‑k phải chứa section/bảng được mong đợi.

- Test `answer_engine`:
  - Mock LLM để đảm bảo logic answerability và định dạng JSON output.

- Test `memory_store`:
  - Thiết lập và đọc lại profile, history.

### 10.2. Integration test

- Chạy pipeline từ `POST /chat` đến trả lời, dùng PDF thật.
- Đánh giá:
  - Status code.
  - Trường JSON bắt buộc có mặt.
  - Tổng latency dưới ngưỡng cấu hình.

### 10.3. GUI test

Thiết kế một số **test kịch bản GUI** (có thể dùng Playwright/Selenium hoặc test thủ công có script):

1. **Kịch bản 1 – Câu hỏi text đơn giản**
   - B1: Mở trang chủ.
   - B2: Nhập câu "Giới thiệu chung về Trường".
   - B3: Gửi, kiểm tra:
     - Bot trả lời trong vòng < 5 giây.
     - Câu trả lời hiển thị đầy đủ, có nguồn trang/mục.

2. **Kịch bản 2 – Câu hỏi cần bảng**
   - B1: Hỏi "Các bậc đào tạo và loại hình tương ứng".
   - B2: Kiểm tra:
     - Bảng hiển thị đúng số cột/hàng.
     - Các ô liên quan (ví dụ hàng "Đại học") được highlight vàng.

3. **Kịch bản 3 – Câu hỏi về thư viện**
   - B1: Hỏi "Sinh viên được mượn tối đa bao nhiêu sách?" sau khi đã khai báo "tôi là sinh viên".
   - B2: Kiểm tra:
     - Bot trả lời đúng theo giới hạn cho sinh viên.
     - Nếu câu trả lời trích từ bảng quy định thư viện, bảng được hiển thị + highlight.

4. **Kịch bản 4 – Câu hỏi OOD**
   - B1: Hỏi "Điểm chuẩn tuyển sinh năm 2023 là bao nhiêu?".
   - B2: Kiểm tra:
     - Bot trả về thông điệp chuẩn hóa: câu hỏi nằm ngoài phạm vi Sổ tay SV 2020.
     - Không có bảng hoặc thông tin bịa.

5. **Kịch bản 5 – Multi‑turn với memory**
   - B1: Nhập "Tôi là sinh viên vừa làm vừa học".
   - B2: Tiếp tục hỏi "Mỗi học kỳ tôi được đăng ký tối đa bao nhiêu tín chỉ?".
   - B3: Kiểm tra:
     - Bot dựa trên role sinh viên, không trả lời bằng quy định cho đối tượng khác.

6. **Kịch bản 6 – Lỗi hệ thống**
   - Mô phỏng Qdrant/Redis down.
   - Kiểm tra UI hiển thị thông báo lỗi thân thiện, không treo vô hạn.

## 11. Phân chia repo & module

Gợi ý cấu trúc thư mục để thuận tiện quản lý, debug và mở rộng:

- `ingestion_parser/`
  - `__init__.py`
  - `parser.py`
  - `schemas.py`

- `indexing_retrieval/`
  - `__init__.py`
  - `indexer.py`
  - `retriever.py`
  - `schemas.py`

- `answer_engine/`
  - `__init__.py`
  - `engine.py`
  - `answerability.py`
  - `schemas.py`

- `memory_store/`
  - `__init__.py`
  - `redis_client.py`
  - `profile.py`
  - `session.py`

- `api_backend/`
  - `main.py`
  - `routers/`
    - `chat.py`
    - `health.py`
  - `dependencies.py`

- `web_frontend/`
  - `app.py` (Flask)
  - `templates/`
    - `index.html`
  - `static/` (CSS, JS)

- `monitoring_logging/`
  - `logging_config.py`
  - `metrics.py`

- `tests/`
  - `unit/`
  - `integration/`
  - `gui/` (kịch bản GUI test)

Tài liệu này chỉ liệt kê các thành phần và trách nhiệm chính để AI Agent có thể dựa vào đó thiết kế & triển khai hệ thống chatbot, không bao gồm phần lý thuyết chi tiết hay danh sách thư viện cài đặt.