"""Evaluation & Class Analytics Engine (M8).

Two parts:
  1. Class-level analytics (for dashboard)
  2. Effectiveness evaluation (evidence-based)

移植说明：数据入口改为 EngineDataGateway；修正原 bug —— diagnose_student() 返回 dict，
取其 individual_diagnoses 再遍历。前后测 t 检验需 scipy（未装则优雅报错）。"""

from collections import Counter
from app.data_access import EngineDataGateway
from app.engines.diagnosis import DiagnosisEngine
from app.engines.profile import ProfileEngine


class EvaluationEngine:
    def __init__(self, gateway: EngineDataGateway):
        self.g = gateway
        self.diagnosis = DiagnosisEngine(gateway)
        self.profile = ProfileEngine(gateway)

    # ---------- Class analytics ----------

    async def class_mastery_heatmap(self) -> list[dict]:
        students = await self.g.get_students()
        concepts = await self.g.all_concepts()
        rows = []
        for student in students:
            sid = student["id"]
            mastery = await self.diagnosis.compute_mastery(sid)
            for concept in concepts:
                cid = concept["id"]
                m = mastery.get(cid)
                rows.append({
                    "student_id": sid,
                    "concept_id": cid,
                    "concept_label": concept["label"],
                    "concept_label_cn": concept.get("label_cn", ""),
                    "mastery": m["probability"] if m else None,
                    "state": m["state"] if m else "no_data",
                })
        return rows

    async def tier_distribution(self) -> dict[str, int]:
        counter = Counter()
        profiles = await self.profile.build_all_profiles()
        for profile in profiles:
            counter[profile["tier"]] += 1
        return {
            "at_risk": counter.get("at_risk", 0),
            "weak": counter.get("weak", 0),
            "on_track": counter.get("on_track", 0),
            "advanced": counter.get("advanced", 0),
        }

    async def top_root_causes(self, limit: int = 5) -> list[dict]:
        students = await self.g.get_students()
        causes = Counter()
        for student in students:
            full = await self.diagnosis.diagnose_student(student["id"])
            for diag in full["individual_diagnoses"]:
                causes[diag["root_cause_concept"]] += 1
        return [{"concept": c, "count": n} for c, n in causes.most_common(limit)]

    async def top_error_concepts(self, limit: int = 5) -> list[dict]:
        students = await self.g.get_students()
        concepts = Counter()
        for student in students:
            full = await self.diagnosis.diagnose_student(student["id"])
            for diag in full["individual_diagnoses"]:
                concepts[diag["visible_concept"]] += 1
        return [{"concept": c, "count": n} for c, n in concepts.most_common(limit)]

    async def class_overview(self) -> dict:
        students = await self.g.get_students()
        concepts = await self.g.all_concepts()
        relations = await self.g.all_relations()
        total_mistakes = 0
        for s in students:
            full = await self.diagnosis.diagnose_student(s["id"])
            total_mistakes += len(full["individual_diagnoses"])
        tier_dist = await self.tier_distribution()

        return {
            "total_students": len(students),
            "total_concepts": len(concepts),
            "total_relations": len(relations),
            "total_diagnosed_mistakes": total_mistakes,
            "tier_distribution": tier_dist,
        }

    # ---------- Effectiveness evaluation ----------

    def pre_post_comparison(self, pre_scores: list[float], post_scores: list[float]) -> dict:
        try:
            from scipy import stats
        except ImportError:
            return {"error": "scipy not installed — run: pip install scipy"}

        if len(pre_scores) != len(post_scores) or not pre_scores:
            return {"error": "pre and post score lists must be non-empty and equal length"}

        import statistics
        pre_mean = round(statistics.mean(pre_scores), 2)
        post_mean = round(statistics.mean(post_scores), 2)

        t_stat, p_value = stats.ttest_rel(post_scores, pre_scores)

        diffs = [post - pre for post, pre in zip(post_scores, pre_scores)]
        d = statistics.mean(diffs) / statistics.pstdev(diffs) if statistics.pstdev(diffs) > 0 else 0.0

        return {
            "n": len(pre_scores),
            "pre_mean": pre_mean,
            "post_mean": post_mean,
            "improvement": round(post_mean - pre_mean, 2),
            "t_statistic": round(float(t_stat), 4),
            "p_value": round(float(p_value), 4),
            "cohens_d": round(d, 4),
            "significant": bool(p_value < 0.05),
        }
