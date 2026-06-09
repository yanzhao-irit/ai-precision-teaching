# Real Course Data Normalization Report

Generated on: 2026-06-09 03:31:18

## Purpose

This report summarizes the transformation of anonymized course exports into simple normalized tables used by the teaching diagnosis system.

## Normalized vocabulary

- `student`: anonymized learner
- `subject`: course or class
- `work`: quiz, homework, exam, chapter test or global score
- `answer`: student result on a work
- `activity`: learning behavior such as video watching, task completion, discussion or attendance
- `concept`: course knowledge point
- `relation`: link between concepts
- `resource`: lesson, video, PDF, task or exercise
- `diagnosis`: generated later from answers, activities, concepts and relations

## Files processed

- `AI for CS students_anonymized.xlsx`
- `AI for every student\255680494_A__128633355__2025-2026-1_-202500_anonymized.xlsx`
- `AI for every student\255680494_A__128633357__2025-2026-1_-202500_anonymized.xlsx`

## Output tables

- Students: **0**
- Subjects: **3**
- Works: **54**
- Answers: **0**
- Activities: **0**
- Concepts: **14**
- Relations: **9**
- Resources: **189**

## Privacy note

The normalized files are generated from anonymized files. They still describe student learning behavior, so they remain local and are ignored by Git.