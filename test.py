from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:1234/v1",
    api_key="EMPTY",  # vLLM по умолчанию не требует ключ
)

response = client.chat.completions.create(
    model="Qwen/Qwen3.6-35B-A3B-FP8",
    messages=[
        {"role": "user", "content": "Привет! Как дела?"}
    ],
)

print(response.choices[0].message.content)