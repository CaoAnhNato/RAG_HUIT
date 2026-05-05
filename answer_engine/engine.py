import os
import json
import requests
from indexing_retrieval.retriever import BaseRetriever
from answer_engine.answerability import AnswerabilityEstimator

class Engine:
    def __init__(self, retriever: BaseRetriever, memory):
        self.retriever = retriever
        self.memory = memory
        self.ood_detector = AnswerabilityEstimator()
        
        self.api_key = os.getenv("GEMINI_API_KEY", "mock_key")
        self.api_base = os.getenv("GEMINI_BASE_URL", "https://llm.chiasegpu.vn/v1")
        self.model_name = os.getenv("GEMINI_MODEL", "csu/pro/kimi-k2.5")
        
        self.table_store = {}
        self._load_tables()
        
    def _load_tables(self):
        try:
            table_file = os.path.join(os.path.dirname(__file__), '..', 'data', 'parsed_tables.json')
            if os.path.exists(table_file):
                with open(table_file, 'r', encoding='utf-8') as f:
                    self.table_store = json.load(f)
        except Exception as e:
            print("Error loading tables:", e)
        
    def _call_llm(self, prompt: str) -> str:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": self.model_name,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.3
        }
        
        try:
            url = f"{self.api_base}/chat/completions"
            resp = requests.post(url, json=payload, headers=headers)
            resp.raise_for_status()
            data = resp.json()
            return data["choices"][0]["message"]["content"]
        except Exception as e:
            print("LLM Error:", e)
            return "{\"answer_text\": \"Lỗi khi gọi mô hình ngôn ngữ.\", \"answer_type\": \"TEXT\"}"

    def query(self, text: str, session_id: str):
        # 1. Fetch memory history
        history = self.memory.get_history(session_id) if self.memory else []
        
        # 2. Fetch context from retriever
        # Add school name to improve dense retrieval accuracy
        enhanced_query = f"{text} tại Trường Đại học Công nghiệp Thực phẩm TP. HCM HUFI"
        contexts = self.retriever.retrieve(enhanced_query)
        
        # 3. Kích hoạt OOD (Out-Of-Domain) Detection
        if not self.ood_detector.is_in_domain(text, contexts):
            reply = "Xin lỗi, tôi chỉ có thể trả lời các thông tin liên quan đến Sổ tay sinh viên HUIT. Câu hỏi của bạn có vẻ nằm ngoài phạm vi này."
            if self.memory:
                self.memory.add_message(session_id, f"User: {text}")
                self.memory.add_message(session_id, f"Bot: {reply}")
            return {"answer": {
                "answer_text": reply,
                "answer_type": "TEXT",
                "source_spans": [],
                "table_id": None,
                "highlight_cells": []
            }, "context": []}
            
        context_str = "\n".join(contexts)
        
        # 4. Construct Prompt cho Gemini
        prompt = f"""Bạn là chatbot hỗ trợ sinh viên HUIT. Dựa vào thông tin sau để trả lời:
Ngữ cảnh:
{context_str}

Lịch sử:
{history[-3:] if history else 'Không có'}

Câu hỏi sinh viên: {text}
Hãy trả lời chính xác, nếu trong ngữ cảnh không có thông tin, hãy báo không biết.
Yêu cầu định dạng đầu ra (bắt buộc trả về đúng định dạng JSON này, không có markdown text):
{{
    "answer_text": "Câu trả lời của bạn",
    "answer_type": "TEXT", // Hoặc "TABLE", "MIXED"
    "source_spans": ["trích dẫn 1", "trích dẫn 2"],
    "table_id": null, // Hoặc string ID của bảng nếu có
    "highlight_cells": [] // Hoặc list chứa tọa độ cell nếu có
}}"""
        
        # 4. Generate response
        reply = self._call_llm(prompt)
        
        try:
            import json
            import re
            
            clean_reply = re.sub(r"```[A-Za-z]*\s*", "", reply)
            clean_reply = re.sub(r"```", "", clean_reply).strip()
            # Bỏ comments // vì json.loads không hỗ trợ javascript comments, LLM đôi khi trả về
            clean_reply = re.sub(r"//.*", "", clean_reply)
            structured_data = json.loads(clean_reply)
        except Exception:
            structured_data = {
                "answer_text": reply,
                "answer_type": "TEXT",
                "source_spans": [],
                "table_id": None,
                "highlight_cells": []
            }
            
        # Xử lý table_html nếu có
        if structured_data.get("answer_type") in ["TABLE", "MIXED"] and structured_data.get("table_id"):
            table_id = structured_data["table_id"]
            if table_id in self.table_store:
                table_data = self.table_store[table_id]
                structured_data["table_json"] = {
                    "headers": table_data.get("headers", []),
                    "rows": table_data.get("rows", [])
                }
                
                # Highlight cells in HTML
                html = table_data.get("html", "")
                highlight_cells = structured_data.get("highlight_cells", [])
                
                if html and highlight_cells:
                    from bs4 import BeautifulSoup
                    soup = BeautifulSoup(html, 'html.parser')
                    for cell_id in highlight_cells:
                        # cell_id có thể là chuỗi mô tả, nên cần regex hoặc match ID nếu format là ID
                        # Do dữ liệu giả lập có ID dạng "table_{id}_cell_{r}_{c}", giả định LLM sinh ra đúng
                        cell = soup.find(id=cell_id)
                        if cell:
                            cell['class'] = cell.get('class', []) + ['highlight-cell']
                    structured_data["table_html"] = str(soup)
                else:
                    structured_data["table_html"] = html
        
        # 5. Lưu lại vào session memory
        if self.memory:
            self.memory.add_message(session_id, f"User: {text}")
            self.memory.add_message(session_id, f"Bot: {structured_data.get('answer_text', reply)}")
            
        return {"answer": structured_data, "context": contexts}