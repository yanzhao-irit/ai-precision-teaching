# 数据管道 · Data Pipeline (连数据库后用 · for use after DB connection)

当前初版用内存模拟数据，不需要数据管道。
The current version uses in-memory mock data and needs no pipeline.

将来连接数据库时，这里放：
When connecting a database later, put here:
- `anonymize.py` — 学号脱敏 · anonymize student IDs
- `import_to_neo4j.py` — 知识图谱入 Neo4j · load KG into Neo4j
- `import_to_postgres.py` — 行为数据入库 · load behavior data
- `extract_kp.py` — LLM 抽取知识点 · LLM knowledge-point extraction

可从 prototype 分支移植这些脚本。
These scripts can be ported from the prototype branch.
