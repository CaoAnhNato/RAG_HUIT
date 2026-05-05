import pytest
import subprocess
import time
import requests
import sys
import os

@pytest.fixture(scope="session", autouse=True)
def start_services():
    # Cần set PYTHONPATH để chạy đúng
    env = os.environ.copy()
    env["PYTHONPATH"] = "c:\\Users\\Admin\\HUIT - Học Tập\\Năm 3\\Semester_2\\Research\\RAG_HUIT"
    env["PYTHONUNBUFFERED"] = "1"
    
    backend_log = open("backend_test.log", "w")
    frontend_log = open("frontend_test.log", "w")
    
    # Start Backend
    backend = subprocess.Popen([sys.executable, "api_backend/main.py"], cwd="c:\\Users\\Admin\\HUIT - Học Tập\\Năm 3\\Semester_2\\Research\\RAG_HUIT", env=env, stdout=backend_log, stderr=subprocess.STDOUT)
    
    # Start Frontend
    frontend = subprocess.Popen([sys.executable, "web_frontend/app.py"], cwd="c:\\Users\\Admin\\HUIT - Học Tập\\Năm 3\\Semester_2\\Research\\RAG_HUIT", env=env, stdout=frontend_log, stderr=subprocess.STDOUT)
    
    # Wait for services to be ready
    max_retries = 30
    backend_ready = False
    for _ in range(max_retries):
        try:
            response = requests.get("http://127.0.0.1:8000/health")
            if response.status_code == 200:
                backend_ready = True
                break
        except requests.ConnectionError:
            time.sleep(1)
            
    frontend_ready = False
    for _ in range(max_retries):
        try:
            response = requests.get("http://127.0.0.1:5000/")
            if response.status_code == 200:
                frontend_ready = True
                break
        except requests.ConnectionError:
            time.sleep(1)
            
    if not backend_ready or not frontend_ready:
        backend.terminate()
        frontend.terminate()
        pytest.fail("Failed to start services")

    yield

    backend.terminate()
    frontend.terminate()
