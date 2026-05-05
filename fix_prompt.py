import sys

with open('answer_engine/engine.py', 'r', encoding='utf-8') as f:
    content = f.read()

old_prompt = '''        context_str = "\\n".join(contexts)
        
        # 4. Construct Prompt cho Gemini
        prompt = f"""Báº¡n lÃ  chatbot há»— trá»£ sinh viÃªn HUIT. Dá»±a vÃ o thÃ´ng tin sau Ä‘á»ƒ tráº£ lá»i sinh viÃªn: {text}
HÃ£y tráº£ lá» Ä‘Ãºng Ä‘á»‹nh dáº¡ng JSON nÃ y, khÃ´ng cÃ³ markdown text):
{{
    "answer_text": "CÃ¢u tráº£ lá»a Ä‘á»™ cell náº¿u cÃ³
}}"""'''

new_prompt = '''        context_str = "\\n".join(contexts)
        
        # 4. Construct Prompt cho LLM
        prompt = f"""Bạn là chatbot hỗ trợ sinh viên HUIT. Dựa vào thông tin ngữ cảnh sau đây để trả lời câu hỏi của sinh viên.
Ngữ cảnh (TRÍCH TỪ SỔ TAY SINH VIÊN):
{context_str}

Câu hỏi sinh viên: {text}
Nếu thông tin không có trong ngữ cảnh, hãy nói là không tìm thấy thông tin trong sổ tay. Không tự bịa thêm thông tin.
Yêu cầu trả về đúng cú pháp JSON (BẮT BUỘC, KHÔNG CÓ BẤT KỲ CÂU CHỮ NÀO KHÁC, KHÔNG MARKDOWN):
{{
    "answer_text": "Câu trả lời chi tiết của bot",
    "answer_type": "TEXT",
    "source_spans": [],
    "table_id": null,
    "highlight_cells": []
}}"""'''

content = content.replace(old_prompt, new_prompt)

with open('answer_engine/engine.py', 'w', encoding='utf-8') as f:
    f.write(content)
print("Replaced!")
