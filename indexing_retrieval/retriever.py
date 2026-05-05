from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer
import os

class BaseRetriever:
    def __init__(self, client=None, collection_name="chatbot_docs"):
        if client:
            self.client = client
        else:
            self.client = QdrantClient(
                host=os.getenv("QDRANT_HOST", "localhost"), 
                port=int(os.getenv("QDRANT_PORT", 6333))
            )
        
        self.collection_name = collection_name
        self.embed_model = SentenceTransformer('thanhtantran/Vietnamese_Embedding_v2')
        
    def retrieve(self, query: str, top_k: int = 15) -> list[str]:
        if not self.client.collection_exists(self.collection_name):
            return []
            
        # Encode the query
        query_vector = self.embed_model.encode(query).tolist()
        
        # Search using query_points
        search_result = self.client.query_points(
            collection_name=self.collection_name,
            query=query_vector,
            limit=top_k
        )
        
        # Extract payload text
        return [hit.payload.get("text", "") for hit in search_result.points if hit.payload]