from langchain_openai import OpenAIEmbeddings
from langchain_neo4j import Neo4jGraph
from util import get_neo4j_config, default_embedding_model

config = get_neo4j_config()

graph = Neo4jGraph(
    url=config.uri,
    username=config.username,
    password=config.password,
    database=config.database
)

embeddings = OpenAIEmbeddings(model=default_embedding_model())

def vector_search(query, k=3):
    """벡터 유사도 검색"""
    query_embedding = embeddings.embed_query(query)

    result = graph.query("""
        CALL db.index.vector.queryNodes(
            'chunk_embeddings',
            $k,
            $embedding
        )
        YIELD node, score
        RETURN node.text AS text, score
    """, params={
        "k": k,
        "embedding": query_embedding
    })

    return result

# 테스트
query = "한글을 만든 사람은 누구인가요?"
results = vector_search(query)

print(f"질문: {query}\n")
print("검색 결과:")
for i, r in enumerate(results, 1):
    print(f"\n[{i}] (유사도: {r['score']:.4f})")
    print(f"    {r['text'][:100]}...")
