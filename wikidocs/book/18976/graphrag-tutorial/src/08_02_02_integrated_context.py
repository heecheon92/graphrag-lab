from util import get_neo4j_config, default_llm_model, default_embedding_model
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_neo4j import Neo4jGraph
from langchain_core.prompts import ChatPromptTemplate

config = get_neo4j_config()

graph = Neo4jGraph(
    url=config.uri,
    username=config.username,
    password=config.password,
    database=config.database
)
embeddings = OpenAIEmbeddings(model=default_embedding_model())
llm = ChatOpenAI(model=default_llm_model(), temperature=0)

def build_rich_context(query, k=3):
    """풍부한 컨텍스트 구성"""

    query_embedding = embeddings.embed_query(query)

    # 1. 벡터 검색으로 관련 청크 찾기
    chunks = graph.query("""
        CALL db.index.vector.queryNodes('chunk_embeddings', $k, $embedding)
        YIELD node, score
        RETURN node.text AS text, node.id AS id, score
    """, params={"k": k, "embedding": query_embedding})

    # 2. 청크에서 언급된 엔티티 수집
    all_entities = set()
    for chunk in chunks:
        entities = graph.query("""
            MATCH (c:Chunk {id: $id})-[:MENTIONS]->(e)
            RETURN e.name AS name
        """, params={"id": chunk['id']})
        for e in entities:
            all_entities.add(e['name'])

    # 3. 엔티티의 관계 탐색
    relationships = []
    for entity in all_entities:
        rels = graph.query("""
            MATCH (e {name: $name})-[r]->(related)
            RETURN e.name AS from, type(r) AS relation, related.name AS to
            LIMIT 5
        """, params={"name": entity})
        relationships.extend(rels)

    # 4. 컨텍스트 조합
    context_parts = []

    # 청크 텍스트
    context_parts.append("## 관련 문서")
    for chunk in chunks:
        context_parts.append(f"- {chunk['text']}")

    # 엔티티 정보
    if all_entities:
        context_parts.append("\n## 관련 엔티티")
        context_parts.append(", ".join(all_entities))

    # 관계 정보
    if relationships:
        context_parts.append("\n## 관계 정보")
        for rel in relationships:
            context_parts.append(f"- {rel['from']} → [{rel['relation']}] → {rel['to']}")

    return "\n".join(context_parts)

# 테스트
query = "세종대왕이 설립한 기관과 그곳에서 활동한 사람들"
context = build_rich_context(query)
print("생성된 컨텍스트:")
print(context)

# LLM으로 답변 생성
prompt = ChatPromptTemplate.from_template("""
다음 컨텍스트를 바탕으로 질문에 상세히 답해주세요.

컨텍스트:
{context}

질문: {question}

답변:""")

chain = prompt | llm
response = chain.invoke({"context": context, "question": query})
print("\n답변:")
print(response.content)

def get_path_context(entity1, entity2, max_hops=3):
    """두 엔티티 간 경로 찾기"""

    result = graph.query("""
        MATCH path = shortestPath(
            (a {name: $entity1})-[*1..""" + str(max_hops) + """]-(b {name: $entity2})
        )
        RETURN [n in nodes(path) | n.name] AS nodes,
               [r in relationships(path) | type(r)] AS relations
    """, params={"entity1": entity1, "entity2": entity2})

    if result:
        path_info = result[0]
        nodes = path_info['nodes']
        relations = path_info['relations']

        # 경로를 문자열로 변환
        path_str = nodes[0]
        for i, rel in enumerate(relations):
            path_str += f" -[{rel}]-> {nodes[i+1]}"

        return path_str

    return None

# 테스트
path = get_path_context("세종대왕", "성삼문")
print(f"\n경로: {path}")
# 예: 세종대왕 -[ESTABLISHED]-> 집현전 <-[WORKED_AT]- 성삼문

