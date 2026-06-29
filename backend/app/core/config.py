from dataclasses import dataclass, field
import os
from pathlib import Path
from dotenv import load_dotenv
from urllib.parse import quote_plus

env_path = Path(__file__).resolve().parents[2] / ".env"
load_dotenv(dotenv_path=env_path, override=True)

@dataclass
class Settings:
    # ── Neo4j ─────────────────────────────────────────
    NEO4J_URI: str = field(default_factory=lambda: os.getenv(
        "NEO4J_URI", "bolt://localhost:7687"
    ))
    NEO4J_USER: str = field(default_factory=lambda: os.getenv(
        "NEO4J_USER", "neo4j"
    ))
    NEO4J_PASSWORD: str = field(default_factory=lambda: os.getenv(
        "NEO4J_PASSWORD", "password"
    ))

    # ── PostgreSQL ────────────────────────────────────
    POSTGRES_HOST: str = field(default_factory=lambda: os.getenv(
        "POSTGRES_HOST", "localhost"
    ))
    POSTGRES_PORT: int = field(default_factory=lambda: int(os.getenv(
        "POSTGRES_PORT", "5432"
    )))
    POSTGRES_DB: str = field(default_factory=lambda: os.getenv(
        "POSTGRES_DB", "ai_precision_teaching"
    ))
    POSTGRES_USER: str = field(default_factory=lambda: os.getenv(
        "POSTGRES_USER", "postgres"
    ))
    POSTGRES_PASSWORD: str = field(default_factory=lambda: os.getenv(
        "POSTGRES_PASSWORD", "password"
    ))

    # ── Data Source ───────────────────────────────────
    # Valeurs possibles : "in_memory" | "neo4j" | "postgres" | "both"
    DATA_SOURCE: str = field(default_factory=lambda: os.getenv(
        "DATA_SOURCE", "in_memory"
    ))

    # ── App Metadata ──────────────────────────────────
    APP_TITLE: str = "AI-Empowered Precision Teaching"
    APP_VERSION: str = "0.1.0"

    @property
    def POSTGRES_URL(self) -> str:
        password = quote_plus(self.POSTGRES_PASSWORD)
        return (
            f"postgresql+asyncpg://{self.POSTGRES_USER}:"
            f"{password}@{self.POSTGRES_HOST}:"
            f"{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    @property
    def use_postgres(self) -> bool:
        return self.DATA_SOURCE.lower() in ("postgres", "both")

    @property
    def use_neo4j(self) -> bool:
        return self.DATA_SOURCE.lower() in ("neo4j", "both")

settings = Settings()
