// 07-03. 그래프+벡터 검색 결합
// Source: https://wikidocs.net/319225
// These queries write scoped practice data only.
// They demonstrate the idea behind VectorCypherRetriever/HybridRetriever using pure Cypher.

// 1. Clean only Chapter 7 graph-vector practice data.
MATCH (n:PracticeChapter07GraphVector)
DETACH DELETE n;

DROP INDEX practice_ch07_gv_chunk_embeddings IF EXISTS;
DROP INDEX practice_ch07_gv_chunk_fulltext IF EXISTS;

// 2. Create Chunk nodes with toy embeddings.
MERGE (c1:Chunk:PracticeChapter07GraphVectorChunk:PracticeChapter07GraphVector {id: "gv-c1"})
SET c1.text = "세종대왕은 백성을 위해 훈민정음을 창제했다.",
    c1.source = "chapter07_graph_vector_practice",
    c1.embedding = [0.90, 0.10, 0.20, 0.00]
MERGE (c2:Chunk:PracticeChapter07GraphVectorChunk:PracticeChapter07GraphVector {id: "gv-c2"})
SET c2.text = "집현전은 세종대왕이 설치한 학문 연구 기관이며 여러 학자가 활동했다.",
    c2.source = "chapter07_graph_vector_practice",
    c2.embedding = [0.78, 0.28, 0.34, 0.10]
MERGE (c3:Chunk:PracticeChapter07GraphVectorChunk:PracticeChapter07GraphVector {id: "gv-c3"})
SET c3.text = "장영실은 앙부일구와 자격루 같은 과학 기구 발명에 기여했다.",
    c3.source = "chapter07_graph_vector_practice",
    c3.embedding = [0.20, 0.82, 0.10, 0.30]
MERGE (c4:Chunk:PracticeChapter07GraphVectorChunk:PracticeChapter07GraphVector {id: "gv-c4"})
SET c4.text = "성삼문과 박팽년은 집현전에서 활동한 학자이다.",
    c4.source = "chapter07_graph_vector_practice",
    c4.embedding = [0.55, 0.36, 0.42, 0.10];

// 3. Create entity nodes.
MERGE (sejong:Person:PracticeChapter07GraphVector {name: "세종대왕"})
SET sejong.role = "왕"
MERGE (jang:Person:PracticeChapter07GraphVector {name: "장영실"})
SET jang.role = "과학자"
MERGE (sung:Person:PracticeChapter07GraphVector {name: "성삼문"})
SET sung.role = "학자"
MERGE (park:Person:PracticeChapter07GraphVector {name: "박팽년"})
SET park.role = "학자"
MERGE (hangul:Achievement:PracticeChapter07GraphVector {name: "훈민정음"})
SET hangul.type = "문자", hangul.year = 1443
MERGE (jiphyeon:Organization:PracticeChapter07GraphVector {name: "집현전"})
SET jiphyeon.type = "학술기관"
MERGE (sundial:Achievement:PracticeChapter07GraphVector {name: "앙부일구"})
SET sundial.type = "과학 기구"
MERGE (waterclock:Achievement:PracticeChapter07GraphVector {name: "자격루"})
SET waterclock.type = "과학 기구";

// 4. Connect chunks to mentioned entities and connect entities to each other.
MATCH (c1:Chunk:PracticeChapter07GraphVectorChunk:PracticeChapter07GraphVector {id: "gv-c1"})
MATCH (c2:Chunk:PracticeChapter07GraphVectorChunk:PracticeChapter07GraphVector {id: "gv-c2"})
MATCH (c3:Chunk:PracticeChapter07GraphVectorChunk:PracticeChapter07GraphVector {id: "gv-c3"})
MATCH (c4:Chunk:PracticeChapter07GraphVectorChunk:PracticeChapter07GraphVector {id: "gv-c4"})
MATCH (sejong:Person:PracticeChapter07GraphVector {name: "세종대왕"})
MATCH (jang:Person:PracticeChapter07GraphVector {name: "장영실"})
MATCH (sung:Person:PracticeChapter07GraphVector {name: "성삼문"})
MATCH (park:Person:PracticeChapter07GraphVector {name: "박팽년"})
MATCH (hangul:Achievement:PracticeChapter07GraphVector {name: "훈민정음"})
MATCH (jiphyeon:Organization:PracticeChapter07GraphVector {name: "집현전"})
MATCH (sundial:Achievement:PracticeChapter07GraphVector {name: "앙부일구"})
MATCH (waterclock:Achievement:PracticeChapter07GraphVector {name: "자격루"})
MERGE (c1)-[:MENTIONS]->(sejong)
MERGE (c1)-[:MENTIONS]->(hangul)
MERGE (c2)-[:MENTIONS]->(sejong)
MERGE (c2)-[:MENTIONS]->(jiphyeon)
MERGE (c3)-[:MENTIONS]->(jang)
MERGE (c3)-[:MENTIONS]->(sundial)
MERGE (c3)-[:MENTIONS]->(waterclock)
MERGE (c4)-[:MENTIONS]->(sung)
MERGE (c4)-[:MENTIONS]->(park)
MERGE (c4)-[:MENTIONS]->(jiphyeon)
MERGE (sejong)-[:CREATED]->(hangul)
MERGE (sejong)-[:ESTABLISHED]->(jiphyeon)
MERGE (sejong)-[:COLLABORATED_WITH]->(jang)
MERGE (jang)-[:INVENTED]->(sundial)
MERGE (jang)-[:INVENTED]->(waterclock)
MERGE (sung)-[:WORKED_AT]->(jiphyeon)
MERGE (park)-[:WORKED_AT]->(jiphyeon);

