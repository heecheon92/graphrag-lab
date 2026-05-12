from pathlib import Path

from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings

PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_ROOT / ".env")

embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

# 여러 텍스트를 한 번에 임베딩
texts = [
    "오늘 날씨가 정말 좋습니다.",
    "화창한 하늘이 아름답네요.",
    "파이썬 프로그래밍을 배우고 있습니다.",
    "맛있는 저녁을 먹었습니다."
]

# embed_documents는 여러 텍스트를 한 번에 처리
vectors = embeddings.embed_documents(texts)

print(f"텍스트 개수: {len(texts)}")
print(f"벡터 개수: {len(vectors)}")
print(f"각 벡터의 차원: {len(vectors[0])}")
