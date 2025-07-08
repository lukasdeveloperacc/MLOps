from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:9000/v1",
    api_key="EMPTY",
)

model = "llama-3.1-8b-instruct"
completion = client.chat.completions.create(
    model=model,
    messages=[
        {
            "role": "system",
            "content": "You are a helpful assistant.",
        },
        {"role": "user", "content": "What are LLMs? Please tell me as korean"},
    ],
    max_tokens=4096,
)

print(completion.choices[0].message.content)
