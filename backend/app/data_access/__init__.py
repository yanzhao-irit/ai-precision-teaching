"""
数据访问层 · Data Access Layer
==============================
引擎只依赖 EngineDataGateway 这一个门面：
  - 关系库 (SqlRepository)  : 学生 / 逐题作答 / 题目↔知识点
  - 图库   (GraphRepository): 概念前置回溯 / 误区
跨库桥 = 共享的 kp_code。
"""
from app.data_access.gateway import EngineDataGateway
from app.data_access.sql_repo import SqlRepository
from app.data_access.graph_repo import GraphRepository

__all__ = ["EngineDataGateway", "SqlRepository", "GraphRepository"]
