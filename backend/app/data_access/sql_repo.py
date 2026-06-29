"""
关系库仓储 · SqlRepository (async SQLAlchemy core)
从 PostgreSQL 读引擎所需的业务数据。所有方法按课程(course_code)隔离。
"""
from __future__ import annotations

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


class SqlRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def _rows(self, sql: str, **params) -> list[dict]:
        res = await self.session.execute(text(sql), params)
        return [dict(m) for m in res.mappings().all()]

    # ---------- 逐题作答 · per-question responses ----------
    async def get_responses(self, student_no: str, course_code: str) -> list[dict]:
        """
        返回该生在该课程的逐题作答（已挂主知识点的取权重最高的 kp）。
        每行: question_id, kp_code, is_correct, score, submitted_at, weight
        """
        rows = await self._rows(
            """
            SELECT qr.question_id, kp.kp_code, qr.is_correct, qr.score,
                   s.submitted_at, qkp.weight
            FROM student st
            JOIN enrollment e  ON e.student_id = st.student_id
            JOIN course c      ON c.course_id  = e.course_id AND c.course_code = :course_code
            JOIN submission s  ON s.enrollment_id = e.enrollment_id
            JOIN question_response qr ON qr.submission_id = s.submission_id
            JOIN question q    ON q.question_id = qr.question_id
            LEFT JOIN question_knowledge_point qkp
                   ON qkp.question_id = q.question_id AND qkp.review_status = 'approved'
            LEFT JOIN knowledge_point kp ON kp.kp_id = qkp.kp_id
            WHERE st.student_no = :student_no
            ORDER BY s.submitted_at NULLS LAST, qr.question_id
            """,
            student_no=student_no, course_code=course_code,
        )
        # 一题多知识点时只保留权重最高的，保持作答时间顺序
        primary: dict[str, dict] = {}
        order: list[str] = []
        for r in rows:
            qid = str(r["question_id"])
            if qid not in primary:
                order.append(qid)
            cur = primary.get(qid)
            w = r["weight"] if r["weight"] is not None else 0
            if cur is None or w > cur["_w"]:
                primary[qid] = {
                    "question_id": qid,
                    "kp_code": r["kp_code"],
                    "is_correct": bool(r["is_correct"]) if r["is_correct"] is not None else False,
                    "score": float(r["score"]) if r["score"] is not None else None,
                    "timestamp": r["submitted_at"],
                    "error_type": None,     # 导出数据无错因类型
                    "time_seconds": None,   # 导出数据无作答用时
                    "_w": w,
                }
        return [primary[q] for q in order]

    # ---------- 题目↔知识点 · question -> kp ----------
    async def question_kp_map(self, course_code: str) -> dict[str, str]:
        rows = await self._rows(
            """
            SELECT DISTINCT ON (q.question_id) q.question_id, kp.kp_code
            FROM question q
            JOIN assessment a ON a.assessment_id = q.assessment_id
            JOIN course c     ON c.course_id = a.course_id AND c.course_code = :course_code
            JOIN question_knowledge_point qkp
                 ON qkp.question_id = q.question_id AND qkp.review_status = 'approved'
            JOIN knowledge_point kp ON kp.kp_id = qkp.kp_id
            ORDER BY q.question_id, qkp.weight DESC NULLS LAST
            """,
            course_code=course_code,
        )
        return {str(r["question_id"]): r["kp_code"] for r in rows}

    # ---------- 知识点标签 · kp labels ----------
    async def kp_labels(self, course_code: str) -> dict[str, dict]:
        rows = await self._rows(
            """
            SELECT kp.kp_code, kp.label, kp.difficulty
            FROM knowledge_point kp
            JOIN course c ON c.course_id = kp.course_id AND c.course_code = :course_code
            """,
            course_code=course_code,
        )
        return {r["kp_code"]: {"id": r["kp_code"], "label": r["label"],
                              "label_cn": r["label"], "difficulty": r["difficulty"]}
                for r in rows}

    # ---------- 课程 · courses ----------
    async def create_course(
        self, course_code: str, course_name: str, term_code: str | None = None
    ) -> dict:
        rows = await self._rows(
            """
            INSERT INTO course (course_code, course_name, term_code)
            VALUES (:code, :name, :term)
            ON CONFLICT (course_code) DO UPDATE SET course_name = EXCLUDED.course_name
            RETURNING course_code, course_name, term_code
            """,
            code=course_code, name=course_name, term=term_code,
        )
        return rows[0]

    async def list_courses(self) -> list[dict]:
        rows = await self._rows(
            "SELECT course_code, course_name, term_code FROM course ORDER BY course_code"
        )
        return [{"course_code": r["course_code"], "course_name": r["course_name"],
                 "term_code": r["term_code"]} for r in rows]

    # ---------- 学生 · students ----------
    async def students_of_course(self, course_code: str) -> list[dict]:
        rows = await self._rows(
            """
            SELECT st.student_no, st.full_name
            FROM student st
            JOIN enrollment e ON e.student_id = st.student_id
            JOIN course c     ON c.course_id = e.course_id AND c.course_code = :course_code
            ORDER BY st.student_no
            """,
            course_code=course_code,
        )
        return [{"id": r["student_no"], "name": r["full_name"]} for r in rows]

    # ---------- 资源 · learning resources ----------
    async def resources_of_course(self, course_code: str) -> list[dict]:
        """
        推荐引擎需要资源带 concept_id / type / level；当前导出的 learning_resource
        无这些标签，故返回空（后续给资源打知识点标签后再填充）。
        """
        return []

    # ---------- 题干 · question stems ----------
    async def questions(self, course_code: str) -> list[dict]:
        rows = await self._rows(
            """
            SELECT q.question_id, q.stem
            FROM question q
            JOIN assessment a ON a.assessment_id = q.assessment_id
            JOIN course c     ON c.course_id = a.course_id AND c.course_code = :course_code
            """,
            course_code=course_code,
        )
        return [{"id": str(r["question_id"]), "text": r["stem"]} for r in rows]

    # =====================================================================
    # 教师端看板 · Teacher dashboard aggregates
    # 班级筛选统一用 (CAST(:class_name AS text) IS NULL OR e.class_name = :class_name)
    # =====================================================================

    # ---------- 课程列表（带统计）· course summaries ----------
    async def course_summaries(self) -> list[dict]:
        rows = await self._rows(
            """
            SELECT c.course_code, c.course_name, c.term_code,
                   COUNT(DISTINCT e.student_id) AS student_count,
                   COUNT(DISTINCT e.class_name) AS class_count,
                   COUNT(DISTINCT a.chapter_id) AS chapter_count,
                   (SELECT AVG(CASE WHEN qr.is_correct THEN 1.0 ELSE 0.0 END)
                      FROM submission s
                      JOIN enrollment e2 ON e2.enrollment_id = s.enrollment_id
                                        AND e2.course_id = c.course_id
                      JOIN question_response qr ON qr.submission_id = s.submission_id
                   ) AS accuracy
            FROM course c
            LEFT JOIN enrollment e ON e.course_id = c.course_id
            LEFT JOIN assessment  a ON a.course_id = c.course_id
            GROUP BY c.course_id, c.course_code, c.course_name, c.term_code
            ORDER BY c.course_code
            """
        )
        return [{
            "course_code": r["course_code"],
            "course_name": r["course_name"],
            "term_code": r["term_code"],
            "student_count": int(r["student_count"] or 0),
            "class_count": int(r["class_count"] or 0),
            "chapter_count": int(r["chapter_count"] or 0),
            "accuracy": round(float(r["accuracy"]), 3) if r["accuracy"] is not None else None,
        } for r in rows]

    # ---------- 某课程的班级 · classes of a course ----------
    async def classes_of_course(self, course_code: str) -> list[str]:
        rows = await self._rows(
            """
            SELECT DISTINCT e.class_name
            FROM enrollment e
            JOIN course c ON c.course_id = e.course_id AND c.course_code = :course_code
            WHERE e.class_name IS NOT NULL
            ORDER BY e.class_name
            """,
            course_code=course_code,
        )
        return [r["class_name"] for r in rows]

    # ---------- 看板基础统计 · dashboard base stats ----------
    async def dashboard_stats(self, course_code: str, class_name: str | None) -> dict:
        head = await self._rows(
            """
            SELECT COUNT(DISTINCT e.student_id) AS student_count,
                   COUNT(DISTINCT e.class_name) AS class_count,
                   COUNT(DISTINCT a.chapter_id) AS chapter_count
            FROM course c
            LEFT JOIN enrollment e ON e.course_id = c.course_id
                                  AND (CAST(:class_name AS text) IS NULL OR e.class_name = :class_name)
            LEFT JOIN assessment  a ON a.course_id = c.course_id
            WHERE c.course_code = :course_code
            """,
            course_code=course_code, class_name=class_name,
        )
        acc = await self._rows(
            """
            SELECT COUNT(*) AS response_count,
                   AVG(CASE WHEN qr.is_correct THEN 1.0 ELSE 0.0 END) AS accuracy,
                   COUNT(DISTINCT e.student_id) AS tested_students
            FROM submission s
            JOIN enrollment e ON e.enrollment_id = s.enrollment_id
                             AND (CAST(:class_name AS text) IS NULL OR e.class_name = :class_name)
            JOIN course c ON c.course_id = e.course_id AND c.course_code = :course_code
            JOIN question_response qr ON qr.submission_id = s.submission_id
            """,
            course_code=course_code, class_name=class_name,
        )
        eng = await self._rows(
            """
            SELECT AVG(sp.task_completion_ratio) AS task_ratio,
                   AVG(sp.discussion_count)      AS discussion,
                   AVG(sp.chapter_visit_count)   AS visits
            FROM student_progress sp
            JOIN enrollment e ON e.enrollment_id = sp.enrollment_id
                             AND (CAST(:class_name AS text) IS NULL OR e.class_name = :class_name)
            JOIN course c ON c.course_id = e.course_id AND c.course_code = :course_code
            """,
            course_code=course_code, class_name=class_name,
        )
        grade = await self._rows(
            """
            SELECT AVG(cg.homework_score) AS homework, AVG(cg.final_score) AS final
            FROM composite_grade cg
            JOIN enrollment e ON e.enrollment_id = cg.enrollment_id
                             AND (CAST(:class_name AS text) IS NULL OR e.class_name = :class_name)
            JOIN course c ON c.course_id = e.course_id AND c.course_code = :course_code
            """,
            course_code=course_code, class_name=class_name,
        )
        h, a2, e2, g = head[0], acc[0], eng[0], grade[0]

        def fnum(v, nd=3):
            return round(float(v), nd) if v is not None else None

        return {
            "student_count": int(h["student_count"] or 0),
            "class_count": int(h["class_count"] or 0),
            "chapter_count": int(h["chapter_count"] or 0),
            "response_count": int(a2["response_count"] or 0),
            "tested_students": int(a2["tested_students"] or 0),
            "accuracy": fnum(a2["accuracy"]),
            "engagement": {
                "task_completion_ratio": fnum(e2["task_ratio"]),
                "avg_discussion_count": fnum(e2["discussion"], 1),
                "avg_chapter_visits": fnum(e2["visits"], 1),
            },
            "grade": {
                "avg_homework": fnum(g["homework"], 1),
                "avg_final": fnum(g["final"], 1),
            },
        }

    # ---------- 逐题×知识点作答（供掌握度计算）· kp-level responses ----------
    async def kp_responses(self, course_code: str, class_name: str | None) -> list[dict]:
        return await self._rows(
            """
            SELECT st.student_no, qr.question_id, kp.kp_code, kp.label AS kp_label,
                   qr.is_correct, s.submitted_at
            FROM student st
            JOIN enrollment e ON e.student_id = st.student_id
                             AND (CAST(:class_name AS text) IS NULL OR e.class_name = :class_name)
            JOIN course c ON c.course_id = e.course_id AND c.course_code = :course_code
            JOIN submission s ON s.enrollment_id = e.enrollment_id
            JOIN question_response qr ON qr.submission_id = s.submission_id
            JOIN question_knowledge_point qkp ON qkp.question_id = qr.question_id
                                             AND qkp.review_status = 'approved'
            JOIN knowledge_point kp ON kp.kp_id = qkp.kp_id
            WHERE (CAST(:class_name AS text) IS NULL OR e.class_name = :class_name)
            ORDER BY st.student_no, s.submitted_at NULLS LAST, qr.question_id
            """,
            course_code=course_code, class_name=class_name,
        )

    # ---------- 逐题正确率（高错题）· per-question stats ----------
    async def question_stats(self, course_code: str, class_name: str | None) -> list[dict]:
        rows = await self._rows(
            """
            SELECT q.question_id, q.seq_no, q.stem, q.type::text AS type,
                   COUNT(qr.response_id) AS total,
                   SUM(CASE WHEN qr.is_correct THEN 1 ELSE 0 END) AS correct
            FROM question q
            JOIN assessment a ON a.assessment_id = q.assessment_id
            JOIN course c ON c.course_id = a.course_id AND c.course_code = :course_code
            JOIN question_response qr ON qr.question_id = q.question_id
            JOIN submission s ON s.submission_id = qr.submission_id
            JOIN enrollment e ON e.enrollment_id = s.enrollment_id
                             AND (CAST(:class_name AS text) IS NULL OR e.class_name = :class_name)
            GROUP BY q.question_id, q.seq_no, q.stem, q.type
            HAVING COUNT(qr.response_id) > 0
            """,
            course_code=course_code, class_name=class_name,
        )
        return [{
            "question_id": str(r["question_id"]),
            "seq_no": r["seq_no"],
            "stem": r["stem"],
            "type": r["type"],
            "total": int(r["total"]),
            "correct": int(r["correct"]),
        } for r in rows]

    # ---------- 单题详情 · question detail ----------
    async def question_detail(self, question_id: str) -> dict | None:
        rows = await self._rows(
            """
            SELECT q.question_id, q.seq_no, q.type::text AS type, q.stem,
                   q.correct_answer, q.explanation, q.difficulty
            FROM question q WHERE q.question_id = :qid
            """,
            qid=int(question_id),
        )
        if not rows:
            return None
        r = rows[0]
        opts = await self._rows(
            """
            SELECT option_label, option_text, is_correct
            FROM question_option WHERE question_id = :qid ORDER BY option_label
            """,
            qid=int(question_id),
        )
        return {
            "question_id": str(r["question_id"]),
            "seq_no": r["seq_no"],
            "type": r["type"],
            "stem": r["stem"],
            "correct_answer": r["correct_answer"],
            "explanation": r["explanation"],
            "difficulty": r["difficulty"],
            "options": [{
                "label": o["option_label"],
                "text": o["option_text"],
                "is_correct": bool(o["is_correct"]),
            } for o in opts],
        }

    # ---------- 选项作答分布（干扰项分析）· option distribution ----------
    async def option_distribution(
        self, question_id: str, class_name: str | None
    ) -> list[dict]:
        rows = await self._rows(
            """
            SELECT qr.student_answer AS answer, COUNT(*) AS cnt,
                   SUM(CASE WHEN qr.is_correct THEN 1 ELSE 0 END) AS correct_cnt
            FROM question_response qr
            JOIN submission s ON s.submission_id = qr.submission_id
            JOIN enrollment e ON e.enrollment_id = s.enrollment_id
                             AND (CAST(:class_name AS text) IS NULL OR e.class_name = :class_name)
            WHERE qr.question_id = :qid
            GROUP BY qr.student_answer
            ORDER BY cnt DESC
            """,
            qid=int(question_id), class_name=class_name,
        )
        return [{
            "answer": r["answer"],
            "count": int(r["cnt"]),
            "is_correct": int(r["correct_cnt"] or 0) > 0,
        } for r in rows]

    # ---------- 答错该题的学生 · students who missed a question ----------
    async def students_missed_question(
        self, question_id: str, class_name: str | None
    ) -> list[dict]:
        rows = await self._rows(
            """
            SELECT st.student_no, st.full_name, qr.student_answer AS answer
            FROM question_response qr
            JOIN submission s ON s.submission_id = qr.submission_id
            JOIN enrollment e ON e.enrollment_id = s.enrollment_id
                             AND (CAST(:class_name AS text) IS NULL OR e.class_name = :class_name)
            JOIN student st ON st.student_id = e.student_id
            WHERE qr.question_id = :qid AND qr.is_correct = false
            ORDER BY st.student_no
            """,
            qid=int(question_id), class_name=class_name,
        )
        return [{
            "student_no": r["student_no"],
            "name": r["full_name"],
            "answer": r["answer"],
        } for r in rows]

    # ---------- 某知识点逐生正确率（薄弱学生）· per-student accuracy on a KP ----------
    async def kp_student_accuracy(
        self, course_code: str, kp_code: str, class_name: str | None
    ) -> list[dict]:
        rows = await self._rows(
            """
            SELECT st.student_no, st.full_name,
                   COUNT(qr.response_id) AS total,
                   SUM(CASE WHEN qr.is_correct THEN 1 ELSE 0 END) AS correct
            FROM knowledge_point kp
            JOIN course c ON c.course_id = kp.course_id AND c.course_code = :course_code
            JOIN question_knowledge_point qkp ON qkp.kp_id = kp.kp_id
                                             AND qkp.review_status = 'approved'
            JOIN question_response qr ON qr.question_id = qkp.question_id
            JOIN submission s ON s.submission_id = qr.submission_id
            JOIN enrollment e ON e.enrollment_id = s.enrollment_id
                             AND (CAST(:class_name AS text) IS NULL OR e.class_name = :class_name)
            JOIN student st ON st.student_id = e.student_id
            WHERE kp.kp_code = :kp_code
            GROUP BY st.student_no, st.full_name
            """,
            course_code=course_code, kp_code=kp_code, class_name=class_name,
        )
        return [{
            "student_no": r["student_no"],
            "name": r["full_name"],
            "total": int(r["total"]),
            "correct": int(r["correct"]),
        } for r in rows]

    # ---------- 逐生参与度（测验/任务/作业）· per-student engagement ----------
    async def student_engagement(
        self, course_code: str, class_name: str | None
    ) -> list[dict]:
        rows = await self._rows(
            """
            SELECT st.student_no, st.full_name, e.class_name,
                   COALESCE(r.total, 0)   AS total,
                   COALESCE(r.correct, 0) AS correct,
                   sp.task_completed, sp.task_total,
                   cg.homework_score, cg.final_score
            FROM enrollment e
            JOIN course c ON c.course_id = e.course_id AND c.course_code = :course_code
            JOIN student st ON st.student_id = e.student_id
            LEFT JOIN (
                SELECT sub.enrollment_id,
                       COUNT(qr.response_id) AS total,
                       SUM(CASE WHEN qr.is_correct THEN 1 ELSE 0 END) AS correct
                FROM submission sub
                JOIN question_response qr ON qr.submission_id = sub.submission_id
                GROUP BY sub.enrollment_id
            ) r ON r.enrollment_id = e.enrollment_id
            LEFT JOIN (
                SELECT enrollment_id,
                       MAX(task_completed_count) AS task_completed,
                       MAX(task_total_count)     AS task_total
                FROM student_progress GROUP BY enrollment_id
            ) sp ON sp.enrollment_id = e.enrollment_id
            LEFT JOIN composite_grade cg ON cg.enrollment_id = e.enrollment_id
            WHERE (CAST(:class_name AS text) IS NULL OR e.class_name = :class_name)
            ORDER BY st.student_no
            """,
            course_code=course_code, class_name=class_name,
        )

        def num(v):
            return float(v) if v is not None else None

        out = []
        for r in rows:
            total = int(r["total"] or 0)
            correct = int(r["correct"] or 0)
            tc, tt = r["task_completed"], r["task_total"]
            task_ratio = (float(tc) / float(tt)) if (tc is not None and tt) else None
            out.append({
                "student_no": r["student_no"],
                "name": r["full_name"],
                "class_name": r["class_name"],
                "tested": total > 0,
                "total": total,
                "correct": correct,
                "accuracy": round(correct / total, 3) if total else None,
                "task_completed": int(tc) if tc is not None else None,
                "task_total": int(tt) if tt is not None else None,
                "task_ratio": round(task_ratio, 3) if task_ratio is not None else None,
                "homework_score": num(r["homework_score"]),
                "final_score": num(r["final_score"]),
            })
        return out

    # ---------- 知识点标签（单个）· single kp label ----------
    async def kp_label(self, course_code: str, kp_code: str) -> str | None:
        rows = await self._rows(
            """
            SELECT kp.label FROM knowledge_point kp
            JOIN course c ON c.course_id = kp.course_id AND c.course_code = :course_code
            WHERE kp.kp_code = :kp_code
            """,
            course_code=course_code, kp_code=kp_code,
        )
        return rows[0]["label"] if rows else None
