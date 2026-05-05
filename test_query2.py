import sys
import os
import asyncio
from dotenv import load_dotenv
load_dotenv()
from answer_engine.engine import Engine
from indexing_retrieval.retriever import BaseRetriever
from memory_store.redis_client import RedisStore
from memory_store.session import SessionMemory

redis_store = RedisStore()
session_memory = SessionMemory(redis_store)
retriever = BaseRetriever()
engine = Engine(retriever, session_memory)
result = engine.query('Giới thiệu chung về Trường', 'test_session_123')
import json
print(json.dumps(result, ensure_ascii=False, indent=2))
