"""
Schémas pour Profile Engine · Profile Schemas (M4)
"""
from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum

class TierEnum(str, Enum):
    """Niveaux d'apprentissage."""
    ADVANCED = "advanced"
    ON_TRACK = "on_track"
    WEAK = "weak"
    AT_RISK = "at_risk"


class MasteryDetailSchema(BaseModel):
    """Détail de maîtrise par concept."""
    probability: float = Field(..., ge=0.0, le=1.0, description="P(mastered) selon BKT")
    state: str = Field(..., description="mastered | learning | not_learned")
    attempts: int = Field(..., description="Nombre de tentatives")
    recent_trend: str = Field(..., description="improving | stable | regressing")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confiance du diagnostic")
    last_attempt_correct: Optional[bool] = Field(None, description="Dernière tentative correcte?")


class WeakConceptSchema(BaseModel):
    """Un concept faible (mastery < 0.5)."""
    concept_id: str
    probability: float = Field(..., ge=0.0, le=1.0)
    state: str
    attempts: int
    recent_trend: str
    confidence: float
    last_attempt_correct: Optional[bool] = None


class KnowledgeDimensionSchema(BaseModel):
    """Dimension connaissance du profil."""
    avg_mastery: float = Field(..., ge=0.0, le=1.0, description="Maîtrise moyenne")
    weak_concept_count: int = Field(..., description="Nombre de concepts faibles")
    weak_concepts: list[WeakConceptSchema] = Field(..., description="Détail des concepts faibles")
    mastery_detail: dict[str, MasteryDetailSchema] = Field(..., description="Maîtrise par concept")


class BehaviorDimensionSchema(BaseModel):
    """Dimension comportement du profil."""
    total_attempts: int = Field(..., description="Nombre total de tentatives")
    accuracy: float = Field(..., ge=0.0, le=1.0, description="Taux de réussite")
    avg_time_seconds: float = Field(..., description="Temps moyen par tentative")


class CognitionDimensionSchema(BaseModel):
    """Dimension cognition du profil."""
    dominant_error_types: list[str] = Field(..., description="Top 3 types d'erreurs")


class StudentProfileSchema(BaseModel):
    """Profil complet d'un étudiant (3D)."""
    student_id: str = Field(..., description="ID de l'étudiant")
    tier: TierEnum = Field(..., description="Niveau d'apprentissage")
    knowledge: KnowledgeDimensionSchema
    behavior: BehaviorDimensionSchema
    cognition: CognitionDimensionSchema

    class Config:
        json_schema_extra = {
            "example": {
                "student_id": "student_001",
                "tier": "on_track",
                "knowledge": {
                    "avg_mastery": 0.65,
                    "weak_concept_count": 2,
                    "weak_concepts": [
                        {
                            "concept_id": "concept_005",
                            "probability": 0.42,
                            "state": "learning",
                            "attempts": 5,
                            "recent_trend": "improving",
                            "confidence": 0.5
                        }
                    ],
                    "mastery_detail": {}
                },
                "behavior": {
                    "total_attempts": 42,
                    "accuracy": 0.76,
                    "avg_time_seconds": 120.5
                },
                "cognition": {
                    "dominant_error_types": ["careless_mistake", "conceptual_error"]
                }
            }
        }
