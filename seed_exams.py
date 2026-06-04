import random
from neo4j import GraphDatabase

URI = "bolt://localhost:7687"
AUTH = ("neo4j", "Bpa25072020!")

# === Paramètres ===
EXAMS_PER_SUBCHAPTER_PER_STUDENT = (1, 3)   # min, max
SCORE_RANGE = (4.0, 19.5)                   # bornes des notes /20
RESET_BEFORE_SEED = False                   # ⚠️ True = supprime tous les Exam existants

driver = GraphDatabase.driver(URI, auth=AUTH)


def fetch_students_and_subchapters(tx):
    students = [r["name"] for r in tx.run("MATCH (e:Student) RETURN e.name AS name")]
    subs = [r["name"] for r in tx.run("MATCH (sc:SubChapter) RETURN sc.name AS name")]
    return students, subs


def reset_exams(tx):
    tx.run("MATCH (ex:Exam) DETACH DELETE ex")


def create_exam(tx, exam_id, student_name, sub_name, score):
    tx.run(
        """
        MATCH (e:Student {name:$student})
        MATCH (sc:SubChapter {name:$sub})
        MERGE (ex:Exam {id:$exam_id})
        MERGE (e)-[r:TOOK]->(ex)
          SET r.score = $score
        MERGE (ex)-[:COVERS]->(sc)
        """,
        student=student_name,
        sub=sub_name,
        exam_id=exam_id,
        score=score,
    )


def main():
    with driver.session() as session:
        students, subs = session.execute_read(fetch_students_and_subchapters)

        print(f"👤 Students  : {len(students)}")
        print(f"📖 SubChapters: {len(subs)}")

        if not students or not subs:
            print("❌ Pas assez de données de base (Students / SubChapters).")
            return

        if RESET_BEFORE_SEED:
            print("🧹 Suppression des Exam existants...")
            session.execute_write(reset_exams)

        # Point de départ pour les IDs (évite les collisions si on rejoue)
        start_id = session.run(
            "MATCH (ex:Exam) RETURN coalesce(max(toInteger(ex.id)), 0) AS m"
        ).single()["m"]

        exam_counter = start_id + 1
        total_created = 0

        for student in students:
            for sub in subs:
                n_exams = random.randint(*EXAMS_PER_SUBCHAPTER_PER_STUDENT)
                # Biais "par étudiant" pour un peu de cohérence
                student_bias = random.uniform(-2.5, 2.5)

                for _ in range(n_exams):
                    raw_score = random.uniform(*SCORE_RANGE) + student_bias
                    score = round(max(0.0, min(20.0, raw_score)), 2)
                    exam_id = str(exam_counter)
                    exam_counter += 1

                    session.execute_write(
                        create_exam, exam_id, student, sub, score
                    )
                    total_created += 1

            print(f"  ✅ {student} : examens générés sur {len(subs)} sous-chapitres")

        print(f"\n🎉 Terminé : {total_created} examens créés.")

    driver.close()


if __name__ == "__main__":
    main()
