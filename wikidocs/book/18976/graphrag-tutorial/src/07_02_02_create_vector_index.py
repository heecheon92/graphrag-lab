from langchain_neo4j import Neo4jGraph
from util import get_neo4j_config

config = get_neo4j_config()

graph = Neo4jGraph(
    url=config.uri,
    username=config.username,
    password=config.password,
    database=config.database
)

# 인덱스 생성
graph.query("""
    CREATE VECTOR INDEX chunk_embeddings IF NOT EXISTS
    FOR (c:Chunk)
    ON c.embedding
    OPTIONS {
        indexConfig: {
            `vector.dimensions`: 1536,
            `vector.similarity_function`: 'cosine'
        }
    }
""")

print("벡터 인덱스 생성 완료!")
