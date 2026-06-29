"""Recommendation Engine (M5) - Enhanced.

Three learning paths:
  1. REMEDIAL (mastery < 0.4): Fix foundational gaps
  2. CONSOLIDATION (0.4 ≤ mastery < 0.7): Strengthen current knowledge
  3. EXTENSION (mastery ≥ 0.7): Deep dive, apply, create
"""

from typing import Optional
from enum import Enum
from app.data_access import EngineDataGateway
from app.engines.diagnosis import DiagnosisEngine

class LearningPath(str, Enum):
    REMEDIAL = "remedial"
    CONSOLIDATION = "consolidation"
    EXTENSION = "extension"

class RecommendationEngine:
    def __init__(self, gateway: EngineDataGateway):
        self.g = gateway
        self.diagnosis = DiagnosisEngine(gateway)
        self._resource_cache: dict = {}

    async def recommend_for_student(
        self, 
        student_id: str, 
        max_items: int = 5,
        learning_style: Optional[str] = None,  # "visual", "read", "hands-on", etc.
    ) -> dict:
        """
        Recommande ressources avec 3 chemins pédagogiques.
        Returns: {
            "remedial": [...],
            "consolidation": [...],
            "extension": [...],
            "summary": {...}
        }
        """
        mastery = await self.diagnosis.compute_mastery(student_id)
        resources = await self._get_resources_cached()
        concepts = await self.g.all_concepts()
        
        # Grouper les concepts par niveau de maîtrise
        weak = []        # < 0.4
        learning = []    # 0.4-0.7
        mastered = []    # >= 0.7
        
        for cid, m in mastery.items():
            prob = m["probability"]
            if prob < 0.4:
                weak.append((cid, prob))
            elif prob < 0.7:
                learning.append((cid, prob))
            else:
                mastered.append((cid, prob))
        
        # Générer 3 chemins
        remedial = await self._recommend_remedial(
            weak, resources, concepts, learning_style
        )
        consolidation = await self._recommend_consolidation(
            learning, resources, concepts, learning_style
        )
        extension = await self._recommend_extension(
            mastered, resources, concepts, learning_style
        )
        
        # Sélectionner top-N par chemin (évite déséquilibre)
        items_per_path = max(1, max_items // 3)
        return {
            "student_id": student_id,
            "remedial": remedial[:items_per_path],
            "consolidation": consolidation[:items_per_path],
            "extension": extension[:items_per_path],
            "summary": {
                "total_weak_concepts": len(weak),
                "total_learning_concepts": len(learning),
                "total_mastered_concepts": len(mastered),
                "recommended_count": sum(
                    len(remedial[:items_per_path]) +
                    len(consolidation[:items_per_path]) +
                    len(extension[:items_per_path])
                ),
            },
        }

    # ============== REMEDIAL (Fix gaps) ==============
    
    async def _recommend_remedial(
        self, 
        weak_concepts: list[tuple[str, float]], 
        resources: list[dict],
        concepts: list[dict],
        learning_style: Optional[str],
    ) -> list[dict]:
        """Concepts faibles → ressources explicatives + prérequis."""
        
        recommendations = []
        seen = set()
        
        # Trier par mastery (plus faible en premier)
        weak_concepts.sort(key=lambda x: x[1])
        
        for concept_id, prob in weak_concepts:
            concept = next((c for c in concepts if c["id"] == concept_id), None)
            if not concept:
                continue
            
            # 1️⃣ Ressources DIRECTES pour le concept faible
            for res in resources:
                if (res["concept_id"] == concept_id and 
                    res["id"] not in seen):
                    
                    score = self._score_resource(res, "remedial", learning_style)
                    recommendations.append({
                        **res,
                        "concept": concept,
                        "reason": (
                            f"针对薄弱知识点「{concept.get('label_cn', concept['label'])}」"
                            f"(掌握度 {prob:.1%}) 的基础复习 / "
                            f"Foundational review for weak concept: {concept['label']} ({prob:.1%})"
                        ),
                        "priority": "remedial",
                        "sequence": 1,  # À faire d'abord
                        "score": score,
                    })
                    seen.add(res["id"])
            
            # 2️⃣ Prérequis (si manquants)
            prereqs = await self.g.get_prerequisites(concept_id, max_depth=2)
            for pre in prereqs:
                pre_concept = next((c for c in concepts if c["id"] == pre["id"]), None)
                if not pre_concept:
                    continue
                
                for res in resources:
                    if (res["concept_id"] == pre["id"] and 
                        res["id"] not in seen):
                        
                        score = self._score_resource(res, "remedial", learning_style)
                        recommendations.append({
                            **res,
                            "concept": pre_concept,
                            "reason": (
                                f"前置知识「{pre_concept.get('label_cn', pre_concept['label'])}」"
                                f"缺失，必须补强 / "
                                f"Missing prerequisite: {pre_concept['label']}"
                            ),
                            "priority": "remedial",
                            "sequence": 0,  # À faire EN PREMIER
                            "score": score,
                        })
                        seen.add(res["id"])
        
        # Trier : sequence (0 avant 1), puis score
        return sorted(
            recommendations,
            key=lambda x: (x["sequence"], -x["score"])
        )

    # ============== CONSOLIDATION (Deepen) ==============
    
    async def _recommend_consolidation(
        self,
        learning_concepts: list[tuple[str, float]],
        resources: list[dict],
        concepts: list[dict],
        learning_style: Optional[str],
    ) -> list[dict]:
        """Concepts en apprentissage → exercices progressifs + cas d'usage."""
        
        recommendations = []
        seen = set()
        
        learning_concepts.sort(key=lambda x: x[1], reverse=True)  # Plus maîtrisé en premier
        
        for concept_id, prob in learning_concepts:
            concept = next((c for c in concepts if c["id"] == concept_id), None)
            if not concept:
                continue
            
            # 1️⃣ Exercices pratiques (PRACTICE, PROBLEM_SET)
            for res in resources:
                if (res["concept_id"] == concept_id and 
                    res["id"] not in seen and
                    res.get("type") in ["practice", "problem_set", "exercise"]):
                    
                    score = self._score_resource(res, "consolidation", learning_style)
                    recommendations.append({
                        **res,
                        "concept": concept,
                        "reason": (
                            f"通过练习强化「{concept.get('label_cn', concept['label'])}」"
                            f"(掌握度 {prob:.1%}) / "
                            f"Strengthen {concept['label']} through practice ({prob:.1%})"
                        ),
                        "priority": "consolidation",
                        "sequence": 1,
                        "score": score,
                    })
                    seen.add(res["id"])
            
            # 2️⃣ Cas d'usage réels (APPLICATION, CASE_STUDY)
            for res in resources:
                if (res["concept_id"] == concept_id and 
                    res["id"] not in seen and
                    res.get("type") in ["application", "case_study", "project"]):
                    
                    score = self._score_resource(res, "consolidation", learning_style)
                    recommendations.append({
                        **res,
                        "concept": concept,
                        "reason": (
                            f"通过实战应用「{concept.get('label_cn', concept['label'])}」 / "
                            f"Apply {concept['label']} to real-world scenarios"
                        ),
                        "priority": "consolidation",
                        "sequence": 2,
                        "score": score,
                    })
                    seen.add(res["id"])
        
        return sorted(
            recommendations,
            key=lambda x: (x["sequence"], -x["score"])
        )

    # ============== EXTENSION (Go deeper) ==============
    
    async def _recommend_extension(
        self,
        mastered_concepts: list[tuple[str, float]],
        resources: list[dict],
        concepts: list[dict],
        learning_style: Optional[str],
    ) -> list[dict]:
        """Concepts maîtrisés → concepts avancés, connections, recherche."""
        
        recommendations = []
        seen = set()
        
        # Déjà maîtrisés → recommander ce qui s'en suit
        mastered_ids = {cid for cid, _ in mastered_concepts}
        
        for concept_id, prob in mastered_concepts:
            concept = next((c for c in concepts if c["id"] == concept_id), None)
            if not concept:
                continue
            
            # 1️⃣ Ressources avancées du concept lui-même
            for res in resources:
                if (res["concept_id"] == concept_id and 
                    res["id"] not in seen and
                    res.get("level") in ["advanced", "expert", "research"]):
                    
                    score = self._score_resource(res, "extension", learning_style)
                    recommendations.append({
                        **res,
                        "concept": concept,
                        "reason": (
                            f"深化「{concept.get('label_cn', concept['label'])}」"
                            f"(已掌握 {prob:.1%}) / "
                            f"Advanced topics in {concept['label']}"
                        ),
                        "priority": "extension",
                        "sequence": 1,
                        "score": score,
                    })
                    seen.add(res["id"])
            
            # 2️⃣ Concepts dépendants (forward relations)
            dependent = await self._find_dependents(concept_id, concepts)
            for dep_concept_id in dependent:
                if dep_concept_id not in mastered_ids:  # Pas encore maîtrisé
                    dep_concept = next((c for c in concepts if c["id"] == dep_concept_id), None)
                    if not dep_concept:
                        continue
                    
                    for res in resources:
                        if (res["concept_id"] == dep_concept_id and 
                            res["id"] not in seen):
                            
                            score = self._score_resource(res, "extension", learning_style)
                            recommendations.append({
                                **res,
                                "concept": dep_concept,
                                "reason": (
                                    f"在掌握「{concept.get('label_cn', concept['label'])}」基础上，"
                                    f"学习「{dep_concept.get('label_cn', dep_concept['label'])}」 / "
                                    f"Next logical step: {dep_concept['label']}"
                                ),
                                "priority": "extension",
                                "sequence": 2,
                                "score": score,
                            })
                            seen.add(res["id"])
        
        return sorted(
            recommendations,
            key=lambda x: (x["sequence"], -x["score"])
        )

    # ============== Helper methods ==============
    
    def _score_resource(
        self, 
        resource: dict, 
        path: str,
        learning_style: Optional[str],
    ) -> float:
        """Score une ressource (0-1) selon le chemin pédagogique et style."""
        
        score = 0.5  # Baseline
        
        # Bonus par type de ressource
        type_bonus = {
            "explanation": 0.3,
            "tutorial": 0.25,
            "video": 0.2,
            "practice": 0.25,
            "problem_set": 0.2,
            "exercise": 0.15,
            "application": 0.3,
            "case_study": 0.25,
            "project": 0.2,
        }
        score += type_bonus.get(resource.get("type", ""), 0.0)
        
        # Bonus par style d'apprentissage
        if learning_style:
            if learning_style == "visual" and resource.get("type") in ["video", "diagram", "infographic"]:
                score += 0.15
            elif learning_style == "read" and resource.get("type") in ["article", "documentation", "book"]:
                score += 0.15
            elif learning_style == "hands-on" and resource.get("type") in ["practice", "project", "exercise"]:
                score += 0.15
            elif learning_style == "interactive" and resource.get("type") in ["simulation", "interactive", "game"]:
                score += 0.15
        
        # Bonus par niveau de difficulté
        if resource.get("level") == "beginner":
            score += 0.1 if path == "remedial" else 0.0
        elif resource.get("level") == "intermediate":
            score += 0.1 if path == "consolidation" else 0.05
        elif resource.get("level") in ["advanced", "expert"]:
            score += 0.1 if path == "extension" else 0.0
        
        return min(1.0, score)  # Cap à 1.0

    async def _find_dependents(self, concept_id: str, concepts: list[dict]) -> list[str]:
        """Trouve les concepts qui DÉPENDENT du concept donné (forward relation)."""
        
        relations = await self.g.all_relations()
        dependents = []
        
        for rel in relations:
            if rel["target_id"] == concept_id:  # concept_id est un prérequis
                # Donc source dépend de concept_id
                dependents.append(rel["source_id"])
        
        return dependents

    async def _get_resources_cached(self) -> list[dict]:
        """Cache les ressources pour éviter requêtes répétées."""
        
        if not self._resource_cache:
            self._resource_cache = await self.g.get_resources()
        
        return self._resource_cache
