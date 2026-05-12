from neo4j import GraphDatabase

from util import get_neo4j_config


def main():
    config = get_neo4j_config()

    driver = GraphDatabase.driver(config.uri, auth=config.auth)

    try:
        with driver.session(database=config.database) as session:
            # 노드 생성
            session.run("""
                CREATE (p:Person {name: '김철수', age: 30})
                CREATE (c:Company {name: 'AI 스타트업'})
                CREATE (p)-[:WORKS_AT]->(c)
            """)
            print(f"✅ 데이터 생성 완료! database={config.database}")

            # 데이터 조회
            result = session.run("""
                MATCH (p:Person)-[:WORKS_AT]->(c:Company)
                RETURN p.name AS person, c.name AS company
            """)

            for record in result:
                print(f"👤 {record['person']}님은 {record['company']}에서 일합니다.")
    finally:
        driver.close()


if __name__ == "__main__":
    main()
