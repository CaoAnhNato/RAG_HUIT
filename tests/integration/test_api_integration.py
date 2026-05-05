import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch
from api_backend.main import app

client = TestClient(app)

@patch("api_backend.routers.chat.engine")
def test_full_chat_api(mock_engine):
    # Mocking behavior of the engine to abstract away DB/LLM connection for the API Integration Test
    mock_engine.query.return_value = {
        "answer": "Theo sổ tay sinh viên, sinh viên cần 150 tín chỉ.",
        "context": ["Sinh viên tích luỹ 150 tín chỉ để tốt nghiệp."]
    }
    
    response = client.post("/api/chat", json={
        "session_id": "e2e_test_session",
        "message": "Cần bao nhiêu tín chỉ tốt nghiệp?"
    })
    
    assert response.status_code == 200
    data = response.json()
    assert data["reply"] == "Theo sổ tay sinh viên, sinh viên cần 150 tín chỉ."
    assert len(data["context"]) == 1
