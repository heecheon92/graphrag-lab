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

## 주의사항

- `03_test_neo4j_data.py`는 Neo4j 데이터베이스에 실제 노드와 관계를 생성합니다.
- OpenAI를 사용하는 스크립트는 API 호출 비용이 발생할 수 있습니다.
- `04_03_03_rag_complete.py`, `04_03_04_rag_limitations.py`는 LLM 응답 생성을 포함하므로 실행 시 OpenAI API 호출이 발생합니다.
- 스크립트를 `src/` 안에서 직접 실행해도 `.env`는 프로젝트 루트의 파일을 읽도록 구성되어 있습니다.

## 권장 학습 순서

1. `03_test_all.py`로 환경이 정상인지 확인합니다.
2. `04_01_01_embedding_basic.py`, `04_01_02_embedding_many.py`로 임베딩의 형태를 확인합니다.
3. `04_02_01_similarity_manual.py`, `04_02_02_find_similar.py`로 벡터 유사도와 검색 원리를 이해합니다.
4. `04_02_03_vector_store_basic.py`, `04_03_01_rag_chunking.py`, `04_03_02_rag_vectorstore.py`로 LangChain 기반 검색 흐름을 익힙니다.
5. `04_03_03_rag_complete.py`로 기본 RAG 체인을 실행합니다.
6. `04_03_04_rag_limitations.py`로 전통 RAG의 한계를 관찰합니다.
