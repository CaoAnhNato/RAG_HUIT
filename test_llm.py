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
payload = {
    "model": "gemini-2.5-flash",
    "messages": [{"role": "user", "content": "hi"}],
    "temperature": 0.3
}
try:
    print(f"URL: {api_base}/chat/completions")
    resp = requests.post(f"{api_base}/chat/completions", json=payload, headers=headers)
    print(resp.status_code)
    print(resp.text)
    resp.raise_for_status()
except Exception as e:
    print("Error:", e)
