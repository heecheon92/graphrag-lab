from langchain_core.vectorstores import InMemoryVectorStore
from langchain_openai import OpenAIEmbeddings

from util import default_embedding_model, ensure_project_root_on_path, split_texts

ensure_project_root_on_path()

from data.documents import DOCUMENTS

# 1. 문서 분할
chunks = split_texts(DOCUMENTS, chunk_size=150, chunk_overlap=30)

print(f"총 {len(chunks)}개 청크 생성")

# 2. 벡터 저장소 생성 및 문서 추가
embeddings = OpenAIEmbeddings(model=default_embedding_model())
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
