"""
Import the demo Artificial Intelligence knowledge graph into Neo4j.

This script is intentionally simple and explainable:
- concepts become (:Concept)
- questions become (:Question)
- prerequisites become (:Concept)-[:REQUIRES]->(:Concept)
- demo student answers become (:Student)-[:ANSWERED]->(:Question)
"""

from pathlib import Path
import csv
from neo4j import GraphDatabase

from src.utils.config import PROJECT_ROOT, NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD, NEO4J_DATABASE


KG_DIR = PROJECT_ROOT / "data" / "kg" / "artificial-intelligence"
DEMO_DIR = PROJECT_ROOT / "data" / "demo" / "artificial-intelligence"


def read_csv(path: Path) -> list[dict]:
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def to_bool(value: str) -> bool:
    return str(value).strip() in {"1", "true", "True", "TRUE", "yes", "YES"}


def import_ai_kg(reset: bool = False) -> None:
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

    concepts = read_csv(KG_DIR / "knowledge_points.csv")
    relations = read_csv(KG_DIR / "relations.csv")
    misconceptions = read_csv(KG_DIR / "misconceptions.csv")
    questions = read_csv(KG_DIR / "questions.csv")
    students = read_csv(DEMO_DIR / "students.csv")
    attempts = read_csv(DEMO_DIR / "student_attempts.csv")
    video_activity = read_csv(DEMO_DIR / "video_activity.csv")

    with driver.session(database=NEO4J_DATABASE) as session:
        if reset:
            session.run("MATCH (n) DETACH DELETE n")

        session.run("CREATE CONSTRAINT concept_id_unique IF NOT EXISTS FOR (c:Concept) REQUIRE c.concept_id IS UNIQUE")
        session.run("CREATE CONSTRAINT question_id_unique IF NOT EXISTS FOR (q:Question) REQUIRE q.question_id IS UNIQUE")
        session.run("CREATE CONSTRAINT student_id_unique IF NOT EXISTS FOR (s:Student) REQUIRE s.student_id IS UNIQUE")
        session.run("CREATE CONSTRAINT misconception_id_unique IF NOT EXISTS FOR (m:Misconception) REQUIRE m.misconception_id IS UNIQUE")

        for row in concepts:
            session.run(
                """
                MERGE (c:Concept {concept_id: $concept_id})
                SET c.label = $label,
                    c.chapter = $chapter,
                    c.description = $description,
                    c.domain = "Artificial Intelligence"
                """,
                **row,
            )

        for row in relations:
            session.run(
                """
                MATCH (source:Concept {concept_id: $source_id})
                MATCH (target:Concept {concept_id: $target_id})
                CALL {
                    WITH source, target
                    WITH source, target
                    WHERE $relation_type = "REQUIRES"
                    MERGE (source)-[r:REQUIRES]->(target)
                    SET r.explanation = $explanation
                    RETURN count(*) AS _
                    UNION
                    WITH source, target
                    WITH source, target
                    WHERE $relation_type = "IS_PART_OF"
                    MERGE (source)-[r:IS_PART_OF]->(target)
                    SET r.explanation = $explanation
                    RETURN count(*) AS _
                }
                RETURN count(*) AS done
                """,
                **row,
            )

        for row in misconceptions:
            session.run(
                """
                MERGE (m:Misconception {misconception_id: $misconception_id})
                SET m.label = $label, m.description = $description
                WITH m
                MATCH (c:Concept {concept_id: $concept_id})
                MERGE (m)-[:ABOUT]->(c)
                """,
                **row,
            )

        for row in questions:
            prereq_ids = [x.strip() for x in row["prerequisite_concept_ids"].split(";") if x.strip()]
            session.run(
                """
                MERGE (q:Question {question_id: $question_id})
                SET q.question_text = $question_text,
                    q.question_type = $question_type,
                    q.difficulty = toInteger($difficulty)
                WITH q
                MATCH (c:Concept {concept_id: $primary_concept_id})
                MERGE (q)-[:EVALUATES]->(c)
                """,
                **row,
            )
            for prereq_id in prereq_ids:
                session.run(
                    """
                    MATCH (q:Question {question_id: $question_id})
                    MATCH (pre:Concept {concept_id: $prereq_id})
                    MERGE (q)-[:REQUIRES]->(pre)
                    """,
                    question_id=row["question_id"],
                    prereq_id=prereq_id,
                )

        for row in students:
            session.run(
                """
                MERGE (s:Student {student_id: $student_id})
                SET s.cohort = $cohort, s.is_demo = true
                """,
                **row,
            )

        for row in attempts:
            session.run(
                """
                MATCH (s:Student {student_id: $student_id})
                MATCH (q:Question {question_id: $question_id})
                MERGE (s)-[a:ANSWERED]->(q)
                SET a.is_correct = $is_correct,
                    a.score = toFloat($score),
                    a.time_seconds = toInteger($time_seconds),
                    a.error_type = $error_type
                """,
                student_id=row["student_id"],
                question_id=row["question_id"],
                is_correct=to_bool(row["is_correct"]),
                score=row["score"],
                time_seconds=row["time_seconds"],
                error_type=row["error_type"],
            )

        for row in video_activity:
            session.run(
                """
                MATCH (s:Student {student_id: $student_id})
                MATCH (c:Concept {concept_id: $concept_id})
                MERGE (s)-[w:WATCHED_CONCEPT_VIDEO]->(c)
                SET w.completion_rate = toFloat($completion_rate)
                """,
                **row,
            )

        counts = session.run(
            """
            MATCH (n)
            RETURN labels(n)[0] AS label, count(n) AS count
            ORDER BY label
            """
        ).data()
        rel_counts = session.run(
            """
            MATCH ()-[r]->()
            RETURN type(r) AS relation, count(r) AS count
            ORDER BY relation
            """
        ).data()

    driver.close()

    print("Import completed.")
    print("Nodes:")
    for row in counts:
        print(f"  {row['label']}: {row['count']}")
    print("Relationships:")
    for row in rel_counts:
        print(f"  {row['relation']}: {row['count']}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--reset", action="store_true", help="Delete all Neo4j data before import")
    args = parser.parse_args()
    import_ai_kg(reset=args.reset)
