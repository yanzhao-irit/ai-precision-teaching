"""
课程看板分析 · Course-level analytics
=====================================
把全班逐题×知识点作答(SqlRepository.kp_responses)聚合成：
  - 学生分层分布（已掌握/部分掌握/未掌握，按 BKT 平均掌握度）
  - 知识点掌握度 & 正确率排行（薄弱知识点）

掌握度沿用诊断引擎的 BKT 与阈值，保证看板与个体诊断口径一致。
三档阈值：已掌握 ≥0.7 / 部分掌握 ≥0.4 / 未掌握 <0.4
"""
from __future__ import annotations

from collections import defaultdict

from app.engines.diagnosis.bkt import BKT

TIER_KEYS = ("mastered", "partial", "unlearned")


def tier_of(prob: float) -> str:
    if prob >= 0.7:
        return "mastered"
    if prob >= 0.4:
        return "partial"
    return "unlearned"


class CourseAnalytics:
    """输入 SqlRepository.kp_responses 的行（已按学生、时间排序）。"""

    def __init__(self, rows: list[dict]):
        self.bkt = BKT()
        # 学生 -> 知识点 -> [对错序列]（行已排序，保持作答顺序）
        by_student_kp: dict[str, dict[str, list[bool]]] = defaultdict(lambda: defaultdict(list))
        kp_label: dict[str, str] = {}
        kp_total: dict[str, int] = defaultdict(int)
        kp_correct: dict[str, int] = defaultdict(int)
        for r in rows:
            sno, kp = r["student_no"], r["kp_code"]
            correct = bool(r["is_correct"])
            by_student_kp[sno][kp].append(correct)
            kp_label[kp] = r["kp_label"]
            kp_total[kp] += 1
            kp_correct[kp] += 1 if correct else 0

        # 每生每知识点掌握度 + 每生平均掌握度
        kp_masteries: dict[str, list[float]] = defaultdict(list)
        self.student_avg: dict[str, float] = {}
        for sno, kps in by_student_kp.items():
            probs = []
            for kp, seq in kps.items():
                p = self.bkt.estimate(seq)
                kp_masteries[kp].append(p)
                probs.append(p)
            self.student_avg[sno] = sum(probs) / len(probs) if probs else 0.0

        self._kp_label = kp_label
        self._kp_total = kp_total
        self._kp_correct = kp_correct
        self._kp_masteries = kp_masteries

    # ---------- 学生分层分布 ----------
    def tier_distribution(self) -> dict:
        dist = {k: 0 for k in TIER_KEYS}
        for p in self.student_avg.values():
            dist[tier_of(p)] += 1
        avg = (sum(self.student_avg.values()) / len(self.student_avg)
               if self.student_avg else 0.0)
        return {
            "avg_mastery": round(avg, 3),
            "tested_students": len(self.student_avg),
            "distribution": dist,
        }

    # ---------- 知识点掌握度排行 ----------
    def knowledge_points(self) -> list[dict]:
        out = []
        for kp, probs in self._kp_masteries.items():
            avg = sum(probs) / len(probs) if probs else 0.0
            total = self._kp_total.get(kp, 0)
            correct = self._kp_correct.get(kp, 0)
            out.append({
                "kp_code": kp,
                "label": self._kp_label.get(kp, kp),
                "avg_mastery": round(avg, 3),
                "tier": tier_of(avg),
                "accuracy": round(correct / total, 3) if total else None,
                "student_count": len(probs),
            })
        out.sort(key=lambda x: x["avg_mastery"])  # 最弱在前
        return out

    def weak_knowledge_points(self, limit: int = 10) -> list[dict]:
        return self.knowledge_points()[:limit]
