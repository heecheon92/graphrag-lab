// 08-04. 성능 최적화
// Source: https://wikidocs.net/319232
// Neo4j Browser-runnable performance inspection and index examples.
// Most queries are read-only. CREATE INDEX statements add indexes only if missing.

// 1. Check Neo4j version before choosing vector search syntax.
CALL dbms.components() YIELD name, versions, edition
RETURN name, versions[0] AS version, edition;

// 2. Inspect current indexes and confirm they are ONLINE.
SHOW INDEXES YIELD name, type, labelsOrTypes, properties, state, populationPercent
RETURN name, type, labelsOrTypes, properties, state, populationPercent
ORDER BY type, name;

// 3. Inspect vector indexes only.
SHOW VECTOR INDEXES YIELD name, state, populationPercent, labelsOrTypes, properties
RETURN name, state, populationPercent, labelsOrTypes, properties
ORDER BY name;

// 4. Base vector index for this tutorial project.
// text-embedding-3-small default dimension is 1536.
CREATE VECTOR INDEX chunk_embeddings IF NOT EXISTS
FOR (c:Chunk) ON (c.embedding)
OPTIONS { indexConfig: {
  `vector.dimensions`: 1536,
  `vector.similarity_function`: 'cosine'
} };

// 5. Fulltext index for this project.
// The WikiDocs page uses c.content in examples, but this repo's Chunk property is c.text.
CREATE FULLTEXT INDEX chunk_fulltext IF NOT EXISTS
FOR (c:Chunk) ON EACH [c.text];

// 6. Property index for frequent source filtering.
CREATE INDEX chunk_source IF NOT EXISTS
FOR (c:Chunk) ON (c.source);

// 7. Optional property index for stable lookup by tutorial chunk id.
CREATE INDEX chunk_id IF NOT EXISTS
FOR (c:Chunk) ON (c.id);

// 8. Confirm indexes again after creation.
SHOW INDEXES YIELD name, type, labelsOrTypes, properties, state, populationPercent
WHERE name IN ['chunk_embeddings', 'chunk_fulltext', 'chunk_source', 'chunk_id']
RETURN name, type, labelsOrTypes, properties, state, populationPercent
ORDER BY name;

// 9. EXPLAIN: inspect plan without executing the query.
EXPLAIN
MATCH (c:Chunk)-[:MENTIONS]->(e)
WHERE c.source = 'korean_history.txt'
RETURN c.id AS chunk_id, c.text AS text, collect(e.name) AS entities
LIMIT 20;

// 10. PROFILE: read-only query execution with actual plan metrics.
PROFILE
MATCH (c:Chunk)-[:MENTIONS]->(e)
WHERE c.source = 'korean_history.txt'
RETURN c.id AS chunk_id, c.text AS text, collect(e.name) AS entities
LIMIT 20;

// 11. Efficient relationship expansion after candidate chunks are limited.
MATCH (c:Chunk)
WHERE c.source = 'korean_history.txt' AND c.embedding IS NOT NULL
WITH c
ORDER BY c.id
LIMIT 100
OPTIONAL MATCH (c)-[:MENTIONS]->(e)
RETURN c.id AS chunk_id, left(c.text, 80) AS text, collect(e.name) AS entities;

// 12. Fulltext search smoke test.
CALL db.index.fulltext.queryNodes('chunk_fulltext', '세종대왕 OR 집현전')
YIELD node, score
RETURN node.id AS chunk_id, left(node.text, 100) AS text, score
ORDER BY score DESC
LIMIT 10;

// 13. Vector search with pagination-style slicing.
// Replace $embedding with a real query embedding from Python/driver code.
// CALL db.index.vector.queryNodes('chunk_embeddings', $top_k, $embedding)
// YIELD node, score
// RETURN node.id AS chunk_id, node.text AS text, score
// ORDER BY score DESC
// SKIP $skip
// LIMIT $limit;

// 14. Neo4j 2026.01+ preferred vector search shape.
// Use only if your server supports the SEARCH clause.
// MATCH (c:Chunk)
//   SEARCH c IN (
//     VECTOR INDEX chunk_embeddings
//     FOR $embedding
//     LIMIT 10
//   ) SCORE AS score
// RETURN c.id AS chunk_id, c.text AS text, score
// ORDER BY score DESC;
