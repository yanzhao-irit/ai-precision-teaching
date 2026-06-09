# Real Course Data Anonymization Report

Generated on: 2026-06-08 11:05:48

## Purpose

This report describes the anonymization process applied to the real course files. It does not contain raw student names or raw student numbers.

## Rules applied

- Student identifiers, names and account fields are replaced with anonymous IDs such as `S0001`.
- Phone numbers, emails and identity fields are replaced with `[removed]`.
- Raw files remain local in `data/raw/real_courses/` and must never be committed.
- Anonymized Excel files remain local in `data/processed/real_courses/anonymized/`.

## Summary

- Anonymous students detected: **0**
- Safe mapping file: `data\processed\real_courses\anonymized\student_mapping_safe.json`

## Files processed

### 05-getting-started.md

- Type: `md`

### AI for CS students.xlsx

- Type: `xlsx`
- Output: `data\processed\real_courses\anonymized\AI for CS students_anonymized.xlsx`
#### Sheet: `综合成绩`
- Rows: **83**
- Columns: **9**
- Rows processed: **0**
- Sensitive columns anonymized: none detected

#### Sheet: `学生学习进度详情`
- Rows: **83**
- Columns: **14**
- Rows processed: **0**
- Sensitive columns anonymized: none detected

#### Sheet: `章节学习次数`
- Rows: **62**
- Columns: **8**
- Rows processed: **0**
- Sensitive columns anonymized: none detected

#### Sheet: `任务点完成详情`
- Rows: **85**
- Columns: **90**
- Rows processed: **0**
- Sensitive columns anonymized: none detected

#### Sheet: `音视频观看详情`
- Rows: **85**
- Columns: **42**
- Rows processed: **0**
- Sensitive columns anonymized: none detected

#### Sheet: `讨论参与详情`
- Rows: **83**
- Columns: **11**
- Rows processed: **0**
- Sensitive columns anonymized: none detected

#### Sheet: `作业统计`
- Rows: **84**
- Columns: **36**
- Rows processed: **0**
- Sensitive columns anonymized: none detected

#### Sheet: `考试统计`
- Rows: **84**
- Columns: **6**
- Rows processed: **0**
- Sensitive columns anonymized: none detected

#### Sheet: `章节测验统计`
- Rows: **84**
- Columns: **36**
- Rows processed: **0**
- Sensitive columns anonymized: none detected

#### Sheet: `线下成绩统计`
- Rows: **83**
- Columns: **7**
- Rows processed: **0**
- Sensitive columns anonymized: none detected

#### Sheet: `签到详情统计`
- Rows: **84**
- Columns: **20**
- Rows processed: **0**
- Sensitive columns anonymized: none detected

#### Sheet: `综合成绩（各权重项百分制得分）`
- Rows: **83**
- Columns: **9**
- Rows processed: **0**
- Sensitive columns anonymized: none detected


### AI for every student.zip

- Type: `zip`
- Excel entries processed: **2**

#### AI for every student.zip::255680494╚╦╣ñ╓╟─▄╡╝┬█(A)_128633357_(2025-2026-1)-202500.xlsx
- Output: `data\processed\real_courses\anonymized\AI for every student\255680494_A__128633357__2025-2026-1_-202500_anonymized.xlsx`
#### Sheet: `综合成绩`
- Rows: **55**
- Columns: **13**
- Rows processed: **0**
- Sensitive columns anonymized: none detected

#### Sheet: `学生学习进度详情`
- Rows: **55**
- Columns: **15**
- Rows processed: **0**
- Sensitive columns anonymized: none detected

#### Sheet: `章节学习次数`
- Rows: **96**
- Columns: **8**
- Rows processed: **0**
- Sensitive columns anonymized: none detected

#### Sheet: `任务点完成详情`
- Rows: **57**
- Columns: **78**
- Rows processed: **0**
- Sensitive columns anonymized: none detected

#### Sheet: `音视频观看详情`
- Rows: **57**
- Columns: **150**
- Rows processed: **0**
- Sensitive columns anonymized: none detected

#### Sheet: `讨论参与详情`
- Rows: **55**
- Columns: **11**
- Rows processed: **0**
- Sensitive columns anonymized: none detected

#### Sheet: `作业统计`
- Rows: **56**
- Columns: **30**
- Rows processed: **0**
- Sensitive columns anonymized: none detected

#### Sheet: `考试统计`
- Rows: **56**
- Columns: **30**
- Rows processed: **0**
- Sensitive columns anonymized: none detected

#### Sheet: `章节测验统计`
- Rows: **56**
- Columns: **6**
- Rows processed: **0**
- Sensitive columns anonymized: none detected

#### Sheet: `课程报告`
- Rows: **55**
- Columns: **7**
- Rows processed: **0**
- Sensitive columns anonymized: none detected

#### Sheet: `签到详情统计`
- Rows: **56**
- Columns: **14**
- Rows processed: **0**
- Sensitive columns anonymized: none detected

#### Sheet: `综合成绩（各权重项百分制得分）`
- Rows: **55**
- Columns: **13**
- Rows processed: **0**
- Sensitive columns anonymized: none detected


#### AI for every student.zip::255680494╚╦╣ñ╓╟─▄╡╝┬█(A)_128633355_(2025-2026-1)-202500.xlsx
- Output: `data\processed\real_courses\anonymized\AI for every student\255680494_A__128633355__2025-2026-1_-202500_anonymized.xlsx`
#### Sheet: `综合成绩`
- Rows: **73**
- Columns: **13**
- Rows processed: **0**
- Sensitive columns anonymized: none detected

#### Sheet: `学生学习进度详情`
- Rows: **73**
- Columns: **15**
- Rows processed: **0**
- Sensitive columns anonymized: none detected

#### Sheet: `章节学习次数`
- Rows: **113**
- Columns: **8**
- Rows processed: **0**
- Sensitive columns anonymized: none detected

#### Sheet: `任务点完成详情`
- Rows: **75**
- Columns: **78**
- Rows processed: **0**
- Sensitive columns anonymized: none detected

#### Sheet: `音视频观看详情`
- Rows: **75**
- Columns: **150**
- Rows processed: **0**
- Sensitive columns anonymized: none detected

#### Sheet: `讨论参与详情`
- Rows: **73**
- Columns: **11**
- Rows processed: **0**
- Sensitive columns anonymized: none detected

#### Sheet: `作业统计`
- Rows: **74**
- Columns: **30**
- Rows processed: **0**
- Sensitive columns anonymized: none detected

#### Sheet: `考试统计`
- Rows: **74**
- Columns: **30**
- Rows processed: **0**
- Sensitive columns anonymized: none detected

#### Sheet: `章节测验统计`
- Rows: **74**
- Columns: **6**
- Rows processed: **0**
- Sensitive columns anonymized: none detected

#### Sheet: `课程报告`
- Rows: **73**
- Columns: **7**
- Rows processed: **0**
- Sensitive columns anonymized: none detected

#### Sheet: `签到详情统计`
- Rows: **74**
- Columns: **14**
- Rows processed: **0**
- Sensitive columns anonymized: none detected

#### Sheet: `综合成绩（各权重项百分制得分）`
- Rows: **73**
- Columns: **13**
- Rows processed: **0**
- Sensitive columns anonymized: none detected



### ai-precision-teaching-system.zip

- Type: `zip`
- Excel entries processed: **0**

