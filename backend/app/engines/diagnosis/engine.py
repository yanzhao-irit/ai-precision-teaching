"""
诊断引擎 · Diagnosis Engine (M3) - Enhanced
================================================
Integrates:
  - Prerequisite-traceback diagnosis (three stages)
  - Lightweight BKT mastery model with caching
  - Temporal sequence analysis (order of attempts matters)
  - Error pattern detection (systematic mistakes)
  - Misconception targeting
  - Actionable, prioritized recommendations
"""

from collections import defaultdict
from datetime import datetime
from enum import Enum
from typing import Optional
from app.data_access import EngineDataGateway
from app.engines.diagnosis.bkt import BKT

class ErrorPattern(str, Enum):
    """Erreurs détectées par analyse de séquence."""
    SYSTEMATIC = "systematic"          # Toujours la même erreur
    INTERMITTENT = "intermittent"      # Parfois correct, parfois non
    IMPROVING = "improving"            # Tend vers le succès
    REGRESSING = "regressing"          # Tend vers l'échec
    CORRECT_BUT_SLOW = "correct_but_slow"  # Juste mais très lent

class DiagnosisEngine:
    def __init__(self, gateway: EngineDataGateway):
        self.g = gateway
        self.bkt = BKT()

        # Caches pour éviter recalculs
        self._mastery_cache: dict = {}
        self._prerequisite_cache: dict = {}

    # ========== MASTERY (avec cache) ==========

    async def compute_mastery(
        self, 
        student_id: str,
        use_cache: bool = True,
    ) -> dict[str, dict]:
        """
        Calcule la maîtrise par concept avec caching optionnel.
        
        Returns: {
            "concept_id": {
                "probability": float,      # P(mastered) selon BKT
                "state": str,              # "mastered" | "learning" | "not_learned"
                "attempts": int,
                "recent_trend": str,       # "improving" | "stable" | "regressing"
                "confidence": float,       # Basé sur nombre d'essais
            },
            ...
        }
        """
        
        cache_key = f"mastery:{student_id}"
        if use_cache and cache_key in self._mastery_cache:
            return self._mastery_cache[cache_key]
        
        attempts = await self.g.get_attempts(student_id)
        
        # Grouper par concept
        by_concept = defaultdict(list)
        for a in attempts:
            concept_id = await self.g.concept_for_question(a["question_id"])
            if concept_id:
                by_concept[concept_id].append({
                    "correct": bool(a["is_correct"]),
                    "timestamp": a.get("timestamp", datetime.now()),
                    "time_seconds": a.get("time_seconds", 0),
                })
        
        mastery = {}
        for concept_id, sequence in by_concept.items():
            # Extraire juste correct/incorrect pour BKT
            correctness = [s["correct"] for s in sequence]
            
            # Maîtrise globale
            prob = self.bkt.estimate(correctness)
            
            # Tendance récente (derniers 3-5 essais)
            recent = correctness[-5:]
            recent_trend = self._compute_trend(recent)
            
            # Confiance basée sur nombre d'essais
            confidence = min(1.0, len(sequence) / 10.0)  # Max confiance à 10 essais
            
            mastery[concept_id] = {
                "probability": round(prob, 3),
                "state": self.bkt.mastery_state(prob),
                "attempts": len(sequence),
                "recent_trend": recent_trend,
                "confidence": round(confidence, 2),
                "last_attempt_correct": correctness[-1] if correctness else None,
            }
        
        if use_cache:
            self._mastery_cache[cache_key] = mastery
        
        return mastery

    # ========== STUDENT DIAGNOSIS (global) ==========

    async def diagnose_student(
        self, 
        student_id: str,
        max_diagnoses: Optional[int] = None,
    ) -> dict:
        """
        Diagnostic complet d'un étudiant (tous les erreurs).
        
        Returns: {
            "student_id": str,
            "total_attempts": int,
            "total_errors": int,
            "mastery_summary": {...},
            "individual_diagnoses": [...],
            "error_patterns": {...},
            "priority_interventions": [...],
        }
        """
        
        attempts = await self.g.get_attempts(student_id)
        mastery = await self.compute_mastery(student_id)
        wrong = [a for a in attempts if not a["is_correct"]]
        
        # Diagnostics individuels
        individual_diagnoses = []
        for attempt in wrong:
            diag = await self._diagnose_one(student_id, attempt, mastery)
            if diag:
                individual_diagnoses.append(diag)
        
        # Limiter si demandé
        if max_diagnoses:
            individual_diagnoses = individual_diagnoses[-max_diagnoses:]
        
        # Patterns d'erreur globaux
        error_patterns = self._analyze_error_patterns(wrong)
        
        # Interventions prioritaires
        priority_interventions = self._prioritize_interventions(
            individual_diagnoses, 
            mastery, 
            error_patterns
        )
        
        return {
            "student_id": student_id,
            "total_attempts": len(attempts),
            "total_errors": len(wrong),
            "mastery_summary": {
                "avg_mastery": round(
                    sum(m["probability"] for m in mastery.values()) / len(mastery), 
                    3
                ) if mastery else 0.0,
                "by_state": {
                    "mastered": len([m for m in mastery.values() if m["state"] == "mastered"]),
                    "learning": len([m for m in mastery.values() if m["state"] == "learning"]),
                    "not_learned": len([m for m in mastery.values() if m["state"] == "not_learned"]),
                },
            },
            "individual_diagnoses": individual_diagnoses,
            "error_patterns": error_patterns,
            "priority_interventions": priority_interventions,
        }

    # ========== ONE-ERROR DIAGNOSIS ==========

    async def _diagnose_one(
        self, 
        student_id: str,
        attempt: dict,
        mastery: dict,
    ) -> dict | None:
        """
        Diagnostic en 3 étapes pour une erreur spécifique.
        
        1️⃣ Surface: Quel concept, quelle question ?
        2️⃣ Deep: Quels prérequis manquent ?
        3️⃣ Root: Suspicion score & recommandation
        """
        
        question_id = attempt["question_id"]
        
        # ===== STAGE 1: Surface =====
        visible_concept_id = await self.g.concept_for_question(question_id)
        if not visible_concept_id:
            return None
        
        visible_concept = await self.g.get_concept(visible_concept_id)
        visible_mastery = mastery.get(visible_concept_id)
        
        questions = await self.g.get_questions()
        question = next((q for q in questions if q["id"] == question_id), {})
        
        # ===== STAGE 2: Deep =====
        prerequisites = await self._get_prerequisites_cached(
            visible_concept_id, 
            max_depth=3
        )
        
        # Filter: retenir seulement les prérequis "suspects"
        # (ceux avec faible mastery ou pas de données)
        suspect_prerequisites = [
            pre for pre in prerequisites
            if mastery.get(pre["id"], {}).get("probability", 0.0) < 0.6
        ]
        
        # ===== STAGE 3: Root cause =====
        root_cause = None
        best_rank = None
        
        for pre in suspect_prerequisites:
            pre_mastery = mastery.get(pre["id"])
            
            if pre_mastery is not None:
                has_evidence = 1
                prob = pre_mastery["probability"]
            else:
                has_evidence = 0
                prob = 0.5
                pre_mastery = {
                    "probability": prob,
                    "state": "no_data",
                    "attempts": 0,
                    "recent_trend": "unknown",
                    "confidence": 0.0,
                }
            
            # Ranking: evidence > proximité > mastery
            rank = (has_evidence, -pre["distance"], prob)
            
            if best_rank is None or rank > best_rank:
                best_rank = rank
                root_cause = {
                    **pre,
                    "mastery": pre_mastery,
                    "has_evidence": has_evidence,
                }
        
        # Déterminer le type de cause
        if root_cause is None:
            cause_type = "current_concept_difficulty"
            suspicion = 0.50
            root_label = visible_concept["label"]
            root_label_cn = visible_concept.get("label_cn", "")
        else:
            cause_type = "prerequisite_gap"
            suspicion = 0.60
            
            # Boost par distance
            if root_cause["distance"] == 1:
                suspicion += 0.20
            elif root_cause["distance"] == 2:
                suspicion += 0.10
            
            # Boost par faible mastery
            suspicion += (0.6 - root_cause["mastery"]["probability"]) * 0.3
            
            # Boost par confidence du diagnostic
            suspicion += root_cause["mastery"]["confidence"] * 0.1
            
            suspicion = min(round(suspicion, 2), 0.95)
            root_label = root_cause["label"]
            root_label_cn = root_cause.get("label_cn", "")
        
        # Misconceptions
        misconceptions = await self.g.misconceptions_for_concept(visible_concept_id)
        misconception_descs = [m["description"] for m in misconceptions]
        
        # Détection de pattern d'erreur
        error_pattern = self._detect_error_pattern(
            question_id,
            attempt.get("error_type", ""),
        )
        
        # Narratif & recommandation
        narrative = self._generate_narrative(
            visible_concept,
            root_cause,
            cause_type,
            error_pattern,
        )
        recommendation = self._generate_recommendation(
            visible_concept,
            root_cause,
            cause_type,
            error_pattern,
        )
        
        return {
            # Surface level
            "student_id": student_id,
            "question_id": question_id,
            "question_text": question.get("text", ""),
            "visible_concept_id": visible_concept_id,
            "visible_concept": visible_concept["label"],
            "visible_concept_cn": visible_concept.get("label_cn", ""),
            "visible_concept_mastery": visible_mastery["probability"] if visible_mastery else 0.0,
            
            # Deep level
            "root_cause_concept": root_label,
            "root_cause_concept_cn": root_label_cn,
            "cause_type": cause_type,
            "prerequisite_gap_depth": root_cause["distance"] if root_cause else None,
            
            # Root level
            "suspicion_score": suspicion,
            "error_type": attempt.get("error_type", ""),
            "error_pattern": error_pattern,
            "time_seconds": attempt.get("time_seconds"),
            
            # Context
            "misconceptions": misconception_descs,
            
            # Explanation
            "explanation": narrative,
            "recommendation": recommendation,
            "priority": "high" if suspicion >= 0.7 else "medium" if suspicion >= 0.5 else "low",
        }

    # ========== HELPER METHODS ==========

    async def _get_prerequisites_cached(
        self, 
        concept_id: str, 
        max_depth: int = 3,
    ) -> list[dict]:
        """Cache des prérequis pour éviter requêtes répétées."""
        
        cache_key = f"prereq:{concept_id}:{max_depth}"
        if cache_key not in self._prerequisite_cache:
            self._prerequisite_cache[cache_key] = await self.g.get_prerequisites(
                concept_id, 
                max_depth
            )
        return self._prerequisite_cache[cache_key]

    def _compute_trend(self, recent_sequence: list[bool]) -> str:
        """Analyse la tendance récente (derniers essais)."""
        
        if not recent_sequence:
            return "no_data"
        
        if len(recent_sequence) < 2:
            return "improving" if recent_sequence[0] else "regressing"
        
        # Comparer première moitié vs seconde moitié
        mid = len(recent_sequence) // 2
        first_half = sum(recent_sequence[:mid]) / len(recent_sequence[:mid])
        second_half = sum(recent_sequence[mid:]) / len(recent_sequence[mid:])
        
        if second_half > first_half + 0.2:
            return "improving"
        elif second_half < first_half - 0.2:
            return "regressing"
        else:
            return "stable"

    def _detect_error_pattern(self, question_id: str, error_type: str) -> str:
        """
        Détecte des patterns d'erreur.
        TODO: Implémenter une vraie détection par historique.
        """
        
        if error_type in ["conceptual_error", "misconception"]:
            return ErrorPattern.SYSTEMATIC
        elif error_type in ["careless_mistake", "transcription_error"]:
            return ErrorPattern.INTERMITTENT
        else:
            return ErrorPattern.INTERMITTENT

    def _analyze_error_patterns(self, wrong_attempts: list[dict]) -> dict:
        """Analyse globale des patterns d'erreur."""
        
        error_types = defaultdict(int)
        for a in wrong_attempts:
            error_types[a.get("error_type", "unknown")] += 1
        
        return {
            "total_errors": len(wrong_attempts),
            "by_type": dict(error_types),
            "most_common": max(error_types, key=error_types.get) if error_types else None,
            "systematic_errors": len([a for a in wrong_attempts 
                                     if a.get("error_type") in ["conceptual_error", "misconception"]]),
        }

    def _prioritize_interventions(
        self,
        diagnoses: list[dict],
        mastery: dict,
        error_patterns: dict,
    ) -> list[dict]:
        """
        Priorise les interventions pour le teacher/student.
        
        Critères:
          - Suspicion score élevé
          - Concepts faibles affectant beaucoup d'autres
          - Erreurs systématiques
        """
        
        # Trier par suspicion
        sorted_diagnoses = sorted(
            diagnoses,
            key=lambda d: (
                -d.get("suspicion_score", 0),
                d.get("priority") != "high"
            )
        )
        
        # Top 5 + grouper par concept
        prioritized = []
        seen_concepts = set()
        
        for diag in sorted_diagnoses:
            root_concept = diag["root_cause_concept"]
            if root_concept not in seen_concepts:
                prioritized.append({
                    "concept": root_concept,
                    "concept_cn": diag["root_cause_concept_cn"],
                    "cause_type": diag["cause_type"],
                    "suspicion": diag["suspicion_score"],
                    "example_question": diag["question_id"],
                    "recommendation": diag["recommendation"],
                    "priority": diag["priority"],
                })
                seen_concepts.add(root_concept)
            
            if len(prioritized) >= 5:
                break
        
        return prioritized

    # ========== TEXT GENERATION ==========

    def _generate_narrative(
        self,
        visible: dict,
        root_cause: dict | None,
        cause_type: str,
        error_pattern: str,
    ) -> str:
        """
        Génère une explication structurée + lisible.
        """
        
        if cause_type == "current_concept_difficulty":
            return (
                f"学生在「{visible.get('label_cn') or visible['label']}」相关题目上出错。"
                f"未发现明显的前置知识缺口，困难可能直接来自该知识点本身的理解或应用。 / "
                f"The student failed a question about **{visible['label']}**. "
                f"No clear prerequisite gap detected — the difficulty may relate directly to understanding or applying {visible['label']}."
            )
        else:
            return (
                f"学生在「{visible.get('label_cn') or visible['label']}」相关题目上出错。"
                f"根据知识图谱，「{root_cause.get('label_cn') or root_cause['label']}」"
                f"是其前置知识，学生在该前置上的掌握度仅为 {root_cause['mastery']['probability']:.1%}。"
                f"错误根源很可能在于此前置知识缺口。 / "
                f"The student failed a question about **{visible['label']}**. "
                f"The knowledge graph shows **{root_cause['label']}** is a prerequisite, "
                f"and the student's mastery of it is only {root_cause['mastery']['probability']:.1%}. "
                f"The root cause likely stems from this prerequisite gap."
            )

    def _generate_recommendation(
        self,
        visible: dict,
        root_cause: dict | None,
        cause_type: str,
        error_pattern: str,
    ) -> str:
        """Générer une recommandation actionable."""
        
        if cause_type == "current_concept_difficulty":
            return (
                f"📌 **立即行动** / **Immediate Action**:\n"
                f"  1. 重温「{visible.get('label_cn') or visible['label']}」的核心定义与案例\n"
                f"  1. Review core definitions and examples of {visible['label']}\n"
                f"  2. 再做 3-5 道同类练习，关注解题步骤\n"
                f"  2. Redo 3–5 similar practice problems, paying attention to steps\n"
            )
        else:
            return (
                f"📌 **分阶段学习路径** / **Phased Learning Path**:\n"
                f"  **第一步 / Step 1**: 补强前置「{root_cause.get('label_cn') or root_cause['label']}」"
                f"（目标掌握度：≥ 70%）\n"
                f"  **First**: Strengthen prerequisite {root_cause['label']} (target: ≥70% mastery)\n"
                f"  **第二步 / Step 2**: 再返回「{visible.get('label_cn') or visible['label']}」的练习\n"
                f"  **Then**: Return to {visible['label']} practice\n"
            )

    def generate_narrative_with_llm(self, diagnosis: dict) -> str:
        """
        TODO: LLM 润色诊断文字（离线功能）.
        TODO: Use LLM to generate richer narrative (optional enhancement).
        
        Hook for future integration with DeepSeek/GPT.
        """
        raise NotImplementedError("LLM narrative enhancement not yet enabled.")
