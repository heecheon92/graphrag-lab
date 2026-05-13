# Source: https://wikidocs.net/319228

import logging
import os

from dotenv import load_dotenv

load_dotenv()

# Hugging Face download settings must be set before sentence_transformers loads.
if os.getenv("HF_TOKEN") and not os.getenv("HUGGINGFACE_HUB_TOKEN"):
    os.environ["HUGGINGFACE_HUB_TOKEN"] = os.environ["HF_TOKEN"]
os.environ.setdefault("HF_HUB_DISABLE_XET", "1")

# Neo4j 6.x prints deprecation notifications for db.index.vector.queryNodes().
# Keep this tutorial output focused on the search/reranking results.
logging.getLogger("neo4j.notifications").setLevel(logging.ERROR)

from util import get_neo4j_config
from langchain_openai import OpenAIEmbeddings
from langchain_neo4j import Neo4jGraph

config = get_neo4j_config()

graph = Neo4jGraph(
    url=config.uri,
    username=config.username,
    password=config.password,
    database=config.database
)

embeddings = OpenAIEmbeddings(model="text-embedding-3-small")


def hybrid_search(query, vector_weight=0.5, fulltext_weight=0.5, k=5):
    """가중치 조정 가능한 하이브리드 검색"""

    # 질문 임베딩
    query_embedding = embeddings.embed_query(query)

    result = graph.query("""
        // 벡터 검색
        CALL db.index.vector.queryNodes('chunk_embeddings', $k * 2, $embedding)
        YIELD node AS vNode, score AS vScore

        WITH collect({node: vNode, score: vScore, source: 'vector'}) AS vectorResults

        // 전문 검색
        CALL db.index.fulltext.queryNodes('chunk_fulltext', $query)
        YIELD node AS fNode, score AS fScore

        WITH vectorResults, collect({node: fNode, score: fScore, source: 'fulltext'}) AS fulltextResults

        // 결과 통합
        WITH vectorResults + fulltextResults AS allResults
        UNWIND allResults AS result

        WITH result.node AS node,
             CASE result.source
                 WHEN 'vector' THEN result.score * $vectorWeight
                 ELSE result.score * $fulltextWeight
             END AS weightedScore,
             result.source AS source

        // 같은 노드의 점수 합산
        WITH node, sum(weightedScore) AS totalScore, collect(source) AS sources

        RETURN node.id AS id,
               node.text AS text,
               totalScore,
               sources
        ORDER BY totalScore DESC
        LIMIT $k
    """, params={
        "embedding": query_embedding,
        "query": query,
        "k": k,
        "vectorWeight": vector_weight,
        "fulltextWeight": fulltext_weight
    })

    return result


def score_of(row, score_key="totalScore"):
    """출력용 점수 키를 통일해서 가져옵니다."""
    return row.get(score_key, row.get("score", 0))


def text_of(row):
    """출력용 텍스트 키를 통일해서 가져옵니다."""
    return row.get("text", "")


def print_results(title, results, limit=3, score_key="totalScore"):
    """검색 결과가 비어 있어도 상태를 확인할 수 있게 출력합니다."""
    print(f"\n=== {title} ===")
    print(f"검색 결과 수: {len(results)}")

    if not results:
        print("검색 결과 없음")
        return

    for r in results[:limit]:
        print(f"[{score_of(r, score_key):.3f}] {text_of(r)[:50]}...")


# 테스트: 다양한 가중치로 비교
query = "세종대왕이 설치한 학문 연구 기관에서 일한 사람"

results = hybrid_search(query, vector_weight=0.8, fulltext_weight=0.2)
print_results("벡터 중심 (0.8:0.2)", results)

results = hybrid_search(query, vector_weight=0.5, fulltext_weight=0.5)
print_results("균형 (0.5:0.5)", results)

results = hybrid_search(query, vector_weight=0.2, fulltext_weight=0.8)
print_results("키워드 중심 (0.2:0.8)", results)


from sentence_transformers import CrossEncoder

# 재순위화 모델 로드
reranker_model = os.getenv("RERANKER_MODEL", "cross-encoder/ms-marco-MiniLM-L-6-v2")
reranker = CrossEncoder(reranker_model, token=os.getenv("HF_TOKEN"))


def rerank_results(query, results, top_k=5):
    """검색 결과 재순위화"""

    if not results:
        return []

    # (질문, 문서) 쌍 생성
    pairs = [(query, r['text']) for r in results]

    # 재순위화 점수 계산
    scores = reranker.predict(pairs)

    # 점수로 정렬
    ranked = sorted(
        zip(results, scores),
        key=lambda x: x[1],
        reverse=True
    )

    return [(r, s) for r, s in ranked[:top_k]]


# 사용 예
initial_results = hybrid_search(query, k=10)
reranked = rerank_results(query, initial_results, top_k=5)

reranked_results = [
    {"id": result.get("id"), "text": result["text"], "score": score}
    for result, score in reranked
]
print_results("재순위화 결과", reranked_results, limit=5, score_key="score")



