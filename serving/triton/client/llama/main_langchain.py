from langchain_nvidia_ai_endpoints import ChatNVIDIA
from langchain_core.messages import SystemMessage, HumanMessage
from pydantic import SecretStr

llm = ChatNVIDIA(
    base_url="http://localhost:9000/v1",
    model="llama-3.1-8b-instruct",
    temperature=0.0,
    api_key=SecretStr("sk-dummy"),
    max_tokens=4096,
)

messages = [
    SystemMessage(content="You are a helpful assistant. Please tell me as korean"),
    HumanMessage(content="What are LLMs?"),
]

response = llm.invoke(messages)
print(response.content)
