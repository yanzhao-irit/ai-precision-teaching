"""Tous les schémas."""
from .kg_schemas import (
    ConceptSchema,
    RelationSchema,
    PrerequisiteSchema,
    KnowledgeGraphSchema,
    MisconceptionSchema,
)
from .profile_schemas import (
    StudentProfileSchema,
    TierEnum,
    KnowledgeDimensionSchema,
    BehaviorDimensionSchema,
    CognitionDimensionSchema,
)
from .diagnosis_schemas import (
    FullDiagnosisSchema,
    SingleDiagnosisSchema,
    PriorityInterventionSchema,
    ErrorPatternEnum,
)
from .recommendation_schemas import (
    ThreePathRecommendationSchema,
    RecommendedResourceSchema,
    LearningPathEnum,
)

__all__ = [
    # KG
    "ConceptSchema",
    "RelationSchema",
    "PrerequisiteSchema",
    "KnowledgeGraphSchema",
    "MisconceptionSchema",
    # Profile
    "StudentProfileSchema",
    "TierEnum",
    "KnowledgeDimensionSchema",
    "BehaviorDimensionSchema",
    "CognitionDimensionSchema",
    # Diagnosis
    "FullDiagnosisSchema",
    "SingleDiagnosisSchema",
    "PriorityInterventionSchema",
    "ErrorPatternEnum",
    # Recommendation
    "ThreePathRecommendationSchema",
    "RecommendedResourceSchema",
    "LearningPathEnum",
]
