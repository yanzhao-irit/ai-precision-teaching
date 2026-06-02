# 数据登记本 · Data Registry

> 每次获取一项新数据，在这里登记一条。
> Add a new entry every time you acquire data.

---

## 数据登记 · Entries

<!-- 示例条目，研究生开始填写时删除 · Example, delete when filling in real data -->

```yaml
# 示例 · Example (replace with real entries)
- id: "D000"
  type: "EXAMPLE - delete me"
  type_cn: "示例 - 请删除"
  cohort: "2024-2025-Fall"
  source_person: "张老师 / Prof. Zhang"
  acquired_date: "2025-11-15"
  acquired_by: "学生 A / Student A"
  format: "xlsx"
  rows: 156
  columns: ["student_id", "name", "class", "final_score"]
  contains_pii: true
  anonymized: false
  storage_path: "data/raw/D000_example.xlsx"
  notes: "这是一条示例条目"
```

---

## 待办 · TODO

参考 [`docs/02-data-inventory.md`](../../docs/02-data-inventory.md) 中的清单逐项排查。
See data inventory document for the checklist to work through.
