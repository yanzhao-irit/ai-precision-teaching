"""
AI 精准教学系统 · FastAPI 入口（重建版）
数据层：PostgreSQL（业务+作答）+ Neo4j（知识图谱），引擎经 EngineDataGateway 读。
路由按引擎逐步接入：当前已接 diagnosis；profile/recommendation/warning/evaluation 随后。
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from app.core.config import settings
from app.api import (
    diagnosis, profiles, recommendations, warnings, evaluation, students,
    dashboard, upload,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    from app.core.postgres_client import engine, close_postgres
    try:
        async with engine.begin() as conn:
            await conn.execute(text("SELECT 1"))
        print("✅ PostgreSQL connected")
    except Exception as e:
        print(f"⚠️ PostgreSQL not reachable: {e}")

    try:
        from app.core.neo4j_client import get_neo4j_driver
        driver = await get_neo4j_driver()
        await driver.verify_connectivity()
        print(f"✅ Neo4j connected ({settings.NEO4J_URI})")
    except Exception as e:
        print(f"⚠️ Neo4j not reachable — 诊断将降级为无前置回溯: {e}")

    yield

    await close_postgres()
    try:
        from app.core.neo4j_client import close_neo4j_driver
        await close_neo4j_driver()
    except Exception:
        pass


app = FastAPI(title=settings.APP_TITLE, version=settings.APP_VERSION, lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],      # 生产环境请收紧
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(diagnosis.router)
app.include_router(profiles.router)
app.include_router(recommendations.router)
app.include_router(warnings.router)
app.include_router(evaluation.router)
app.include_router(students.router)
app.include_router(dashboard.router)
app.include_router(upload.router)


@app.get("/", tags=["Root"])
def root():
    return {"name": settings.APP_TITLE, "version": settings.APP_VERSION, "docs": "/docs"}


@app.get("/health", tags=["Root"])
def health():
    return {"status": "ok"}