// 5. Create vector and fulltext indexes.
CREATE VECTOR INDEX practice_ch07_gv_chunk_embeddings IF NOT EXISTS
FOR (c:PracticeChapter07GraphVectorChunk) ON (c.embedding)
OPTIONS { indexConfig: {
  `vector.dimensions`: 4,
  `vector.similarity_function`: 'cosine'
} };

CREATE FULLTEXT INDEX practice_ch07_gv_chunk_fulltext IF NOT EXISTS
FOR (c:PracticeChapter07GraphVectorChunk)
ON EACH [c.text];

// 6. Confirm index states.
SHOW INDEXES YIELD name, type, state, populationPercent
WHERE name IN ['practice_ch07_gv_chunk_embeddings', 'practice_ch07_gv_chunk_fulltext']
RETURN name, type, state, populationPercent
ORDER BY name;

// 7. Vector search only: retrieve relevant Chunk nodes.
CALL db.index.vector.queryNodes(
  'practice_ch07_gv_chunk_embeddings',
  2,
  [0.80, 0.25, 0.32, 0.08]
)
YIELD node, score
RETURN node.id AS chunk_id, node.text AS chunk_text, score
ORDER BY score DESC;

// 8. Vector + graph expansion: mimic VectorCypherRetriever retrieval_query.
CALL db.index.vector.queryNodes(
  'practice_ch07_gv_chunk_embeddings',
  2,
  [0.80, 0.25, 0.32, 0.08]
)
YIELD node, score
OPTIONAL MATCH (node)-[:MENTIONS]->(entity)
OPTIONAL MATCH (entity)-[r]->(related:PracticeChapter07GraphVector)
RETURN node.id AS chunk_id,
       node.text AS chunk_text,
       score,
       collect(DISTINCT entity.name) AS mentioned_entities,
       collect(DISTINCT {from: entity.name, rel: type(r), to: related.name}) AS relationships
ORDER BY score DESC;

// 9. Fulltext search only: retrieve chunks containing exact terms.
CALL db.index.fulltext.queryNodes('practice_ch07_gv_chunk_fulltext', '집현전 OR 학자')
YIELD node, score
RETURN node.id AS chunk_id, node.text AS chunk_text, score
ORDER BY score DESC;

// 10. Hybrid idea in plain Cypher: compare vector hits and fulltext hits side by side.
CALL {
  CALL db.index.vector.queryNodes(
    'practice_ch07_gv_chunk_embeddings',
    3,
    [0.80, 0.25, 0.32, 0.08]
  )
  YIELD node, score
  RETURN node.id AS chunk_id, node.text AS chunk_text, score, 'vector' AS search_type
  UNION ALL
  CALL db.index.fulltext.queryNodes('practice_ch07_gv_chunk_fulltext', '집현전 OR 학자')
  YIELD node, score
  RETURN node.id AS chunk_id, node.text AS chunk_text, score, 'fulltext' AS search_type
}
RETURN search_type, chunk_id, chunk_text, score
ORDER BY search_type, score DESC;

// 11. One-hop context expansion from mentioned entities.
MATCH (node:Chunk:PracticeChapter07GraphVectorChunk:PracticeChapter07GraphVector)-[:MENTIONS]->(entity)
OPTIONAL MATCH (entity)-[r]->(related:PracticeChapter07GraphVector)
RETURN node.id AS chunk_id,
       entity.name AS entity,
       type(r) AS relationship,
       related.name AS related
ORDER BY chunk_id, entity, relationship;

// 12. Two-hop context expansion around Sejong.
MATCH path = (:Person:PracticeChapter07GraphVector {name: "세종대왕"})-[*1..2]-(connected:PracticeChapter07GraphVector)
RETURN [n in nodes(path) | coalesce(n.name, n.id)] AS path_nodes,
       [r in relationships(path) | type(r)] AS path_relationships;

// 13. Restrict expansion to selected relationship types.
MATCH (node:Chunk:PracticeChapter07GraphVectorChunk:PracticeChapter07GraphVector)-[:MENTIONS]->(entity)
OPTIONAL MATCH (entity)-[r:CREATED|INVENTED]->(achievement:Achievement)
RETURN node.id AS chunk_id,
       entity.name AS entity,
       type(r) AS relationship,
       achievement.name AS achievement
ORDER BY chunk_id, entity, achievement;
