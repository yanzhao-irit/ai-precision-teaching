"""
Root-cause diagnosis demo using the Artificial Intelligence KG in Neo4j.

Question:
When a student fails a question, is the real gap the visible concept
or an older prerequisite?
"""

from pathlib import Path
import csv
from neo4j import GraphDatabase

from src.utils.config import PROJECT_ROOT, NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD, NEO4J_DATABASE


OUTPUT_DIR = PROJECT_ROOT / "outputs"
OUTPUT_DIR.mkdir(exist_ok=True)


DIAGNOSIS_QUERY = """
MATCH (s:Student)-[a:ANSWERED]->(q:Question)-[:EVALUATES]->(visible:Concept)
WHERE a.is_correct = false

// candidate root causes are prerequisites reachable in the graph
OPTIONAL MATCH path = (visible)-[:REQUIRES*1..4]->(candidate:Concept)

// previous performance of the same student on questions evaluating the candidate concept
OPTIONAL MATCH (s)-[old:ANSWERED]->(oldq:Question)-[:EVALUATES]->(candidate)
WITH s, a, q, visible, candidate, path,
     avg(old.score) AS candidate_accuracy,
     count(old) AS previous_attempts
OPTIONAL MATCH (s)-[watch:WATCHED_CONCEPT_VIDEO]->(candidate)
WITH s, a, q, visible, candidate, path, candidate_accuracy, previous_attempts,
     avg(watch.completion_rate) AS video_completion

WITH s, q, visible, candidate, path,
     coalesce(candidate_accuracy, 0.50) AS accuracy,
     coalesce(video_completion, 0.50) AS completion,
     previous_attempts,
     CASE WHEN path IS NULL THEN 5 ELSE length(path) END AS distance

WITH s, q, visible, candidate, distance, accuracy, completion, previous_attempts,
     round(
       0.55 * (1.0 - accuracy)
       + 0.25 * (1.0 - completion)
       + 0.20 * (1.0 / distance), 3
     ) AS suspicion_score

RETURN
  s.student_id AS student_id,
  q.question_id AS question_id,
  q.question_text AS question_text,
  visible.concept_id AS visible_concept_id,
  visible.label AS visible_concept,
  candidate.concept_id AS diagnosed_root_concept_id,
  candidate.label AS diagnosed_root_concept,
  distance AS graph_distance,
  accuracy AS previous_accuracy_on_root,
  completion AS video_completion_on_root,
  previous_attempts AS previous_attempts_on_root,
  suspicion_score AS suspicion_score,
  CASE
    WHEN candidate.concept_id IS NULL THEN "Current concept gap"
    WHEN candidate.concept_id = visible.concept_id THEN "Current concept gap"
    ELSE "Prerequisite gap"
  END AS cause_type
ORDER BY student_id, question_id, suspicion_score DESC
"""


def run_diagnosis() -> list[dict]:
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

    with driver.session(database=NEO4J_DATABASE) as session:
        rows = session.run(DIAGNOSIS_QUERY).data()

    driver.close()

    # Keep only the top candidate root cause per failed attempt.
    best_by_attempt = {}
    for row in rows:
        key = (row["student_id"], row["question_id"])
        if key not in best_by_attempt:
            best_by_attempt[key] = row

    final_rows = []
    for row in best_by_attempt.values():
        root = row.get("diagnosed_root_concept") or row["visible_concept"]
        if row["cause_type"] == "Prerequisite gap":
            explanation = (
                f"The student failed a question about {row['visible_concept']}. "
                f"The knowledge graph suggests a possible earlier gap on {root}. "
                f"Evidence: graph distance={row['graph_distance']}, "
                f"previous accuracy={row['previous_accuracy_on_root']:.2f}, "
                f"video completion={row['video_completion_on_root']:.2f}."
            )
            recommendation = (
                f"Review {root} first, then retry the question about {row['visible_concept']}."
            )
        else:
            explanation = (
                f"The student failed a question about {row['visible_concept']}. "
                "No stronger prerequisite root cause was found, so the visible concept is currently the main target."
            )
            recommendation = f"Review {row['visible_concept']} and retry similar questions."

        row["teacher_explanation"] = explanation
        row["recommendation"] = recommendation
        final_rows.append(row)

    return final_rows


def save_csv(rows: list[dict], path: Path) -> None:
    if not rows:
        print("No rows to save.")
        return
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


if __name__ == "__main__":
    rows = run_diagnosis()
    out_path = OUTPUT_DIR / "ai_root_cause_diagnosis_demo.csv"
    save_csv(rows, out_path)

    print(f"Saved diagnosis to: {out_path}")
    print("\nSample results:")
    for row in rows[:8]:
        print(
            f"- {row['student_id']} / {row['question_id']}: "
            f"{row['visible_concept']} -> {row.get('diagnosed_root_concept')}, "
            f"score={row['suspicion_score']}, type={row['cause_type']}"
        )
