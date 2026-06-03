from pathlib import Path
import csv
from collections import defaultdict, Counter
from neo4j import GraphDatabase

ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT / "outputs"
REPORT_DIR = OUTPUT_DIR / "reports"

OUTPUT_DIR.mkdir(exist_ok=True)
REPORT_DIR.mkdir(parents=True, exist_ok=True)

NEO4J_URI = "bolt://localhost:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "devpassword"
NEO4J_DATABASE = "neo4j"


def run_query():
    driver = GraphDatabase.driver(
        NEO4J_URI,
        auth=(NEO4J_USER, NEO4J_PASSWORD)
    )

    query = """
    MATCH (s:Student)-[a:ANSWERED]->(q:Question)-[:EVALUATES]->(visible:Concept)
    WHERE a.is_correct = false

    OPTIONAL MATCH path = (visible)-[:REQUIRES*1..3]->(pre:Concept)

    WITH s, a, q, visible, pre, path

    OPTIONAL MATCH (s)-[old:ANSWERED]->(oldQ:Question)-[:EVALUATES]->(pre)

    WITH
        s, a, q, visible, pre, path,
        sum(CASE WHEN old.is_correct = false THEN 1 ELSE 0 END) AS previous_failures,
        count(old) AS previous_attempts

    RETURN
        s.student_id AS student_id,
        q.question_id AS question_id,
        q.question_text AS question_text,
        visible.label AS visible_concept,
        a.error_type AS error_type,
        a.time_seconds AS time_seconds,
        coalesce(pre.label, visible.label) AS possible_root_cause,
        CASE WHEN path IS NULL THEN 0 ELSE length(path) END AS distance,
        previous_failures AS previous_failures,
        previous_attempts AS previous_attempts

    ORDER BY
        student_id,
        question_id,
        previous_failures DESC,
        distance ASC
    """

    with driver.session(database=NEO4J_DATABASE) as session:
        rows = [dict(record) for record in session.run(query)]

    driver.close()
    return rows


def choose_best_diagnosis(rows):
    grouped = defaultdict(list)

    for row in rows:
        key = (row["student_id"], row["question_id"])
        grouped[key].append(row)

    final_rows = []

    for _, candidates in grouped.items():
        best = candidates[0]

        visible = best["visible_concept"]
        root = best["possible_root_cause"]
        distance = int(best["distance"])
        previous_failures = int(best["previous_failures"])

        if root == visible:
            cause_type = "current concept difficulty"
            suspicion_score = 0.50
        else:
            cause_type = "possible prerequisite gap"
            suspicion_score = 0.60

            if distance == 1:
                suspicion_score += 0.20
            elif distance == 2:
                suspicion_score += 0.10

            if previous_failures > 0:
                suspicion_score += 0.15

            suspicion_score = min(suspicion_score, 0.95)

        if root == visible:
            explanation = (
                f"The student failed a question about {visible}. "
                f"No stronger prerequisite gap was detected, so the difficulty may be directly related to {visible}."
            )
            recommendation = (
                f"Review the concept {visible} and retry similar questions."
            )
        else:
            explanation = (
                f"The student failed a question about {visible}. "
                f"The knowledge graph shows that {root} is a prerequisite of {visible}. "
                f"The mistake may therefore come from a previous gap in {root}."
            )
            recommendation = (
                f"Review {root} first, then retry exercises about {visible}."
            )

        final_rows.append({
            "student_id": best["student_id"],
            "question_id": best["question_id"],
            "question_text": best["question_text"],
            "visible_concept": visible,
            "possible_root_cause": root,
            "cause_type": cause_type,
            "suspicion_score": round(suspicion_score, 2),
            "error_type": best["error_type"],
            "time_seconds": best["time_seconds"],
            "teacher_explanation": explanation,
            "recommendation": recommendation,
        })

    return final_rows


def save_csv(rows):
    output_file = OUTPUT_DIR / "ai_diagnosis_results.csv"

    fieldnames = [
        "student_id",
        "question_id",
        "question_text",
        "visible_concept",
        "possible_root_cause",
        "cause_type",
        "suspicion_score",
        "error_type",
        "time_seconds",
        "teacher_explanation",
        "recommendation",
    ]

    with output_file.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Created {output_file}")


def generate_student_reports(rows):
    by_student = defaultdict(list)

    for row in rows:
        by_student[row["student_id"]].append(row)

    for student_id, student_rows in by_student.items():
        report_file = REPORT_DIR / f"student_{student_id}.md"

        with report_file.open("w", encoding="utf-8") as file:
            file.write(f"# Student Report - {student_id}\n\n")

            file.write("## Summary\n\n")
            file.write(
                "This report lists the student's failed questions and gives a possible explanation "
                "based on the AI course knowledge graph.\n\n"
            )

            for row in student_rows:
                file.write(f"## Failed question: {row['question_id']}\n\n")
                file.write(f"**Question:** {row['question_text']}\n\n")
                file.write(f"- Visible concept: **{row['visible_concept']}**\n")
                file.write(f"- Possible root cause: **{row['possible_root_cause']}**\n")
                file.write(f"- Cause type: **{row['cause_type']}**\n")
                file.write(f"- Suspicion score: **{row['suspicion_score']}**\n")
                file.write(f"- Error type: **{row['error_type']}**\n")
                file.write(f"- Time spent: **{row['time_seconds']} seconds**\n\n")

                file.write("### Explanation\n\n")
                file.write(row["teacher_explanation"] + "\n\n")

                file.write("### Recommendation\n\n")
                file.write(row["recommendation"] + "\n\n")

                file.write("---\n\n")

        print(f"Created {report_file}")


def generate_class_summary(rows):
    summary_file = REPORT_DIR / "class_summary.md"

    visible_counter = Counter(row["visible_concept"] for row in rows)
    root_counter = Counter(row["possible_root_cause"] for row in rows)
    cause_counter = Counter(row["cause_type"] for row in rows)

    with summary_file.open("w", encoding="utf-8") as file:
        file.write("# Class Summary\n\n")

        file.write("This summary gives a simple overview of the main difficulties detected in the demo dataset.\n\n")

        file.write("## Most frequent visible error concepts\n\n")
        for concept, count in visible_counter.most_common():
            file.write(f"- **{concept}**: {count} failed question(s)\n")

        file.write("\n## Most frequent possible root causes\n\n")
        for concept, count in root_counter.most_common():
            file.write(f"- **{concept}**: {count} occurrence(s)\n")

        file.write("\n## Cause types\n\n")
        for cause, count in cause_counter.most_common():
            file.write(f"- **{cause}**: {count} case(s)\n")

        file.write("\n## Interpretation\n\n")
        file.write(
            "If the same prerequisite appears several times as a possible root cause, "
            "the teacher may decide to review this concept with the class.\n"
        )

    print(f"Created {summary_file}")


def main():
    raw_rows = run_query()
    diagnosis_rows = choose_best_diagnosis(raw_rows)

    save_csv(diagnosis_rows)
    generate_student_reports(diagnosis_rows)
    generate_class_summary(diagnosis_rows)

    print("\nDiagnosis completed.")
    print(f"Open this folder: {REPORT_DIR}")


if __name__ == "__main__":
    main()