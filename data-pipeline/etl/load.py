"""
ETL 入库 · Loaders
把 parsers.py 解析出的结构写进 PostgreSQL（幂等 upsert）。
顺序：先题库(load_question_bank) → 再学生答题(load_student_submission)。
"""
from __future__ import annotations

from . import db
from .parsers import ParsedAssessment, ParsedSubmission, ParsedClassExport


def load_question_bank(cur, a: ParsedAssessment) -> dict:
    course_id = db.upsert_course(cur, a.course_code, a.course_name)
    chapter_id = db.upsert_chapter(cur, course_id, a.chapter_no,
                                   f"第{a.chapter_no}章" if a.chapter_no else None)
    assessment_id = db.get_or_create_assessment(
        cur, course_id, chapter_id, a.assessment_type, a.title, a.source_file)

    n_q = n_opt = n_kp = n_pending = 0
    for q in a.questions:
        qid = db.get_or_create_question(cur, assessment_id, q)
        n_q += 1
        for opt in q.options:
            db.upsert_option(cur, qid, opt)
            n_opt += 1
        if q.knowledge_point:
            kp_id = db.upsert_knowledge_point(cur, course_id, a.course_code, q.knowledge_point)
            db.link_question_kp(cur, qid, kp_id)
            n_kp += 1
        else:
            n_pending += 1   # 待 LLM 生成知识点
    return {"assessment_id": assessment_id, "questions": n_q, "options": n_opt,
            "kp_linked": n_kp, "kp_pending": n_pending}


def load_student_submission(cur, s: ParsedSubmission, course_code: str,
                            course_name: str | None = None,
                            assessment_type: str = "unit_test") -> dict:
    if not s.student_no:
        return {"skipped": "no student_no", "file": s.source_file}
    course_id = db.upsert_course(cur, course_code, course_name)
    assessment_id = db.find_assessment(cur, course_id, s.chapter_no, assessment_type)
    if assessment_id is None:
        return {"skipped": "assessment not found — load question bank first",
                "chapter": s.chapter_no, "file": s.source_file}

    student_id = db.upsert_student(cur, s.student_no, s.student_name)
    enrollment_id = db.upsert_enrollment(cur, student_id, course_id, class_name=s.class_name)
    submission_id = db.upsert_submission(
        cur, enrollment_id, assessment_id, s.total_score, "completed",
        s.submitted_at, s.source_file)

    n_resp = n_missing = 0
    for r in s.responses:
        cur.execute(
            "SELECT question_id FROM question WHERE assessment_id=%s AND seq_no=%s",
            (assessment_id, r.seq_no))
        row = cur.fetchone()
        if not row:
            n_missing += 1
            continue
        db.upsert_response(cur, submission_id, row[0], r)
        n_resp += 1
    return {"submission_id": submission_id, "student_no": s.student_no,
            "responses": n_resp, "missing_questions": n_missing}


def load_class_export(cur, c: ParsedClassExport) -> dict:
    course_id = db.upsert_course(cur, c.course_code, c.course_name)
    n_stu = 0
    enr = {}
    for st in c.students:
        sid = db.upsert_student(cur, st.student_no, st.full_name)
        eid = db.upsert_enrollment(
            cur, sid, course_id, school=st.school, department=st.department,
            major=st.major, class_name=st.class_name, admission_year=st.admission_year)
        # external_uid 单独补
        cur.execute("UPDATE student SET external_uid=%s WHERE student_id=%s AND external_uid IS NULL",
                    (st.external_uid, sid))
        enr[st.student_no] = eid
        n_stu += 1

    n_prog = 0
    for p in c.progress:
        eid = enr.get(p["student_no"])
        if not eid:
            continue
        cur.execute(
            """INSERT INTO student_progress
                 (enrollment_id, task_completed_count, task_total_count,
                  discussion_count, chapter_visit_count, learning_status)
               VALUES (%s,%s,%s,%s,%s,%s)""",
            (eid, p.get("task_completed_count"), p.get("task_total_count"),
             p.get("discussion_count"), p.get("chapter_visit_count"), p.get("learning_status")))
        n_prog += 1

    n_comp = 0
    for cgrade in c.composite:
        eid = enr.get(cgrade["student_no"])
        if not eid:
            continue
        cur.execute(
            """INSERT INTO composite_grade (enrollment_id, homework_score, final_score)
               VALUES (%s,%s,%s)
               ON CONFLICT (enrollment_id)
               DO UPDATE SET homework_score=EXCLUDED.homework_score,
                             final_score=EXCLUDED.final_score""",
            (eid, cgrade.get("homework_score"), cgrade.get("final_score")))
        n_comp += 1

    return {"students": n_stu, "progress": n_prog, "composite": n_comp}
