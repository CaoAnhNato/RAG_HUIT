import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

import pytest
from indexing_retrieval.indexer import Indexer
from indexing_retrieval.retriever import BaseRetriever

def test_retriever():
    indexer = Indexer(use_memory=True)
    collection_name = "test_retriever_collection"
    
    docs = [
        "Sinh viên ngành CNTT cần học môn Cấu trúc dữ liệu.",
        "Quy định vắng thi: Sinh viên vắng mặt không phép sẽ nhận điểm 0.",
        "Học bổng khuyến khích học tập dành cho sinh viên có GPA trên 3.2."
    ]
    indexer.index_documents(collection_name, docs)
    
    # Initialize retriever using the same memory client
    retriever = BaseRetriever(client=indexer.client, collection_name=collection_name)
    
    # Test query 1
    results = retriever.retrieve("Xin hỏi về quy định khi nghỉ thi?", top_k=1)
    assert len(results) == 1
    assert "vắng thi" in results[0].lower()
    
    # Test query 2
    results_gpa = retriever.retrieve("Điều kiện lấy học bổng", top_k=1)
    assert "GPA trên 3.2" in results_gpa[0]
