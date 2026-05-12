from neo4j import GraphDatabase

from util import get_neo4j_config


def main():
    config = get_neo4j_config()

    driver = GraphDatabase.driver(config.uri, auth=config.auth)

    try:
        driver.verify_connectivity()
        print("✅ Neo4j 연결 성공!")

        with driver.session(database=config.database) as session:
            result = session.run("RETURN 'Hello from Python!' AS message")
            record = result.single()
            message = record["message"] if record else "(no response)"
            print(f"📝 응답: {message}")
            print(f"🗄️ database={config.database}")

    except Exception as e:
        print(f"❌ 연결 실패: {e}")
        raise

    finally:
        driver.close()


if __name__ == "__main__":
    main()
