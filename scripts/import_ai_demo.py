from pathlib import Path
import csv
from neo4j import GraphDatabase

ROOT = Path(__file__).resolve().parents[1]

KG_DIR = ROOT / "data" / "kg" / "artificial-intelligence"
DEMO_DIR = ROOT / "data" / "demo" / "artificial-intelligence"

NEO4J_URI = "bolt://localhost:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "devpassword"
NEO4J_DATABASE = "neo4j"


def read_csv(path):
    with path.open("r", encoding="utf-8-sig", newline="") as file:
        return list(csv.DictReader(file))


def to_bool(value):
    return str(value).strip().lower() == "true"


def reset_database(session):
    session.run("MATCH (n) DETACH DELETE n")


def create_constraints(session):
    session.run("""
    CREATE CONSTRAINT concept_id IF NOT EXISTS
    FOR (c:Concept) REQUIRE c.concept_id IS UNIQUE
    """)
    session.run("""
    CREATE CONSTRAINT question_id IF NOT EXISTS
    FOR (q:Question) REQUIRE q.question_id IS UNIQUE
    """)
    session.run("""
    CREATE CONSTRAINT student_id IF NOT EXISTS
    FOR (s:Student) REQUIRE s.student_id IS UNIQUE
    """)


def import_concepts(session):
    concepts = read_csv(KG_DIR / "knowledge_points.csv")

    for row in concepts:
        session.run(
            """
            MERGE (c:Concept {concept_id: $concept_id})
            SET c.label = $label,
                c.chapter = $chapter,
                c.description = $description
            """,
            **row
        )

    print(f"Imported {len(concepts)} concepts")


def import_relations(session):
    relations = read_csv(KG_DIR / "relations.csv")

    for row in relations:
        session.run(
            """
            MATCH (source:Concept {concept_id: $source_id})
            MATCH (target:Concept {concept_id: $target_id})
            MERGE (source)-[r:REQUIRES]->(target)
            SET r.explanation = $explanation
            """,
            **row
        )

    print(f"Imported {len(relations)} prerequisite relations")


def import_questions(session):
    questions = read_csv(KG_DIR / "questions.csv")

    for row in questions:
        session.run(
            """
            MERGE (q:Question {question_id: $question_id})
            SET q.question_text = $question_text,
                q.difficulty = $difficulty
            WITH q
            MATCH (c:Concept {concept_id: $concept_id})
            MERGE (q)-[:EVALUATES]->(c)
            """,
            **row
        )

    print(f"Imported {len(questions)} questions")


def import_students(session):
    students = read_csv(DEMO_DIR / "students.csv")

    for row in students:
        session.run(
            """
            MERGE (s:Student {student_id: $student_id})
            SET s.cohort = $cohort
            """,
            **row
        )

    print(f"Imported {len(students)} students")


def import_attempts(session):
    attempts = read_csv(DEMO_DIR / "student_attempts.csv")

    for row in attempts:
        session.run(
            """
            MATCH (s:Student {student_id: $student_id})
            MATCH (q:Question {question_id: $question_id})
            MERGE (s)-[a:ANSWERED]->(q)
            SET a.is_correct = $is_correct,
                a.score = $score,
                a.error_type = $error_type,
                a.time_seconds = $time_seconds
            """,
            student_id=row["student_id"],
            question_id=row["question_id"],
            is_correct=to_bool(row["is_correct"]),
            score=float(row["score"]),
            error_type=row["error_type"],
            time_seconds=int(row["time_seconds"])
        )

    print(f"Imported {len(attempts)} student attempts")


def main():
    driver = GraphDatabase.driver(
        NEO4J_URI,
        auth=(NEO4J_USER, NEO4J_PASSWORD)
    )

    with driver.session(database=NEO4J_DATABASE) as session:
        reset_database(session)
        create_constraints(session)
        import_concepts(session)
        import_relations(session)
        import_questions(session)
        import_students(session)
        import_attempts(session)

    driver.close()
    print("Neo4j import completed")


if __name__ == "__main__":
    main()