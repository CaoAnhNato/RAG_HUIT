import os
from llama_parse import LlamaParse

class DocumentParser:
    def __init__(self):
        self.parser = LlamaParse(
            api_key=os.getenv("LLAMA_CLOUD_API_KEY"),
            result_type="markdown",
            verbose=True,
            language="vi" # Hỗ trợ tiếng Việt
        )
    
    def parse_pdf(self, file_path: str):
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        print(f"Parsing document: {file_path}")
        return self.parser.load_data(file_path)
