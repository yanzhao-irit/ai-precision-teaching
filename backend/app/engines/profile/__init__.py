"""Learner Profile Engine (M4).

Builds a three-dimensional profile (knowledge/behavior/cognition) for each
student and assigns a tier.

移植说明：数据入口改为 EngineDataGateway；导出数据无 time_seconds/error_type，
相应特性做了空值保护（不再崩溃，只是该维度为空）。"""

from collections import Counter
from app.data_access import EngineDataGateway
from app.engines.diagnosis import DiagnosisEngine


class ProfileEngine:
    def __init__(self, gateway: EngineDataGateway):
        self.g = gateway
        self.diagnosis = DiagnosisEngine(gateway)

    async def build_profile(self, student_id: str) -> dict:
        attempts = await self.g.get_attempts(student_id)
        mastery = await self.diagnosis.compute_mastery(student_id)

        if mastery:
            avg_mastery = round(sum(m["probability"] for m in mastery.values()) / len(mastery), 3)
        else:
            avg_mastery = 0.0
        weak_concepts = [
            {"concept_id": cid, **m}
            for cid, m in mastery.items() if m["probability"] < 0.5
        ]

        total = len(attempts)
        correct = sum(1 for a in attempts if a["is_correct"])
        accuracy = round(correct / total, 3) if total else 0.0
        # 导出数据无作答用时 → None 视为 0
        avg_time = round(sum((a.get("time_seconds") or 0) for a in attempts) / total, 1) if total else 0.0

        # 导出数据无错因类型 → 跳过 None
        error_types = [a["error_type"] for a in attempts
                       if not a["is_correct"] and a.get("error_type") and a["error_type"] != "no_error"]
        dominant_errors = [e for e, _ in Counter(error_types).most_common(3)]

        tier = self._assign_tier(avg_mastery, accuracy, len(weak_concepts))

        return {
            "student_id": student_id,
            "tier": tier,
            "knowledge": {
                "avg_mastery": avg_mastery,
                "weak_concept_count": len(weak_concepts),
                "weak_concepts": weak_concepts,
                "mastery_detail": mastery,
            },
            "behavior": {
                "total_attempts": total,
                "accuracy": accuracy,
                "avg_time_seconds": avg_time,
            },
            "cognition": {
                "dominant_error_types": dominant_errors,
            },
        }

    def _assign_tier(self, avg_mastery, accuracy, weak_count) -> str:
        if avg_mastery >= 0.7 and accuracy >= 0.8:
            return "advanced"
        elif avg_mastery >= 0.5 and accuracy >= 0.6:
            return "on_track"
        elif avg_mastery >= 0.35:
            return "weak"
        else:
            return "at_risk"

    async def build_all_profiles(self) -> list[dict]:
        students = await self.g.get_students()
        profiles = []
        for s in students:
            profiles.append(await self.build_profile(s["id"]))
        return profiles
