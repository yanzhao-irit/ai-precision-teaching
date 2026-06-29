"""Early-Warning Engine (M6).

Combines multiple signals to automatically flag students who need attention,
generating a watch-list.

移植说明：数据入口改为 EngineDataGateway；修正原 bug —— diagnose_student() 返回的是
dict，需取其 individual_diagnoses 列表再遍历。"""

from app.data_access import EngineDataGateway
from app.engines.profile import ProfileEngine
from app.engines.diagnosis import DiagnosisEngine


class WarningEngine:
    def __init__(self, gateway: EngineDataGateway):
        self.g = gateway
        self.profile = ProfileEngine(gateway)
        self.diagnosis = DiagnosisEngine(gateway)

    async def get_watch_list(self) -> list[dict]:
        students = await self.g.get_students()
        watch_list = []
        for student in students:
            sid = student["id"]
            profile = await self.profile.build_profile(sid)
            full = await self.diagnosis.diagnose_student(sid)
            diagnoses = full["individual_diagnoses"]

            signals = []
            risk_score = 0.0

            avg_mastery = profile["knowledge"]["avg_mastery"]
            if avg_mastery < 0.4:
                signals.append("平均掌握度过低 · very low average mastery")
                risk_score += 0.35
            elif avg_mastery < 0.5:
                signals.append("平均掌握度偏低 · low average mastery")
                risk_score += 0.2

            accuracy = profile["behavior"]["accuracy"]
            if accuracy < 0.4:
                signals.append("正确率过低 · very low accuracy")
                risk_score += 0.3
            elif accuracy < 0.6:
                signals.append("正确率偏低 · low accuracy")
                risk_score += 0.15

            prereq_gaps = sum(1 for d in diagnoses if d["cause_type"] == "prerequisite_gap")
            if prereq_gaps >= 2:
                signals.append(f"存在 {prereq_gaps} 处前置知识缺口 · {prereq_gaps} prerequisite gaps")
                risk_score += 0.2

            if len(diagnoses) >= 3:
                signals.append(f"错题较多（{len(diagnoses)} 道）· many wrong answers ({len(diagnoses)})")
                risk_score += 0.15

            risk_score = min(round(risk_score, 2), 1.0)

            if signals and profile["tier"] in ("at_risk", "weak"):
                watch_list.append({
                    "student_id": sid,
                    "tier": profile["tier"],
                    "risk_score": risk_score,
                    "signals": signals,
                    "avg_mastery": avg_mastery,
                    "accuracy": accuracy,
                    "wrong_count": len(diagnoses),
                })

        return sorted(watch_list, key=lambda x: x["risk_score"], reverse=True)