"""
Sample Result:

=== 벡터 중심 (0.8:0.2) ===
검색 결과 수: 5
[1.140] 집현전은 세종대왕이 설치한 학문 연구 기관이다. 성삼문, 박팽년 등 많은 학자들이 이곳에서...
[0.601] 훈민정음은 1443년에 세종대왕이 창제한 한국의 문자 체계이다. 백성들이 쉽게 글을 읽고 ...
[0.556] 장영실은 조선시대 최고의 과학자이다. 세종대왕과 함께 측우기, 앙부일구, 자격루 등 다양한...

=== 균형 (0.5:0.5) ===
검색 결과 수: 5
[1.602] 집현전은 세종대왕이 설치한 학문 연구 기관이다. 성삼문, 박팽년 등 많은 학자들이 이곳에서...
[0.521] 훈민정음은 1443년에 세종대왕이 창제한 한국의 문자 체계이다. 백성들이 쉽게 글을 읽고 ...
[0.347] 장영실은 조선시대 최고의 과학자이다. 세종대왕과 함께 측우기, 앙부일구, 자격루 등 다양한...

=== 키워드 중심 (0.2:0.8) ===
검색 결과 수: 5
[2.063] 집현전은 세종대왕이 설치한 학문 연구 기관이다. 성삼문, 박팽년 등 많은 학자들이 이곳에서...
[0.442] 훈민정음은 1443년에 세종대왕이 창제한 한국의 문자 체계이다. 백성들이 쉽게 글을 읽고 ...
[0.139] 장영실은 조선시대 최고의 과학자이다. 세종대왕과 함께 측우기, 앙부일구, 자격루 등 다양한...
Loading weights: 100%|███████████████████████████████████████████████████████████████████████████████████████| 105/105 [00:00<00:00, 14863.88it/s]

=== 재순위화 결과 ===
[8.104] 장영실은 조선시대 최고의 과학자이다. 세종대왕과 함께 측우기, 앙부일구, 자격루 등 다양한...
[8.088] 세종대왕(1397-1450)은 조선의 제4대 왕이다. 그는 백성을 위한 정치를 펼쳤으며, ...
[7.995] 집현전은 세종대왕이 설치한 학문 연구 기관이다. 성삼문, 박팽년 등 많은 학자들이 이곳에서...
[7.936] 정조(1752-1800)는 조선의 제22대 왕이다. 규장각을 설립하고 정약용 등 실학자들을...
[7.855] 훈민정음은 1443년에 세종대왕이 창제한 한국의 문자 체계이다. 백성들이 쉽게 글을 읽고 ...
"""
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

llm = ChatOpenAI(model="gpt-5.4-mini", temperature=0.7)

expansion_prompt = ChatPromptTemplate.from_messages([
    ("system", """사용자의 검색 질문을 분석하고, 관련된 검색어를 추가로 생성하세요.
    원래 질문의 의도를 유지하면서 동의어, 관련 개념을 포함하세요.
    3개의 확장된 검색어를 생성하세요."""),
    ("human", "질문: {query}")
])

def expand_query(query):
    """쿼리 확장"""
    response = llm.invoke(expansion_prompt.format_messages(query=query))
    return response.content

# 예시
original = "세종대왕이 만든 것"
expanded = expand_query(original)
print("\n=== 쿼리 확장 ===")
print(f"원래 질문: {original}")
print("확장 검색어:")
print(expanded)


hyde_prompt = ChatPromptTemplate.from_messages([
    ("system", """질문에 대한 이상적인 답변 문서를 작성하세요.
    실제 정보가 아니어도 됩니다. 형식과 스타일만 맞추세요.
    100자 이내로 작성하세요."""),
    ("human", "질문: {query}")
])

def hyde_search(query, k=5):
    """HyDE 기반 검색"""
    # 가상 문서 생성
    hypothetical = llm.invoke(hyde_prompt.format_messages(query=query))

    print(f"\n=== 가상 문서 중간 결과물 ===")
    print(hypothetical.content)

    # 가상 문서로 검색
    embedding = embeddings.embed_query(hypothetical.content) # type: ignore

    results = graph.query("""
        CALL db.index.vector.queryNodes('chunk_embeddings', $k, $embedding)
        YIELD node, score
        RETURN node.id AS id, node.text AS text, score
    """, params={"k": k, "embedding": embedding})

    return results

# 테스트
results = hyde_search("조선시대 과학 발전")
print_results("HyDE 검색 결과", results, limit=5, score_key="score")



def result_ids(results):
    """검색 결과에서 평가용 id 목록만 추출합니다."""
    return [r["id"] for r in results if r.get("id")]


def calculate_recall(retrieved_ids, relevant_ids):
    """재현율: 관련 문서 중 검색된 비율"""
    if not relevant_ids:
        return 0
    found = len(set(retrieved_ids) & set(relevant_ids))
    return found / len(relevant_ids)


def calculate_precision(retrieved_ids, relevant_ids):
    """정밀도: 검색된 문서 중 관련된 비율"""
    if not retrieved_ids:
        return 0
    found = len(set(retrieved_ids) & set(relevant_ids))
    return found / len(retrieved_ids)


def print_quality(title, results, relevant_ids):
    """실제 검색 결과와 정답 id 목록을 비교해 품질을 출력합니다."""
    retrieved_ids = result_ids(results)
    print(f"\n=== {title} 품질 평가 ===")
    print(f"검색 id: {retrieved_ids}")
    print(f"정답 id: {relevant_ids}")
    print(f"재현율: {calculate_recall(retrieved_ids, relevant_ids):.2f}")
    print(f"정밀도: {calculate_precision(retrieved_ids, relevant_ids):.2f}")


# 예시: 현재 query의 정답 근거 청크는 집현전 chunk_2라고 가정합니다.
relevant_ids = ["chunk_2"]
print_quality("균형 하이브리드", initial_results, relevant_ids)
print_quality("재순위화", reranked_results, relevant_ids)
print_quality("HyDE", results, ["chunk_3"])
