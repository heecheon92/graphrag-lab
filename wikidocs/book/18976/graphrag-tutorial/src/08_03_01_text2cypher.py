from util import get_neo4j_config, default_llm_model
from langchain_neo4j import Neo4jGraph, GraphCypherQAChain
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
import rich as r

config = get_neo4j_config()

# Neo4j 연결
graph = Neo4jGraph(
    url=config.uri,
    username=config.username,
    password=config.password,
    database=config.database
)

# 그래프 스키마 확인
print(graph.schema)

# LLM 설정
llm = ChatOpenAI(model=default_llm_model(), temperature=0)

# Chain 생성
chain = GraphCypherQAChain.from_llm(
    llm=llm,
    graph=graph,
    verbose=True,  # 생성된 Cypher 확인
    allow_dangerous_requests=True  # 실제 쿼리 실행 허용
)

# 간단한 질문
response = chain.invoke({
    "query": "세종대왕과 관련된 모든 사람을 알려줘"
})
# print(response["result"])
r.print(response)

# 복잡한 질문
response = chain.invoke({
    "query": "조선시대 과학자 중 2개 이상의 발명품을 만든 사람은?"
})
# print(response["result"])
r.print(response)