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

# 임베딩 모델
embeddings = OpenAIEmbeddings(model=default_embedding_model())

# 샘플 문서 (청크로 분할됨)
chunks = [
    {
        "text": "세종대왕(1397-1450)은 조선의 제4대 왕이다. 그는 백성을 위한 정치를 펼쳤으며, 특히 한글 창제로 유명하다.",
        "source": "korean_history.txt",
        "entities": ["세종대왕"]
    },
    {
        "text": "훈민정음은 1443년에 세종대왕이 창제한 한국의 문자 체계이다. 백성들이 쉽게 글을 읽고 쓸 수 있도록 만들었다.",
        "source": "korean_history.txt",
        "entities": ["훈민정음", "세종대왕"]
    },
    {
        "text": "집현전은 세종대왕이 설치한 학문 연구 기관이다. 성삼문, 박팽년 등 많은 학자들이 이곳에서 활동했다.",
        "source": "korean_history.txt",
        "entities": ["집현전", "세종대왕", "성삼문", "박팽년"]
    },
    {
        "text": "장영실은 조선시대 최고의 과학자이다. 세종대왕과 함께 측우기, 앙부일구, 자격루 등 다양한 과학 기구를 발명했다.",
        "source": "korean_history.txt",
        "entities": ["장영실", "세종대왕", "측우기", "앙부일구", "자격루"]
    },
    {
        "text": "정조(1752-1800)는 조선의 제22대 왕이다. 규장각을 설립하고 정약용 등 실학자들을 등용했다.",
        "source": "korean_history.txt",
        "entities": ["정조", "규장각", "정약용"]
    },
]

# 청크 생성 및 임베딩 저장
for i, chunk in enumerate(chunks):
    # 임베딩 생성
    embedding = embeddings.embed_query(chunk["text"])

    # Chunk 노드 생성
    graph.query("""
        CREATE (c:Chunk {
            id: $id,
            text: $text,
            source: $source,
            embedding: $embedding
        })
    """, params={
        "id": f"chunk_{i}",
        "text": chunk["text"],
        "source": chunk["source"],
        "embedding": embedding
    })

    # 청크와 엔티티 연결
    for entity_name in chunk["entities"]:
        graph.query("""
            MATCH (c:Chunk {id: $chunk_id})
            MATCH (e {name: $entity_name})
            MERGE (c)-[:MENTIONS]->(e)
        """, params={
            "chunk_id": f"chunk_{i}",
            "entity_name": entity_name
        })

print(f"{len(chunks)}개 청크 생성 완료!")
