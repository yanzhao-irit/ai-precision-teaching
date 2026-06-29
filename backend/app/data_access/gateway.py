"""
引擎数据门面 · EngineDataGateway
================================
引擎只认这一个数据入口。节点身份 = kp_code（题目→知识点在关系库，
知识点→概念→前置在图库）。按课程 course_code 隔离。

暴露给引擎的接口（与旧 repo+kg 同名，便于移植）：
  get_attempts / concept_for_question / get_concept /
  get_prerequisites / misconceptions_for_concept / get_questions
"""
from __future__ import annotations

from app.data_access.sql_repo import SqlRepository
from app.data_access.graph_repo import GraphRepository


class EngineDataGateway:
    def __init__(self, sql: SqlRepository, graph: GraphRepository, course_code: str):
        self.sql = sql
        self.graph = graph
        self.course_code = course_code
        self._q2kp: dict[str, str] | None = None
        self._labels: dict[str, dict] | None = None

    async def _ensure(self):
        if self._q2kp is None:
            self._q2kp = await self.sql.question_kp_map(self.course_code)
        if self._labels is None:
            self._labels = await self.sql.kp_labels(self.course_code)

    # ---------- 关系库 ----------
    async def get_attempts(self, student_no: str) -> list[dict]:
        return await self.sql.get_responses(student_no, self.course_code)

    async def get_questions(self) -> list[dict]:
        return await self.sql.questions(self.course_code)

    async def concept_for_question(self, question_id: str) -> str | None:
        await self._ensure()
        return self._q2kp.get(str(question_id))

    async def get_concept(self, kp_code: str) -> dict | None:
        await self._ensure()
        return self._labels.get(kp_code, {"id": kp_code, "label": kp_code, "label_cn": kp_code})

    async def get_students(self) -> list[dict]:
        return await self.sql.students_of_course(self.course_code)

    async def all_concepts(self) -> list[dict]:
        """引擎的“概念”节点空间 = 知识点(kp)。"""
        await self._ensure()
        return list(self._labels.values())

    async def get_resources(self) -> list[dict]:
        """资源需按知识点打标签后才能用于推荐；当前导出数据无此标签，返回空。"""
        return await self.sql.resources_of_course(self.course_code)

    async def all_relations(self) -> list[dict]:
        """知识点级前置关系对（由图库概念级 REQUIRES 派生）；图库未populate时为空。"""
        return await self.graph.kp_relations(self.course_code)

    # ---------- 图库 ----------
    async def get_prerequisites(self, kp_code: str, max_depth: int = 3) -> list[dict]:
        return await self.graph.prerequisites_of_kp(kp_code, max_depth)

    async def misconceptions_for_concept(self, kp_code: str) -> list[dict]:
        return await self.graph.misconceptions_of_kp(kp_code)
