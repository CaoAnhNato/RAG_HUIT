import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

import pytest
from unittest.mock import MagicMock
from answer_engine.engine import Engine

def test_engine_ood():
    mock_retriever = MagicMock()
    mock_retriever.retrieve.return_value = [] # Không tìm thấy context -> OOD
    mock_memory = MagicMock()
    
    engine = Engine(retriever=mock_retriever, memory=mock_memory)
    
    # Text không thuộc sổ tay sinh viên
    result = engine.query("Cách nấu món phở bò?", "session_1")
    assert "nằm ngoài phạm vi" in result["answer"].lower() or "xin lỗi" in result["answer"].lower()
    assert result["context"] == []
    
    # Kiểm tra memory có ghi nhận log OOD không
    assert mock_memory.add_message.call_count == 2

def test_engine_in_domain():
    mock_retriever = MagicMock()
    mock_retriever.retrieve.return_value = ["1. Sinh viên phải mang thẻ sinh viên khi đến trường."] 
    mock_memory = MagicMock()
    mock_memory.get_history.return_value = ["User: Chào bạn", "Bot: Chào bạn, tôi có thể giúp gì?"]
    
    engine = Engine(retriever=mock_retriever, memory=mock_memory)
    # Mock LLM API call
    engine.llm = MagicMock()
    engine.llm.complete.return_value = "Dạ, quy định ghi rõ sinh viên phải mang thẻ sinh viên."
    
    result = engine.query("Quy định thẻ sinh viên thế nào?", "session_2")
    
    assert "mang thẻ sinh viên" in result["answer"].lower()
    assert len(result["context"]) == 1
    engine.llm.complete.assert_called_once()
