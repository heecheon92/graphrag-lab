from langchain_openai import OpenAIEmbeddings

from util import default_embedding_model

# 임베딩 모델 초기화
embeddings = OpenAIEmbeddings(model=default_embedding_model())

# 텍스트를 임베딩으로 변환
text = "오늘 날씨가 정말 좋습니다."
vector = embeddings.embed_query(text)

# 결과 확인
print(f"입력 텍스트: {text}")
print(f"벡터 차원: {len(vector)}")
print(f"벡터 앞부분: {vector[:5]}")
