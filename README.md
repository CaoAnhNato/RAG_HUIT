# HUIT RAG Chatbot - Hệ thống Hỏi đáp Thông minh

Dự án xây dựng hệ thống Chatbot sử dụng kỹ thuật **RAG (Retrieval-Augmented Generation)** để hỗ trợ giải đáp thắc mắc dựa trên cơ sở dữ liệu nội bộ của trường (HUIT).

## 🚀 Tổng quan hệ thống

Hệ thống được thiết kế với kiến trúc hiện đại, chia làm 2 phần chính:
- **Backend (FastAPI):** Xử lý logic RAG, bao gồm ingestion, indexing, retrieval và tích hợp LLM (Gemini/GPT).
- **Frontend (Flask):** Giao diện web thân thiện cho người dùng cuối tương tác với chatbot.

### Các thành phần chính:
- **LlamaIndex:** Framework chính cho pipeline RAG.
- **Qdrant:** Vector Database để lưu trữ và tìm kiếm vector embeddings.
- **Redis:** Lưu trữ metadata và hỗ trợ các tác vụ caching.
- **Gemini API:** Mô hình ngôn ngữ lớn (LLM) để sinh câu trả lời.

---

## 📂 Cấu trúc thư mục

- `api_backend/`: Source code API (FastAPI).
- `web_frontend/`: Giao diện người dùng (Flask).
- `ingestion_parser/`: Xử lý phân tách và làm sạch dữ liệu đầu vào.
- `indexing_retrieval/`: Quản lý chỉ mục và truy xuất dữ liệu.
- `answer_engine/`: Logic sinh câu trả lời từ dữ liệu truy xuất.
- `example/`: Chứa các hình ảnh minh họa kết quả.

---

## 🛠 Hướng dẫn cài đặt

### 1. Clone Repository
```bash
git clone https://github.com/your-username/RAG_HUIT.git
cd RAG_HUIT
```

### 2. Cài đặt môi trường
Yêu cầu Python 3.9+ và môi trường `fruit_env`.

```bash
# Kích hoạt môi trường (nếu đã có)
conda activate fruit_env

# Hoặc tạo mới và cài đặt dependencies
pip install -r requirements.txt
```

### 3. Cấu hình biến môi trường
Tạo file `.env` tại thư mục gốc và cấu hình các thông số sau:
```env
GEMINI_API_KEY=your_gemini_api_key
GEMINI_BASE_URL=https://llm.chiasegpu.vn/v1
LLAMA_CLOUD_API_KEY=your_llama_cloud_key

REDIS_HOST=localhost
REDIS_PORT=6379
QDRANT_HOST=localhost
QDRANT_PORT=6333
```

---

## 🏃 Cách chạy hệ thống

### Bước 1: Khởi động Backend
Mở terminal và chạy lệnh:
```bash
python api_backend/main.py
```
API sẽ chạy tại: `http://127.0.0.1:8000`

### Bước 2: Khởi động Frontend
Mở một terminal khác và chạy lệnh:
```bash
python web_frontend/app.py
```
Giao diện người dùng sẽ chạy tại: `http://127.0.0.1:5000`

---

## 📊 Kết quả thực hiện

Dưới đây là một số hình ảnh demo kết quả của hệ thống:

![Kết quả 1](example/image_1.png)

![Kết quả 2](example/image_2.png)

---
© 2024 Research Team - HUIT
