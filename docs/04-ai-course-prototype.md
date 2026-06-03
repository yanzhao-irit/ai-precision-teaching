AI Course Knowledge Graph Prototype

1. Objective
This first prototype aims to demonstrate how a knowledge graph can support error diagnosis in an AI course.
The main idea is not only to detect whether a student answer is correct or incorrect, but to understand why the mistake may have happened. In particular, a student may fail a question about a visible concept, such as Neural Network, while the real difficulty may come from an earlier prerequisite, such as Dot Product, Matrix, or Vector.
The prototype therefore connects:
•	AI course concepts;
•	prerequisite relationships between concepts;
•	questions and the concepts they evaluate;
•	student answers;
•	possible root causes of mistakes.

2. Knowledge Graph Principle
We model the AI course as a knowledge graph. Each concept is connected to its prerequisites.
Example:
Neural Network
├── requires Dot Product
├── requires Matrix
├── requires Vector
├── requires Loss Function
└── requires Machine Learning
This structure allows the system to reason backward from a visible mistake to possible earlier learning gaps.
For example, if a student fails a question about Neural Network, the system does not immediately conclude that the student only lacks knowledge about neural networks. It also checks whether the issue may come from mathematical prerequisites such as Dot Product, Matrix, or Vector.

3. Visualizing the Knowledge Graph
The following Cypher query visualizes the prerequisite graph around the concept Neural Network:
MATCH path = (:Concept {label: "Neural Network"})-[:REQUIRES*1..4]->(:Concept)
RETURN path
LIMIT 25;
This query displays the prerequisite paths from the visible concept to earlier concepts.
The result shows that Neural Network is connected to several prerequisite concepts, including:
•	Dot Product;
•	Matrix;
•	Vector;
•	Loss Function;
•	Machine Learning.
This is important because these prerequisite concepts may explain why a student fails a question on neural networks.

4. Student Mistake Detection
The following query lists the incorrect answers made by students:
MATCH (s:Student)-[a:ANSWERED]->(q:Question)-[:EVALUATES]->(c:Concept)
WHERE a.is_correct = false
RETURN s.student_id AS student,
       q.question_id AS failed_question,
       q.question_text AS question,
       c.label AS visible_error_concept,
       a.score AS score,
       a.error_type AS error_type
ORDER BY student, failed_question
LIMIT 10;
This query identifies the visible error. For example, it can show that a student failed a question evaluating Neural Network.
However, this visible concept is not necessarily the root cause of the error.

5. Possible Root Cause Detection
The following query goes one step further. It starts from the failed question, identifies the visible concept, then explores the prerequisite paths in the knowledge graph:
MATCH (s:Student)-[a:ANSWERED]->(q:Question)-[:EVALUATES]->(visible:Concept)
WHERE a.is_correct = false
MATCH path = (visible)-[:REQUIRES*1..3]->(pre:Concept)
RETURN 
  s.student_id AS student,
  q.question_id AS failed_question,
  visible.label AS visible_error,
  pre.label AS possible_previous_gap,
  length(path) AS prerequisite_distance,
  "The student failed a question about " + visible.label +
  ", but the knowledge graph suggests that the difficulty may come from a previous prerequisite: " +
  pre.label AS explanation
ORDER BY student, failed_question, prerequisite_distance
LIMIT 20;
This query produces an explainable diagnosis.
Example interpretation:
The student failed a question about Neural Network,
but the knowledge graph suggests that the difficulty may come from a previous prerequisite: Dot Product.
This directly addresses the main educational problem: a mistake on a current chapter may actually be caused by a gap in a previous chapter.

6. Current Prototype Pipeline
The current prototype follows this pipeline:
AI course concepts
→ prerequisite graph in Neo4j
→ questions linked to concepts
→ student answers
→ failed questions
→ prerequisite traversal
→ possible root cause diagnosis
The prototype currently uses:
•	Neo4j for graph storage and visualization;
•	Cypher queries for graph exploration;
•	Python scripts for importing data and generating diagnosis outputs;
•	synthetic data for students and answers.

7. Current Result
The first version successfully demonstrates that:
1.	AI course concepts can be represented as a knowledge graph.
2.	Questions can be linked to the concepts they evaluate.
3.	Student mistakes can be connected to visible concepts.
4.	The graph can be used to identify possible prerequisite gaps.
5.	The diagnosis is explainable and not only based on a black-box LLM.
This is an important first step toward an AI-empowered teaching support system.

8. Next Improvements at the moment 
The next step is to move from “possible root causes” to “most likely root causes”.
To do this, the system should compute a suspicion score using several indicators:
•	distance in the prerequisite graph;
•	previous student performance on prerequisite concepts;
•	question response time;
•	video completion rate;
•	type of error;
•	repeated mistakes on related concepts.
A future score could follow this logic:
Suspicion score =
0.40 × weakness on prerequisite concept
+ 0.25 × proximity in the knowledge graph
+ 0.20 × low video completion
+ 0.15 × abnormal response time
This would allow the system to rank the most probable root causes and generate more precise recommendations for teachers and students.

9. Future Objective
The long-term objective is to build a system where the teacher can select a student or a question and immediately obtain:
•	the visible error;
•	the evaluated concept;
•	the prerequisite path;
•	the most likely root cause;
•	a clear explanation;
•	a personalized recommendation.
The LLM should not be the only decision-maker. The diagnosis should first rely on explicit graph relationships and student activity data. The LLM can later be used to reformulate explanations and generate personalized exercises.

