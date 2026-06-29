"""
图库仓储 · GraphRepository (async Neo4j)
只做知识图谱查询：概念前置回溯 / 误区。图库未populate时优雅返回空。
约定方向：(A)-[:REQUIRES]->(B) 表示 A 需要 B（B 是 A 的前置）。
节点身份键 kp_code / concept_code 与关系库对齐。
"""
from __future__ import annotations


class GraphRepository:
    def __init__(self, driver):
        self.driver = driver   # 可为 None（图库不可用时降级）

    async def _run(self, query: str, **params) -> list[dict]:
        if self.driver is None:
            return []
        try:
            async with self.driver.session() as session:
                result = await session.run(query, **params)
                return [r.data() async for r in result]
        except Exception:
            return []   # 图库未起/未populate：诊断降级为无前置回溯

    async def prerequisites_of_kp(self, kp_code: str, max_depth: int = 3) -> list[dict]:
        """
        kp -> 所属概念 -> REQUIRES* 前置概念 -> 该前置概念下的知识点。
        返回前置知识点节点 [{id, label, label_cn, distance}]，distance=概念跳数。
        """
        query = (
            "MATCH (kp:KnowledgePoint {kp_code:$kp})<-[:HAS_KNOWLEDGE_POINT]-(c:Concept) "
            f"MATCH p=(c)-[:REQUIRES*1..{int(max_depth)}]->(pre:Concept) "
            "WITH pre, min(length(p)) AS distance "
            "MATCH (pre)-[:HAS_KNOWLEDGE_POINT]->(prekp:KnowledgePoint) "
            "RETURN prekp.kp_code AS id, prekp.label AS label, "
            "prekp.label AS label_cn, distance ORDER BY distance"
        )
        return await self._run(query, kp=kp_code)

    async def kp_relations(self, course_code: str) -> list[dict]:
        """概念级 REQUIRES 派生成知识点级关系对（source 需要 target）。"""
        return await self._run(
            "MATCH (a:Concept {course_code:$course})-[:REQUIRES]->(b:Concept) "
            "MATCH (a)-[:HAS_KNOWLEDGE_POINT]->(akp:KnowledgePoint) "
            "MATCH (b)-[:HAS_KNOWLEDGE_POINT]->(bkp:KnowledgePoint) "
            "RETURN akp.kp_code AS source_id, bkp.kp_code AS target_id, "
            "'REQUIRES' AS relation_type",
            course=course_code,
        )

    async def misconceptions_of_kp(self, kp_code: str) -> list[dict]:
        return await self._run(
            "MATCH (kp:KnowledgePoint {kp_code:$kp})-[:HAS_MISCONCEPTION]->(m:Misconception) "
            "RETURN m.description AS description",
            kp=kp_code,
        )
