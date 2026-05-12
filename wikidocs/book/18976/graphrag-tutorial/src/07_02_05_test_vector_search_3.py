# same as 07_02_03_test_vector_search.py but using "langchain_neo4j" lib.

from util import get_neo4j_config, default_embedding_model
from langchain_openai import OpenAIEmbeddings
from langchain_neo4j import Neo4jVector

config = get_neo4j_config()

# 기존 인덱스에 연결
vector_store = Neo4jVector.from_existing_index(
    embedding=OpenAIEmbeddings(model=default_embedding_model()),
    url=config.uri,
    username=config.username,
    password=config.password,
    index_name="chunk_embeddings",
    text_node_property="text"
)

# 검색
results = vector_store.similarity_search(
    "세종대왕의 업적",
    k=3
)

for doc in results:
    print(f"- {doc.page_content[:80]}...")
