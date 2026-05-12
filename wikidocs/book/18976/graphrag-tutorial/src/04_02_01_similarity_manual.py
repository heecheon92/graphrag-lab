from langchain_openai import OpenAIEmbeddings

from util import cosine_similarity, default_embedding_model

# 임베딩 모델 초기화
embeddings = OpenAIEmbeddings(model=default_embedding_model())

# 테스트 문장들
sentences = [
    "오늘 날씨가 정말 좋습니다.",      # 기준 문장
    "화창한 하늘이 아름답네요.",        # 비슷한 의미
    "파이썬 프로그래밍을 배웁니다.",    # 다른 주제
    "비가 많이 내립니다.",             # 날씨 관련, 다른 내용
]

# 모든 문장 임베딩
vectors = embeddings.embed_documents(sentences)

# 첫 번째 문장과 나머지 비교
print("기준: ", sentences[0])
print("-" * 50)

for i in range(1, len(sentences)):
    similarity = cosine_similarity(vectors[0], vectors[i])
    print(f"{sentences[i]}")
    print(f"  → 유사도: {similarity:.4f}")
    print()
