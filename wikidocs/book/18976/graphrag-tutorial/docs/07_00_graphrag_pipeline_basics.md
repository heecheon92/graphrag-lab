# 07-00. GraphRAG 파이프라인 기초

Source: <https://wikidocs.net/319222>

## 핵심 요약

Chapter 7은 앞에서 배운 세 가지를 하나의 검색 파이프라인으로 묶습니다.

| 앞에서 배운 것 | Chapter 7에서의 역할 |
| --- | --- |
| 임베딩/벡터 검색 | 질문과 의미가 가까운 문서 청크를 찾습니다. |
| Neo4j/Cypher | 찾은 청크 주변의 엔티티와 관계를 탐색합니다. |
| 지식 그래프 | 단순 텍스트 조각을 사람, 기관, 업적, 발명품 같은 연결된 지식으로 확장합니다. |

가장 중요한 한 문장은 다음과 같습니다.

> GraphRAG는 “비슷한 텍스트 찾기”에서 끝나지 않고, 찾은 텍스트가 가리키는 그래프 관계까지 함께 가져와 답변 컨텍스트를 풍부하게 만드는 방식입니다.

## 전체 그림

**다이어그램: Chapter 7에서 조립하는 GraphRAG 학습 흐름입니다.**

```mermaid
flowchart LR
  Q["사용자 질문"] --> E["질문 임베딩"]
  E --> V["벡터 인덱스 검색"]
  V --> C["관련 Chunk 후보"]
  C --> G["MENTIONS 관계로 그래프 확장"]
  G --> X["청크 + 엔티티 + 관계 컨텍스트"]
  X --> A["LLM 답변"]
```

## 왜 헷갈리는가?

Chapter 7은 비슷한 이름의 개념이 한꺼번에 나옵니다.

| 헷갈리는 개념 | 구분법 |
| --- | --- |
| `embedding` | 텍스트를 숫자 벡터로 바꾼 값입니다. 노드 속성으로 저장됩니다. |
| `vector index` | 저장된 벡터를 빠르게 검색하기 위한 Neo4j 인덱스입니다. |
| `Chunk` | 원문 문서를 검색 가능한 작은 단위로 나눈 노드입니다. |
| `Entity` | 청크 안에 언급된 실제 지식 대상입니다. 예: 세종대왕, 집현전, 훈민정음 |
| `Retriever` | 질문이 들어왔을 때 어떤 방식으로 컨텍스트를 가져올지 정하는 검색기입니다. |
| `GraphRAG` | Retriever 결과를 LLM에 넘겨 최종 답변을 만드는 전체 파이프라인입니다. |

## 학습 순서

1. `docs/07_01_graphrag_architecture.md`에서 아키텍처와 데이터 흐름을 먼저 잡습니다.
2. `docs/07_02_vector_index.md`와 `cypher/07_02_vector_index.cypher`로 벡터 인덱스 검색을 연습합니다.
3. `docs/07_03_graph_vector_retrieval.md`와 `cypher/07_03_graph_vector_retrieval.cypher`로 벡터 결과를 그래프 관계로 확장합니다.
4. Python 구현은 원문에 등장하지만, 이 프로젝트 지침상 이번 Chapter 7 처리에서는 `src/` 파일을 만들지 않습니다. 필요하면 나중에 `src/07_02_prepare_chunks.py`, `src/07_03_vector_cypher_retriever.py` 같은 이름으로 직접 추가하면 됩니다.

## 빠른 복습 카드

| 질문 | 답 |
| --- | --- |
| GraphRAG의 출발점은? | 사용자 질문을 임베딩으로 바꾸는 것 |
| 벡터 인덱스가 찾는 것은? | 질문과 의미적으로 가까운 `Chunk` 노드 |
| 그래프 확장이 찾는 것은? | `Chunk`가 언급한 엔티티와 그 엔티티의 관계 |
| 전통 RAG와 가장 큰 차이는? | 관계 추론과 다단계 연결 정보를 컨텍스트에 넣을 수 있다는 점 |
| Chapter 7의 핵심 실수는? | 벡터 차원, 인덱스 이름, `retrieval_query`의 `node`/`score` 변수를 혼동하는 것 |

## 주의사항

- 원문은 OpenAI 임베딩 예시를 다루므로 실제 Python 실행 시 API 비용이 발생할 수 있습니다.
- 이 프로젝트의 Chapter 7 Cypher 파일은 학습용으로 4차원 장난감 벡터를 사용합니다. 실제 OpenAI `text-embedding-3-small` 기본 벡터는 1536차원입니다.
- Neo4j 버전에 따라 벡터 검색 문법이 다를 수 있습니다. Chapter 원문은 `db.index.vector.queryNodes()` 스타일을 설명하고, Neo4j 2026 계열에서는 `SEARCH` 절을 사용할 수 있습니다.
