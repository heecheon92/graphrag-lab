// 07-02. 벡터 인덱스 만들기
// Source: https://wikidocs.net/319224
// These queries write scoped practice data only.
// The embeddings below are 4-dimensional toy vectors for Neo4j Browser practice.
// Real OpenAI text-embedding-3-small embeddings are usually 1536-dimensional.

// 1. Clean only Chapter 7 vector-index practice data.
MATCH (n:PracticeChapter07Vector)
DETACH DELETE n;

// 2. Recreate the practice vector index.
// Dropping this practice index is safe for this tutorial namespace.
DROP INDEX practice_ch07_chunk_embeddings IF EXISTS;

// 3. Create sample Chunk nodes with toy embeddings.
MERGE (c1:Chunk:PracticeChapter07VectorChunk:PracticeChapter07Vector {id: "ch07-c1"})
SET c1.text = "세종대왕은 백성을 위해 훈민정음을 창제했다.",
    c1.source = "chapter07_practice",
    c1.embedding = [0.90, 0.10, 0.20, 0.00]
MERGE (c2:Chunk:PracticeChapter07VectorChunk:PracticeChapter07Vector {id: "ch07-c2"})
SET c2.text = "훈민정음은 백성이 쉽게 읽고 쓸 수 있도록 만든 문자 체계이다.",
    c2.source = "chapter07_practice",
    c2.embedding = [0.85, 0.15, 0.25, 0.05]
MERGE (c3:Chunk:PracticeChapter07VectorChunk:PracticeChapter07Vector {id: "ch07-c3"})
SET c3.text = "집현전은 세종대왕이 설치한 학문 연구 기관이다.",
    c3.source = "chapter07_practice",
    c3.embedding = [0.75, 0.25, 0.35, 0.10]
MERGE (c4:Chunk:PracticeChapter07VectorChunk:PracticeChapter07Vector {id: "ch07-c4"})
SET c4.text = "장영실은 앙부일구와 자격루 같은 과학 기구 발명에 기여했다.",
    c4.source = "chapter07_practice",
    c4.embedding = [0.20, 0.80, 0.10, 0.30]
MERGE (c5:Chunk:PracticeChapter07VectorChunk:PracticeChapter07Vector {id: "ch07-c5"})
SET c5.text = "이순신은 조선 수군을 이끌고 임진왜란에서 활약했다.",
    c5.source = "chapter07_practice",
    c5.embedding = [0.10, 0.20, 0.90, 0.10]
RETURN c1, c2, c3, c4, c5;

// 4. Create a vector index for the toy embeddings.
CREATE VECTOR INDEX practice_ch07_chunk_embeddings IF NOT EXISTS
FOR (c:PracticeChapter07VectorChunk) ON (c.embedding)
OPTIONS { indexConfig: {
  `vector.dimensions`: 4,
  `vector.similarity_function`: 'cosine'
} };

// 5. Confirm the vector index state.
SHOW VECTOR INDEXES YIELD name, state, populationPercent
WHERE name = 'practice_ch07_chunk_embeddings'
RETURN name, state, populationPercent;

// 6. Search for chunks similar to a Sejong/Hunminjeongeum-like query vector.
CALL db.index.vector.queryNodes(
  'practice_ch07_chunk_embeddings',
  3,
  [0.86, 0.14, 0.24, 0.04]
)
YIELD node, score
RETURN node.id AS id, node.text AS text, node.source AS source, score
ORDER BY score DESC;

// 7. Search for chunks similar to a Jang Yeong-sil/science-invention-like query vector.
CALL db.index.vector.queryNodes(
  'practice_ch07_chunk_embeddings',
  3,
  [0.18, 0.82, 0.12, 0.28]
)
YIELD node, score
RETURN node.id AS id, node.text AS text, score
ORDER BY score DESC;

// 8. Check which chunks have embeddings and their dimensions.
MATCH (c:Chunk:PracticeChapter07VectorChunk:PracticeChapter07Vector)
RETURN c.id AS id,
       c.text AS text,
       size(c.embedding) AS embedding_dimensions
ORDER BY id;
