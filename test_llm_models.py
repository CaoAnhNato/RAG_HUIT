import os
import requests
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
api_base = os.getenv("GEMINI_BASE_URL", "https://llm.chiasegpu.vn/v1")

headers = {
    "Authorization": f"Bearer " + str(api_key),
    "Content-Type": "application/json"
}
try:
    resp = requests.get(f"{api_base}/models", headers=headers)
    print(resp.status_code)
    print(resp.text)
except Exception as e:
    print("Error:", e)
