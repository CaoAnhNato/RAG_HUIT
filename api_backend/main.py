import os
import sys

# Thêm directory gốc của project vào sys.path để Python nhận diện được package api_backend, answer_engine...
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# MUST load dotenv before importing routers because routers instantiate services!
load_dotenv()

from api_backend.routers import chat, health

app = FastAPI(title="Chatbot API", description="API Backend for Context-Aware Chatbot")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, tags=["Health"])
app.include_router(chat.router, prefix="/api", tags=["Chat"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api_backend.main:app", host="127.0.0.1", port=8000, reload=True)
