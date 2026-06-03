# AI Teaching Prototype Demo

## Goal

This prototype shows how a knowledge graph can help explain student mistakes in an AI course.

Instead of only saying that an answer is correct or incorrect, the system tries to identify where the difficulty may come from.

Example:

A student fails a question about **Neural Network**.
The system checks the knowledge graph and suggests that the issue may come from **Dot Product**, **Matrix** or **Vector**.

## What is included

* AI course knowledge graph data
* Synthetic student answers
* Neo4j import script
* Diagnosis and report generation script
* Student reports
* Class summary
* Simple web presentation

## How to run

Start Neo4j first.

Then run:

```powershell
python scripts/import_ai_demo.py
python scripts/diagnose_ai_demo.py
```

To open the web page:

```powershell
python -m http.server 8000
```

Then open:

```text
http://localhost:8000/web/
```

## Link with the four project problems

### 1. Understanding mistakes

The system gives a possible explanation, not only a score.

### 2. Linking errors to concepts

Questions are linked to concepts, and concepts are linked to prerequisites.

### 3. Personalized support

Each student can receive a specific report with recommendations.

### 4. Teacher support

The class summary helps identify common difficulties.

## Current limits

* The data is synthetic.
* The graph is still small.
* The diagnosis gives possible causes, not definitive proof.
* The web page is static for now.
