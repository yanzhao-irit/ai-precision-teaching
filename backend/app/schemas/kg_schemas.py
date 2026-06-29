"""
Schémas pour Knowledge Graph · KG Schemas
"""
from pydantic import BaseModel, Field
from typing import Optional

class ConceptSchema(BaseModel):
    """Un concept/nœud du graphe."""
    id: str = Field(..., description="Identifiant unique")
    label: str = Field(..., description="Étiquette anglaise")
    label_cn: str = Field(..., description="Étiquette chinoise")
    chapter: Optional[str] = Field(None, description="Chapitre")
    difficulty: Optional[int] = Field(None, description="Difficulté (1-5)")  # ← CHANGÉ
    description: Optional[str] = Field(None, description="Description")

    class Config:
        json_schema_extra = {
            "example": {
                "id": "concept_001",
                "label": "Variables",
                "label_cn": "变量",
                "chapter": "Chapter 1",
                "difficulty": 2,  # ← INT au lieu de string
                "description": "Basic concept of variables"
            }
        }

class RelationSchema(BaseModel):
    """Une relation REQUIRES entre concepts."""
    source_id: str = Field(..., description="ID du concept source")
    target_id: str = Field(..., description="ID du concept cible")
    relation_type: str = Field(..., description="Type de relation (REQUIRES)")
    explanation: Optional[str] = Field(None, description="Explication du lien")

    class Config:
        json_schema_extra = {
            "example": {
                "source_id": "concept_002",
                "target_id": "concept_001",
                "relation_type": "REQUIRES",
                "explanation": "You need to understand variables first"
            }
        }

class PrerequisiteSchema(BaseModel):
    """Un prérequis avec sa distance."""
    id: str
    label: str
    label_cn: str
    distance: int = Field(..., description="Profondeur du prérequis (1, 2, 3...)")

    class Config:
        json_schema_extra = {
            "example": {
                "id": "concept_001",
                "label": "Variables",
                "label_cn": "变量",
                "distance": 1
            }
        }

class KnowledgeGraphSchema(BaseModel):
    """Graphe complet : nœuds + arêtes."""
    nodes: list[ConceptSchema]
    edges: list[RelationSchema]

    class Config:
        json_schema_extra = {
            "example": {
                "nodes": [
                    {"id": "c1", "label": "Variables", "label_cn": "变量"}
                ],
                "edges": [
                    {"source_id": "c2", "target_id": "c1", "relation_type": "REQUIRES"}
                ]
            }
        }

class MisconceptionSchema(BaseModel):
    """Une fausse conception."""
    id: str
    concept_id: str
    description: str = Field(..., description="Description de la fausse conception")

    class Config:
        json_schema_extra = {
            "example": {
                "id": "misc_001",
                "concept_id": "concept_001",
                "description": "Variables always start with 0"
            }
        }
