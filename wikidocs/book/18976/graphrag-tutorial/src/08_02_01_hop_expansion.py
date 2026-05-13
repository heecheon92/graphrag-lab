from util import get_neo4j_config
from langchain_neo4j import Neo4jGraph

config = get_neo4j_config()

graph = Neo4jGraph(
    url=config.uri,
    username=config.username,
    password=config.password,
    database=config.database
)

def expand_1hop(entity_name):
    """엔티티에서 1홉 확장"""

    result = graph.query("""
        MATCH (e {name: $name})
        OPTIONAL MATCH (e)-[r]->(related)
        OPTIONAL MATCH (incoming)-[r2]->(e)

        WITH e,
             collect(DISTINCT {
                 direction: 'outgoing',
                 relation: type(r),
                 target: related.name,
                 targetType: labels(related)[0]
             }) AS outgoing,
             collect(DISTINCT {
                 direction: 'incoming',
                 relation: type(r2),
                 source: incoming.name,
                 sourceType: labels(incoming)[0]
             }) AS incoming

        RETURN e.name AS entity,
               labels(e)[0] AS type,
               outgoing,
               incoming
    """, params={"name": entity_name})

    # return result[0] if result else None
    return result[0]

# 테스트
info = expand_1hop("세종대왕")
print(f"엔티티: {info['entity']} ({info['type']})")

print("\n나가는 관계:")
for r in info['outgoing']:
    if r['target']:
        print(f"  → [{r['relation']}] → {r['target']}")

print("\n들어오는 관계:")
for r in info['incoming']:
    if r['source']:
        print(f"  ← [{r['relation']}] ← {r['source']}")


def expand_2hop(entity_name, max_results=20):
    """엔티티에서 2홉까지 확장"""

    result = graph.query("""
        MATCH (start {name: $name})

        // 1홉
        OPTIONAL MATCH (start)-[r1]->(hop1)

        // 2홉
        OPTIONAL MATCH (hop1)-[r2]->(hop2)
        WHERE hop2 <> start  // 시작점 제외

        WITH start,
             collect(DISTINCT {
                 hop: 1,
                 path: start.name + ' -[' + type(r1) + ']-> ' + hop1.name
             }) AS paths1,
             collect(DISTINCT {
                 hop: 2,
                 path: start.name + ' -[' + type(r1) + ']-> ' + hop1.name + 
                       ' -[' + type(r2) + ']-> ' + hop2.name
             }) AS paths2

        RETURN start.name AS entity,
               paths1 + paths2 AS allPaths
        LIMIT $limit
    """, params={"name": entity_name, "limit": max_results})

    # return result[0] if result else None
    return result[0]

# 테스트
info = expand_2hop("세종대왕")
print(f"\n\n'{info['entity']}'에서 시작하는 경로:\n")

for path in info['allPaths']:
    if path['path']:
        print(f"[{path['hop']}홉] {path['path']}")


def get_surrounding_chunks(chunk_id, window_size=1):
    """청크 주변의 청크도 함께 가져오기"""

    # 청크 ID에서 순서 추출 (예: chunk_3 → 3)
    current_idx = int(chunk_id.split("_")[1])

    # 앞뒤 청크 ID 계산
    chunk_ids = [
        f"chunk_{current_idx + i}"
        for i in range(-window_size, window_size + 1)
        if current_idx + i >= 0
    ]

    result = graph.query("""
        MATCH (c:Chunk)
        WHERE c.id IN $ids
        RETURN c.id AS id, c.text AS text
        ORDER BY c.id
    """, params={"ids": chunk_ids})

    return result

# 검색된 청크가 chunk_2라면
surrounding = get_surrounding_chunks("chunk_2", window_size=1)
print("\n주변 청크:")
for chunk in surrounding:
    print(f"\n[{chunk['id']}]")
    print(chunk['text'][:100])
