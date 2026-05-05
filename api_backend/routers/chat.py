from fastapi import APIRouter, Depends
from pydantic import BaseModel
from answer_engine.engine import Engine
from memory_store.redis_client import RedisStore
from memory_store.session import SessionMemory
from indexing_retrieval.retriever import BaseRetriever

router = APIRouter()

# Dependency Injection setup
redis_store = RedisStore()
session_memory = SessionMemory(redis_store)
retriever = BaseRetriever()
engine = Engine(retriever, session_memory)

class ChatRequest(BaseModel):
    session_id: str
    message: str

@router.post("/chat")
def chat(req: ChatRequest):
    try:
        result = engine.query(req.message, req.session_id)
        return {"reply": result["answer"], "context": result["context"]}
    except Exception as e:
        return {"error": str(e)}
