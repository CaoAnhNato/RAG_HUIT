from openai import OpenAI

client = OpenAI(
    api_key="sk-f06c90faf071ccd4d60616e75a8d56d196f8abb8b958d9434ff89844c478003c",
    base_url="https://llm.chiasegpu.vn/v1"
)

response = client.chat.completions.create(
    model="gemini-2.5-flash-lite",
    messages=[{"role": "user", "content": "Hiện nay Việt Nam có bao nhiêu tỉnh thành trên cả nước ?"}]
)
print(response.choices[0].message.content)