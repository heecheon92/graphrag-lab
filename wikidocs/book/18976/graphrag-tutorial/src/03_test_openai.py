from langchain_openai import ChatOpenAI

from util import default_llm_model

# ChatGPT 모델 생성
llm = ChatOpenAI(model=default_llm_model(), temperature=0)

# 간단한 테스트
response = llm.invoke("안녕하세요! 한 문장으로 자기소개 해주세요.")
print("🤖 GPT 응답:", response.content)
