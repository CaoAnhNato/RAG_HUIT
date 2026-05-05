from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance, PointStruct
from sentence_transformers import SentenceTransformer
import os
import uuid

class Indexer:
    def __init__(self, use_memory=False):
        # Tránh lỗi require Docker khi chạy unit test cục bộ bằng use_memory
        if use_memory:
            self.client = QdrantClient(location=":memory:")
        else:
            self.client = QdrantClient(
                host=os.getenv("QDRANT_HOST", "localhost"), 
                port=int(os.getenv("QDRANT_PORT", 6333))
            )
        
        # Load embedding model dành cho tiếng Việt
        self.embed_model = SentenceTransformer('thanhtantran/Vietnamese_Embedding_v2')
        self.vector_size = self.embed_model.get_sentence_embedding_dimension()
        
    def setup_collection(self, collection_name: str):
        if not self.client.collection_exists(collection_name):
            self.client.create_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(size=self.vector_size, distance=Distance.COSINE),
            )
            
    def index_documents(self, collection_name: str, documents: list[str]):
        """Lưu trữ list các đoạn text vào Qdrant."""
        self.setup_collection(collection_name)
        
        points = []
        for doc in documents:
            vector = self.embed_model.encode(doc).tolist()
            points.append(PointStruct(id=str(uuid.uuid4()), vector=vector, payload={"text": doc}))
            
        if points:
            self.client.upsert(collection_name=collection_name, points=points)
            return len(points)
        return 0
