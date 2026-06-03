# AI Course Error Diagnosis Demo

## Goal

This demo presents a first version of an error diagnosis system for an AI course.

The goal is simple: when a student makes a mistake, we do not only want to know that the answer is wrong. We want to understand where the difficulty may come from.

For example, if a student fails a question about **Neural Networks**, the real problem may come from an older prerequisite such as **Dot Product**, **Matrix**, or **Vector**.

---

## What was done

For this first version, I added:

* a small knowledge graph for an AI course;
* links between AI concepts and their prerequisites;
* questions linked to the concepts they evaluate;
* synthetic student answers;
* a script to import the graph into Neo4j;
* a first script to detect possible causes of mistakes.

The goal was to keep the prototype simple, clear and functional.

---

## How it works

The current logic is:

```text
Student answer
→ failed question
→ concept evaluated by the question
→ prerequisite concepts
→ possible cause of the mistake
```

Example:

```text
Student S001 failed question Q006.
Q006 evaluates Neural Network.
Neural Network requires Dot Product, Matrix and Vector.
The system suggests that the mistake may come from one of these prerequisites.
```

---

## Link with the 4 project problems

### 1. Understanding student mistakes

The prototype does more than saying “correct” or “incorrect”.

It starts to explain the mistake by checking the concept evaluated by the question and the concepts needed to understand it.

### 2. Linking errors to course concepts

Each question is linked to a course concept.

Each concept is also linked to its prerequisites.

This makes it possible to connect an error to a wider learning path.

### 3. Preparing personalized support

If the system detects that a student may have a problem with a prerequisite, this can later be used to suggest specific exercises or videos.

Example:

```text
Review Dot Product before retrying Neural Network exercises.
```

### 4. Helping teachers

The same approach can help teachers understand class difficulties.

If many students fail questions about Neural Networks, and the graph shows that Dot Product is often involved, the teacher can decide to review this prerequisite with the class.

---

## Current limits

This is only a first prototype.

For now:

* the data is synthetic;
* the knowledge graph is still small;
* the system gives possible causes, not a final diagnosis;
* there is no dashboard yet;
* recommendations are still basic.

---

## Next step

The next useful step is to generate a simple report for each student.

Example:

```text
Student: S001
Failed question: Q006
Visible concept: Neural Network
Possible previous gap: Dot Product

Explanation:
The student failed a question about Neural Network. Since Dot Product is a prerequisite, it may be useful to review it first.

Recommendation:
Review Dot Product, then retry Neural Network exercises.
```

This would make the result easier to understand without using Neo4j directly.
