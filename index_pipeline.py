import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__))))

from ingestion_parser.parser import DocumentParser
from indexing_retrieval.indexer import Indexer

def run_pipeline():
    print("1. Parsing document...")
    parser = DocumentParser()
    docs = parser.parse_pdf("So tay sinh vien nam 2020.pdf")
    
    # LlamaParse returns a list of Document objects.
    # Convert them to text strings for the chunking logic we have
    texts = [doc.text for doc in docs if doc.text]
    
    print(f"2. Indexing {len(texts)} chunks...")
    indexer = Indexer(use_memory=False) # Connect to Docker Qdrant
    count = indexer.index_documents("chatbot_docs", texts)
    print(f"Successfully indexed {count} items.")

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    run_pipeline()