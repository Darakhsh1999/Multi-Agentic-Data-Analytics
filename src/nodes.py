from openai import OpenAI

model = OpenAI(
    base_url="http://localhost:11434/v1",
    api_key="ollama"
)

response = model.chat.completions.create(
    model="llama3.2",
    messages=[
        {
            "role": "user",
            "content": "Hello, how are you?"
        }
    ]
)

print(response.choices[0].message.content)
