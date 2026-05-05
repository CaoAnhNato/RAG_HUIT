import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

import pytest
from indexing_retrieval.indexer import Indexer

def test_indexer_initialization():
    # Chạy Qdrant trong RAM (không cần docker) để unit test nhanh
    indexer = Indexer(use_memory=True)
    assert indexer.vector_size > 0
    assert indexer.embed_model is not None

def test_index_documents():
    indexer = Indexer(use_memory=True)
    collection_name = "test_collection"
    
    docs = [
        "Sổ tay sinh viên quy định về học vụ",
        "Sinh viên cần hoàn thành 150 tín chỉ để tốt nghiệp"
    ]
    
    count = indexer.index_documents(collection_name, docs)
    assert count == 2
    
    # Check if collection exists and has points
    collection_info = indexer.client.get_collection(collection_name)
    assert collection_info.points_count == 2