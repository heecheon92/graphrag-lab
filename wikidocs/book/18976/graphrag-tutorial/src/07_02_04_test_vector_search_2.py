# same as 07_02_03_test_vector_search.py but using "neo4j-graphrag" lib.

from neo4j import GraphDatabase
from neo4j_graphrag.embeddings import OpenAIEmbeddings
from neo4j_graphrag.retrievers import VectorRetriever
from util import get_neo4j_config

config = get_neo4j_config()

# Neo4j 연결
driver = GraphDatabase.driver(
    config.uri,
    auth=config.auth,
)

# 임베딩
embeddings = OpenAIEmbeddings()

# VectorRetriever 생성
retriever = VectorRetriever(
    driver=driver,
    index_name="chunk_embeddings",
    embedder=embeddings,
    return_properties=["text", "source"],
    neo4j_database=config.database
)

# 검색
query = "세종대왕이 만든 것은?"
results = retriever.search(query_text=query, top_k=3)

print(f"질문: {query}\n")
for item in results.items:
    print(f"- {item.content[:80]}...")

driver.close()
