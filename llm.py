from langchain_openai import ChatOpenAI

llm = ChatOpenAI(
    model="gpt-5.6-luna",
    temperature=0,
    use_responses_api=True
)