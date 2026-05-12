from collections.abc import Callable

from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from neo4j import GraphDatabase

from util import Neo4jConfig, default_embedding_model, default_llm_model, get_neo4j_config


def test_neo4j_connection(config: Neo4jConfig) -> None:
    print("\n1️⃣ Neo4j 연결 테스트...")

    driver = GraphDatabase.driver(config.uri, auth=config.auth)

    try:
        driver.verify_connectivity()
        with driver.session(database=config.database) as session:
            result = session.run("RETURN 'Hello from Neo4j!' AS message")
            record = result.single()
            message = record["message"] if record else "(no response)"
        print(f"   ✅ Neo4j 연결 성공! database={config.database}")
        print(f"   📝 응답: {message}")
    finally:
        driver.close()


def test_openai_llm() -> None:
    print("\n2️⃣ OpenAI LLM 테스트...")
    llm = ChatOpenAI(model=default_llm_model(), temperature=0)
    response = llm.invoke("1+1=?")
    print(f"   ✅ LLM 응답: {response.content}")


def test_openai_embeddings() -> None:
    print("\n3️⃣ OpenAI Embeddings 테스트...")

    embeddings = OpenAIEmbeddings(model=default_embedding_model())
    vector = embeddings.embed_query("테스트")
    print(f"   ✅ 임베딩 생성 성공! (차원: {len(vector)})")


def test_langchain_neo4j(config: Neo4jConfig) -> None:
    print("\n4️⃣ LangChain-Neo4j 통합 테스트...")

    from langchain_neo4j import Neo4jGraph

    graph = Neo4jGraph(
        url=config.uri,
        username=config.username,
        password=config.password,
        database=config.database,
    )

    schema = graph.get_schema
    print("   ✅ Neo4j Graph 연결 성공!")
    print(f"   📋 현재 스키마: {schema[:100]}..." if schema else "   📋 스키마: (비어있음)")


def run_step(name: str, test_func: Callable[[], None]) -> None:
    try:
        test_func()
    except Exception as e:
        print(f"   ❌ {name} 실패: {e}")


def main() -> None:
    print("=" * 50)
    print("🧪 GraphRAG 환경 통합 테스트")
    print("=" * 50)

    config = get_neo4j_config()

    run_step("Neo4j 연결", lambda: test_neo4j_connection(config))
    run_step("OpenAI LLM", test_openai_llm)
    run_step("OpenAI Embeddings", test_openai_embeddings)
    run_step("LangChain-Neo4j 통합", lambda: test_langchain_neo4j(config))

    print("\n" + "=" * 50)
    print("🎉 테스트 완료!")
    print("=" * 50)


if __name__ == "__main__":
    main()
