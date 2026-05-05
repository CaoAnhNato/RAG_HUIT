import os
from dotenv import load_dotenv
load_dotenv()

client = OpenAI(
    api_key=os.getenv("GEMINI_API_KEY"),
    base_url=os.getenv("GEMINI_BASE_URL", "https://llm.chiasegpu.vn/v1")
)

response = client.chat.completions.create(
    model="gemini-2.5-flash-lite",
    messages=[{"role": "user", "content": "Hiện nay Việt Nam có bao nhiêu tỉnh thành trên cả nước ?"}]
)
print(response.choices[0].message.content)