"""
Schémas pour Recommendation Engine · Recommendation Schemas (M5)
"""
from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum


class LearningPathEnum(str, Enum):
    """Chemins pédagogiques."""
    REMEDIAL = "remedial"
    CONSOLIDATION = "consolidation"
    EXTENSION = "extension"


class RecommendedResourceSchema(BaseModel):
    """Une ressource recommandée."""
    id: str = Field(..., description="ID unique de la ressource")
    concept_id: str = Field(..., description="Concept associé")
    concept: dict = Field(..., description="Détails du concept")
    type: str = Field(..., description="video | article | practice | project | etc.")
    title: str = Field(..., description="Titre de la ressource")
    url: Optional[str] = Field(None, description="Lien vers la ressource")
    level: Optional[str] = Field(None, description="beginner | intermediate | advanced")
    duration_minutes: Optional[int] = Field(None, description="Durée estimée")
    
    # Recommandation spécifique
    reason: str = Field(..., description="Pourquoi cette ressource est recommandée (bilingue)")
    priority: str = Field(..., description="remedial | consolidation | extension")
    sequence: int = Field(..., description="Ordre de progression (0 = en premier)")
    score: float = Field(..., ge=0.0, le=1.0, description="Score de pertinence")

    class Config:
        json_schema_extra = {
            "example": {
                "id": "res_001",
                "concept_id": "concept_001",
                "concept": {
                    "id": "concept_001",
                    "label": "Variables",
                    "label_cn": "变量"
                },
                "type": "video",
                "title": "Introduction to Variables",
                "url": "https://example.com/video",
                "level": "beginner",
                "duration_minutes": 15,
                "reason": "针对薄弱知识点「变量」(掌握度 42%) 的基础复习 / Foundational review for weak concept",
                "priority": "remedial",
                "sequence": 1,
                "score": 0.85
            }
        }


class RecommendationSummarySchema(BaseModel):
    """Résumé des recommandations."""
    total_weak_concepts: int = Field(..., description="Nombre de concepts faibles")
    total_learning_concepts: int = Field(..., description="Nombre de concepts en apprentissage")
    total_mastered_concepts: int = Field(..., description="Nombre de concepts maîtrisés")
    recommended_count: int = Field(..., description="Nombre total de ressources recommandées")


class ThreePathRecommendationSchema(BaseModel):
    """Recommandations avec 3 chemins pédagogiques."""
    student_id: str = Field(..., description="ID de l'étudiant")
    
    remedial: list[RecommendedResourceSchema] = Field(
        ..., 
        description="Chemin de remédiation (mastery < 0.4)"
    )
    consolidation: list[RecommendedResourceSchema] = Field(
        ..., 
        description="Chemin de consolidation (0.4 ≤ mastery < 0.7)"
    )
    extension: list[RecommendedResourceSchema] = Field(
        ..., 
        description="Chemin d'extension (mastery ≥ 0.7)"
    )
    
    summary: RecommendationSummarySchema

    class Config:
        json_schema_extra = {
            "example": {
                "student_id": "student_001",
                "remedial": [
                    {
                        "id": "res_001",
                        "concept_id": "concept_001",
                        "concept": {
                            "id": "concept_001",
                            "label": "Variables",
                            "label_cn": "变量"
                        },
                        "type": "video",
                        "title": "Introduction to Variables",
                        "url": "https://example.com/video",
                        "level": "beginner",
                        "duration_minutes": 15,
                        "reason": "Foundational review...",
                        "priority": "remedial",
                        "sequence": 0,
                        "score": 0.85
                    }
                ],
                "consolidation": [],
                "extension": [],
                "summary": {
                    "total_weak_concepts": 2,
                    "total_learning_concepts": 3,
                    "total_mastered_concepts": 5,
                    "recommended_count": 8
                }
            }
        }
