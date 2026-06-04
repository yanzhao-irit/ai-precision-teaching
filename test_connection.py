from neo4j import GraphDatabase

uri = "bolt://localhost:7687"
user = "neo4j"
password = "Bpa25072020!"

driver = GraphDatabase.driver(uri, auth=(user, password))

with driver.session() as session:
    result = session.run("RETURN 'Connexion OK' AS message")
    for record in result:
        print(record["message"])

driver.close()