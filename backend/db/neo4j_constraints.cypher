// =====================================================================
// AI 精准教学系统 · 图库约束 (Neo4j)
// 节点身份键与关系库对齐：Course.course_code / Concept.concept_code / KnowledgePoint.kp_code
// 运行：docker compose 的 neo4j-init 服务会自动加载；或手动：
//   docker compose exec -T neo4j cypher-shell -u neo4j -p password -f /init/neo4j_constraints.cypher
// =====================================================================

CREATE CONSTRAINT course_code  IF NOT EXISTS FOR (c:Course)         REQUIRE c.course_code  IS UNIQUE;
CREATE CONSTRAINT concept_code IF NOT EXISTS FOR (c:Concept)        REQUIRE c.concept_code IS UNIQUE;
CREATE CONSTRAINT kp_code      IF NOT EXISTS FOR (k:KnowledgePoint) REQUIRE k.kp_code      IS UNIQUE;
CREATE CONSTRAINT mc_code      IF NOT EXISTS FOR (m:Misconception)  REQUIRE m.mc_code      IS UNIQUE;

// 按课程过滤的常用属性索引
CREATE INDEX concept_course IF NOT EXISTS FOR (c:Concept)        ON (c.course_code);
CREATE INDEX kp_course      IF NOT EXISTS FOR (k:KnowledgePoint) ON (k.course_code);
