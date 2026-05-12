from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_text_splitters import RecursiveCharacterTextSplitter

import sys
from pathlib import Path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
from data.documents import DOCUMENTS

load_dotenv(PROJECT_ROOT / ".env")

# 1. 문서 분할
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=150,
    chunk_overlap=30,
)

chunks = []
for doc in DOCUMENTS:
    chunks.extend(text_splitter.split_text(doc))

print(f"총 {len(chunks)}개 청크 생성")

# 2. 벡터 저장소 생성 및 문서 추가
embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
vector_store = InMemoryVectorStore(embeddings)
vector_store.add_texts(chunks)

print("벡터 저장소 구축 완료!")

# 3. 검색 테스트
query = "세종대왕이 만든 발명품"
results = vector_store.similarity_search(query, k=3)

print(f"\n질문: {query}\n")
print("검색 결과:")
for i, doc in enumerate(results, 1):
    print(f"\n[{i}] {doc.page_content}")
