from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from pydantic import SecretStr

llm = ChatOpenAI(
    base_url="http://localhost:9000/v1",
    model="llama-3.1-8b-instruct",
    temperature=0.0,
    api_key=SecretStr("sk-dummy"),
)

messages = [
    SystemMessage(content="You are a helpful assistant."),
    HumanMessage(content="What are LLMs?"),
]

response = llm.invoke(messages)
print(response.content)
