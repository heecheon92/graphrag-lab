from langchain_openai import OpenAIEmbeddings

from util import default_embedding_model

# 임베딩 모델 생성
embeddings = OpenAIEmbeddings(model=default_embedding_model())

# 테스트 텍스트
text = "GraphRAG는 그래프와 RAG를 결합한 기술입니다."

# 임베딩 생성
vector = embeddings.embed_query(text)

print(f"📊 임베딩 차원: {len(vector)}")
print(f"📊 처음 5개 값: {vector[:5]}")
