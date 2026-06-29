"""
Schémas pour Diagnosis Engine · Diagnosis Schemas (M3)
"""
from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum


class ErrorPatternEnum(str, Enum):
    """Patterns d'erreur détectés."""
    SYSTEMATIC = "systematic"
    INTERMITTENT = "intermittent"
    IMPROVING = "improving"
    REGRESSING = "regressing"
    CORRECT_BUT_SLOW = "correct_but_slow"


class PriorityEnum(str, Enum):
    """Niveaux de priorité."""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class PrerequisiteGapSchema(BaseModel):
    """Écart de prérequis détecté."""
    id: str = Field(..., description="ID du concept prérequis")
    label: str
    label_cn: str
    distance: int = Field(..., description="Profondeur du prérequis")
    mastery: dict = Field(..., description="Détails de maîtrise")
    has_evidence: int = Field(..., description="1 si données disponibles, 0 sinon")


class SingleDiagnosisSchema(BaseModel):
    """Diagnostic pour une erreur spécifique (3 étapes)."""
    
    # Étape 1: Surface (visible)
    student_id: str
    question_id: str
    question_text: str
    visible_concept_id: str
    visible_concept: str = Field(..., description="Concept visible (anglais)")
    visible_concept_cn: str = Field(..., description="Concept visible (chinois)")
    visible_concept_mastery: float = Field(..., ge=0.0, le=1.0)
    
    # Étape 2: Deep (prérequis)
    root_cause_concept: str = Field(..., description="Concept racine (anglais)")
    root_cause_concept_cn: str = Field(..., description="Concept racine (chinois)")
    cause_type: str = Field(..., description="current_concept_difficulty | prerequisite_gap")
    prerequisite_gap_depth: Optional[int] = Field(None, description="Profondeur si gap")
    
    # Étape 3: Root (cause racine)
    suspicion_score: float = Field(..., ge=0.0, le=1.0, description="Score de suspicion")
    error_type: str = Field(..., description="Type d'erreur rapporté")
    error_pattern: str = Field(..., description=ErrorPatternEnum.__doc__)
    time_seconds: Optional[float] = Field(None, description="Temps de résolution")
    
    # Contexte
    misconceptions: list[str] = Field(..., description="Fausses conceptions possibles")
    
    # Explication & recommandation
    explanation: str = Field(..., description="Narrative du diagnostic (bilingue)")
    recommendation: str = Field(..., description="Recommandation actionable")
    priority: PriorityEnum

    class Config:
        json_schema_extra = {
            "example": {
                "student_id": "student_001",
                "question_id": "q_042",
                "question_text": "What is the derivative of x²?",
                "visible_concept_id": "concept_derivatives",
                "visible_concept": "Derivatives",
                "visible_concept_cn": "导数",
                "visible_concept_mastery": 0.45,
                "root_cause_concept": "Limits",
                "root_cause_concept_cn": "极限",
                "cause_type": "prerequisite_gap",
                "prerequisite_gap_depth": 1,
                "suspicion_score": 0.75,
                "error_type": "conceptual_error",
                "error_pattern": "systematic",
                "time_seconds": 180.5,
                "misconceptions": [
                    "Derivative is just the coefficient",
                    "Power rule doesn't apply here"
                ],
                "explanation": "Student failed...",
                "recommendation": "Strengthen prerequisites...",
                "priority": "high"
            }
        }


class MasteryStateSummarySchema(BaseModel):
    """Résumé de maîtrise par état."""
    mastered: int = Field(..., description="Concepts maîtrisés")
    learning: int = Field(..., description="Concepts en apprentissage")
    not_learned: int = Field(..., description="Concepts non appris")


class MasterySummarySchema(BaseModel):
    """Résumé de maîtrise globale."""
    avg_mastery: float = Field(..., ge=0.0, le=1.0)
    by_state: MasteryStateSummarySchema


class ErrorPatternSummarySchema(BaseModel):
    """Résumé des patterns d'erreur."""
    total_errors: int
    by_type: dict[str, int] = Field(..., description="Nombre d'erreurs par type")
    most_common: Optional[str] = Field(None, description="Type d'erreur le plus courant")
    systematic_errors: int = Field(..., description="Nombre d'erreurs systématiques")


class PriorityInterventionSchema(BaseModel):
    """Intervention prioritaire recommandée."""
    concept: str = Field(..., description="Concept à traiter (anglais)")
    concept_cn: str = Field(..., description="Concept à traiter (chinois)")
    cause_type: str = Field(..., description="Type de cause")
    suspicion: float = Field(..., ge=0.0, le=1.0, description="Score de suspicion")
    example_question: str = Field(..., description="Question exemple")
    recommendation: str = Field(..., description="Recommandation actionable")
    priority: PriorityEnum


class FullDiagnosisSchema(BaseModel):
    """Diagnostic complet d'un étudiant."""
    student_id: str
    total_attempts: int = Field(..., description="Nombre total de tentatives")
    total_errors: int = Field(..., description="Nombre total d'erreurs")
    mastery_summary: MasterySummarySchema
    individual_diagnoses: list[SingleDiagnosisSchema] = Field(..., description="Top N diagnostics d'erreurs")
    error_patterns: ErrorPatternSummarySchema
    priority_interventions: list[PriorityInterventionSchema] = Field(..., description="Top 5 interventions")

    class Config:
        json_schema_extra = {
            "example": {
                "student_id": "student_001",
                "total_attempts": 50,
                "total_errors": 12,
                "mastery_summary": {
                    "avg_mastery": 0.62,
                    "by_state": {
                        "mastered": 3,
                        "learning": 5,
                        "not_learned": 2
                    }
                },
                "individual_diagnoses": [],
                "error_patterns": {
                    "total_errors": 12,
                    "by_type": {
                        "conceptual_error": 7,
                        "careless_mistake": 5
                    },
                    "most_common": "conceptual_error",
                    "systematic_errors": 7
                },
                "priority_interventions": []
            }
        }
