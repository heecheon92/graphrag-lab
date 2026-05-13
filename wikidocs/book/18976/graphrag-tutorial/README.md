# GraphRAG Tutorial

이 폴더는 GraphRAG를 학습하기 위한 실습용 Python 프로젝트입니다.  
OpenAI 임베딩, 벡터 검색, 기본 RAG 체인, Neo4j 연결 테스트를 단계별 스크립트로 확인합니다.

## 출처

이 프로젝트의 소스 자료는 WikiDocs의 [GraphRAG Tutorial](https://wikidocs.net/book/18976)에서 가져왔습니다.

## 실행 전 준비

이 프로젝트는 `uv` 기반 Python 프로젝트입니다. 프로젝트 루트에서 실행하세요.

```bash
cd wikidocs/book/18976/graphrag-tutorial
uv sync
```

`.env` 파일에는 최소한 다음 값이 필요합니다.

```env
OPENAI_API_KEY=
OPENAI_DEFAULT_LLM_MODEL=gpt-4o-mini
OPENAI_DEFAULT_EMBEDDING_MODEL=text-embedding-3-small
NEO4J_URI=bolt://localhost:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=
NEO4J_DATABASE=tutorial-db
```

실제 비밀값은 `.env`에 넣고, `.env`는 Git에 커밋하지 않습니다. 공유용 예시는 `.env.example`을 사용합니다.

## 실행 방법

각 스크립트는 프로젝트 루트에서 다음 형식으로 실행합니다.

```bash
uv run python src/<파일명>.py
```

예시:

```bash
uv run python src/03_test_all.py
uv run python src/04_03_03_rag_complete.py
```

Cypher 예제는 Neo4j Browser에서 실행합니다. `docs/` 노트에는 설명, `cypher` 코드 블록,
가능한 경우 Mermaid 그래프가 함께 들어 있고, `cypher/` 파일에는 실행용 쿼리만 모았습니다.
Browser 전용 명령어(`:play movies` 등)는 `.cypher` 파일이 아니라 `docs/` 노트에 정리되어 있습니다.

## 데이터 파일

`src/` 스크립트 일부는 다음 샘플 문서 데이터를 사용합니다.

- `data/documents.py`: 세종대왕, 정조, 이순신, 집현전 등에 대한 짧은 한국어 문서 목록

## src 폴더 파일 설명

### 03 계열: 환경 및 연결 테스트

| 파일 | 역할 | 주요 확인 내용 |
| --- | --- | --- |
| `03_test_neo4j.py` | Neo4j 연결 테스트 | `.env`의 Neo4j 접속 정보로 `NEO4J_DATABASE`에 접속하고 간단한 Cypher 쿼리를 실행합니다. |
| `03_test_neo4j_data.py` | Neo4j 데이터 생성 테스트 | `Person`, `Company`, `WORKS_AT` 관계를 생성하고 조회합니다. **실제 DB에 데이터를 씁니다.** |
| `03_test_openai.py` | OpenAI Chat 모델 테스트 | ChatOpenAI로 간단한 한국어 응답을 받아 OpenAI API 키와 LLM 호출을 확인합니다. |
| `03_test_embedding.py` | OpenAI 임베딩 테스트 | `text-embedding-3-small`로 문장을 임베딩하고 벡터 차원과 앞부분 값을 출력합니다. |
| `03_test_all.py` | 통합 환경 테스트 | Neo4j 연결, OpenAI LLM, OpenAI Embeddings, LangChain-Neo4j 연결을 한 번에 확인합니다. |

### 04 계열: 임베딩, 벡터 검색, RAG 실습

| 파일 | 역할 | 주요 내용 |
| --- | --- | --- |
| `04_01_01_embedding_basic.py` | 단일 문장 임베딩 기초 | 한 문장을 임베딩으로 변환하고 벡터 차원과 일부 값을 출력합니다. |
| `04_01_02_embedding_many.py` | 여러 문장 임베딩 | 여러 텍스트를 `embed_documents()`로 한 번에 임베딩합니다. |
| `04_02_01_similarity_manual.py` | 코사인 유사도 직접 계산 | NumPy로 코사인 유사도를 직접 계산해 문장 간 의미적 유사도를 비교합니다. |
| `04_02_02_find_similar.py` | 수동 벡터 검색 | 문서 목록을 임베딩한 뒤 질문 벡터와의 유사도를 계산해 상위 문서를 찾습니다. |
| `04_02_03_vector_store_basic.py` | LangChain 인메모리 벡터 저장소 기초 | `InMemoryVectorStore`에 문서를 넣고 `similarity_search()`로 검색합니다. |
| `04_03_01_rag_chunking.py` | RAG 문서 청킹 | `data/documents.py`의 문서를 `RecursiveCharacterTextSplitter`로 청크 단위로 나눕니다. |
| `04_03_02_rag_vectorstore.py` | 청킹 + 벡터 저장소 검색 | 문서를 청크로 나눈 뒤 인메모리 벡터 저장소에 넣고 관련 청크를 검색합니다. |
| `04_03_03_rag_complete.py` | 완성형 기본 RAG 파이프라인 | 문서 청킹, 임베딩, 벡터 검색, 프롬프트, LLM 응답 생성을 하나의 RAG 체인으로 구성합니다. |
| `04_03_04_rag_limitations.py` | 전통 RAG 한계 실험 | 관계 추론, 다단계 추론, 비교, 시간순 질문처럼 단순 벡터 검색 RAG가 약한 질문을 테스트합니다. |

## Chapter 05: Neo4j와 Cypher 기초

Chapter 5의 5-1~5-3은 Neo4j Browser와 Cypher 중심이라 `docs/`와 `cypher/`에 분리했습니다.
5-4는 Python에서 Neo4j를 연결/조회/생성하는 실습 스크립트로 `src/`에 정리했습니다.

| 파일 | 역할 |
| --- | --- |
| `docs/05_00_neo4j_cypher_basics.md` | Chapter 5 전체 개요와 Cypher 기본 패턴 |
| `docs/05_01_neo4j_browser.md` | Neo4j Browser 사용법, Browser 명령, 실습 체크리스트 |
| `cypher/05_01_neo4j_browser.cypher` | 영화 샘플 데이터 확인과 그래프 시각화 쿼리 |
| `docs/05_02_cypher_read.md` | `MATCH`, `WHERE`, 관계 탐색, 집계 읽기 패턴 |
| `cypher/05_02_cypher_read.cypher` | 읽기 전용 Cypher 실습 쿼리 |
| `docs/05_03_cypher_write.md` | `CREATE`, `MERGE`, `SET`, `DELETE` 쓰기 패턴과 안전 메모 |
| `cypher/05_03_cypher_write.cypher` | 연습용 데이터 생성/수정/삭제 쿼리 |
| `src/05_04_01_neo4j_basic.py` | Python Neo4j 드라이버 연결 확인 |
| `src/05_04_02_neo4j_query.py` | Python Neo4j 드라이버로 읽기/쓰기 트랜잭션 실행 |
| `src/05_04_03_langchain_neo4j_basic.py` | LangChain `Neo4jGraph` 연결, 스키마 확인, 파라미터 쿼리 |
| `src/05_04_04_build_korean_history_graph.py` | 한국 역사 예제 지식 그래프 생성 |

## Chapter 06: 첫 번째 지식 그래프 만들기

Chapter 6은 스키마 설계와 세종대왕 중심 지식 그래프 수동 구축을 다룹니다.
스키마/검증 쿼리는 `docs/`와 `cypher/`에, Python으로 같은 그래프를 만드는 예제는 `src/`에 정리했습니다.

| 파일 | 역할 |
| --- | --- |
| `docs/06_00_first_knowledge_graph.md` | Chapter 6 전체 개요와 구축 흐름 |
| `docs/06_01_schema_design.md` | 지식 그래프 스키마 설계, 관계 유형, 제약조건 정리 |
| `cypher/06_01_schema_design.cypher` | 스키마 확인과 제약조건 생성 쿼리 |
| `docs/06_02_manual_knowledge_graph.md` | 세종대왕 중심 수동 지식 그래프 구축 노트 |
| `cypher/06_02_manual_knowledge_graph.cypher` | 수동 그래프 구축, 검증, 질문 응답 Cypher |
| `src/06_02_01_build_sejong_graph.py` | LangChain `Neo4jGraph`로 Chapter 6 그래프 구축 |

## Chapter 07: GraphRAG 파이프라인 기초

Chapter 7은 벡터 검색, Neo4j 지식 그래프, Retriever 전략을 결합해 GraphRAG 검색 흐름을 구성합니다.
원문에는 Python 예제가 포함되어 있지만, 이번 Chapter 7 정리는 프로젝트 지침에 따라 `docs/`, `cypher/`, `README.md`만 업데이트했습니다.

| 파일 | 역할 |
| --- | --- |
| `docs/07_00_graphrag_pipeline_basics.md` | Chapter 7 전체 개요, 헷갈리는 개념 구분, 복습 카드 |
| `docs/07_01_graphrag_architecture.md` | GraphRAG 아키텍처, 인덱싱/검색 단계, Retriever 종류 정리 |
| `docs/07_02_vector_index.md` | Neo4j 벡터 인덱스 개념, 차원/유사도/검색 흐름, Python 구현 메모 |
| `cypher/07_02_vector_index.cypher` | 4차원 장난감 벡터로 벡터 인덱스 생성과 검색을 연습하는 Cypher |
| `docs/07_03_graph_vector_retrieval.md` | VectorCypher/Hybrid Retriever, RRF, 컨텍스트 확장 패턴 정리 |
| `cypher/07_03_graph_vector_retrieval.cypher` | 벡터 검색 결과를 `MENTIONS` 관계와 엔티티 주변 관계로 확장하는 Cypher |

## Chapter 08: GraphRAG 고급 기법

Chapter 8은 하이브리드 검색, 컨텍스트 확장, Text2Cypher, 성능 최적화처럼 GraphRAG 품질과 운영성을 높이는 기법을 다룹니다.
이번 문서화 범위는 8-4 성능 최적화 페이지이며, 프로젝트 지침에 따라 `docs/`, `cypher/`, `README.md`만 업데이트했습니다.

| 파일 | 역할 |
| --- | --- |
| `docs/08_04_performance_optimization.md` | 인덱스 튜닝, 쿼리 최적화, 배치/캐싱/모니터링 복습 노트 |
| `cypher/08_04_performance_optimization.cypher` | 인덱스 점검/생성, EXPLAIN/PROFILE, 검색 성능 점검용 Cypher |

## 주의사항

- `03_test_neo4j_data.py`는 Neo4j 데이터베이스에 실제 노드와 관계를 생성합니다.
- OpenAI를 사용하는 스크립트는 API 호출 비용이 발생할 수 있습니다.
- `04_03_03_rag_complete.py`, `04_03_04_rag_limitations.py`는 LLM 응답 생성을 포함하므로 실행 시 OpenAI API 호출이 발생합니다.
- `cypher/05_03_cypher_write.cypher`는 Neo4j 데이터베이스에 연습용 노드와 관계를 생성/수정/삭제합니다.
- `src/05_04_02_neo4j_query.py`, `src/05_04_04_build_korean_history_graph.py`는 Neo4j 데이터베이스에 데이터를 씁니다.
- `cypher/06_01_schema_design.cypher`는 Neo4j 제약조건을 생성할 수 있습니다.
- `cypher/06_02_manual_knowledge_graph.cypher`, `src/06_02_01_build_sejong_graph.py`는 Neo4j 데이터베이스에 Chapter 6 연습 그래프를 씁니다.
- `cypher/07_02_vector_index.cypher`는 `PracticeChapter07Vector` 라벨과 `practice_ch07_chunk_embeddings` 인덱스를 생성/삭제합니다.
- `cypher/07_03_graph_vector_retrieval.cypher`는 `PracticeChapter07GraphVector` 라벨과 Chapter 7 연습용 벡터/전문 검색 인덱스를 생성/삭제합니다.
- Chapter 7 Cypher 예제는 Browser 실행용 4차원 장난감 벡터를 사용합니다. 실제 OpenAI 임베딩과 섞지 마세요.
- `cypher/08_04_performance_optimization.cypher`는 `chunk_source`, `chunk_id` 같은 성능 점검용 인덱스를 생성할 수 있습니다.
- 스크립트를 `src/` 안에서 직접 실행해도 `.env`는 프로젝트 루트의 파일을 읽도록 구성되어 있습니다.

## 권장 학습 순서

1. `03_test_all.py`로 환경이 정상인지 확인합니다.
2. `04_01_01_embedding_basic.py`, `04_01_02_embedding_many.py`로 임베딩의 형태를 확인합니다.
3. `04_02_01_similarity_manual.py`, `04_02_02_find_similar.py`로 벡터 유사도와 검색 원리를 이해합니다.
4. `04_02_03_vector_store_basic.py`, `04_03_01_rag_chunking.py`, `04_03_02_rag_vectorstore.py`로 LangChain 기반 검색 흐름을 익힙니다.
5. `04_03_03_rag_complete.py`로 기본 RAG 체인을 실행합니다.
6. `04_03_04_rag_limitations.py`로 전통 RAG의 한계를 관찰합니다.
7. `docs/05_00_neo4j_cypher_basics.md`부터 Chapter 5 노트를 읽고, `cypher/05_*.cypher`를 Neo4j Browser에서 실행합니다.
8. `src/05_04_*.py`로 Python과 LangChain에서 Neo4j를 사용하는 흐름을 확인합니다.
9. `docs/06_00_first_knowledge_graph.md`부터 Chapter 6 노트를 읽고, `cypher/06_*.cypher` 또는 `src/06_02_01_build_sejong_graph.py`로 첫 지식 그래프를 구축합니다.
10. `docs/07_00_graphrag_pipeline_basics.md`와 `docs/07_01_graphrag_architecture.md`로 GraphRAG 전체 구조를 복습합니다.
11. `cypher/07_02_vector_index.cypher`로 벡터 인덱스 검색을, `cypher/07_03_graph_vector_retrieval.cypher`로 그래프 확장 검색을 Neo4j Browser에서 확인합니다.
12. `docs/08_04_performance_optimization.md`로 GraphRAG 성능 병목 지점을 정리하고, `cypher/08_04_performance_optimization.cypher`로 인덱스/쿼리 계획을 점검합니다.
