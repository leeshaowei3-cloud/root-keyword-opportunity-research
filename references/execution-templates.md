# 执行模板

## 批次清单

```yaml
task_mode: root_keyword_discovery
batch_id: root-YYYYMMDD-001
root_pool_version: v1
root_pool_sha256: ""
market: us
language: en
device: desktop
roots: []
channels:
  - bidirectional_autocomplete
planned_depth: 2
budget_unit: queries
budget_total: 0
allowed_inputs: []
forbidden_inputs: []
step_status:
  autocomplete: pending
  semantic_screening: pending
  metric_enrichment: pending
  trends_validation: pending
  serp_validation: pending
  product_family_pool: pending
```

## 人工晋级表

| promotion_id | keyword | rule_status | category | sources | task_type | input | output | digital_deliverable | disposition | review_reason |
|---|---|---|---|---|---|---|---|---|---|---|
| | | | | | | | | | promoted/review/rejected | |

校验：

- `rule_pass + review + reject = unique_raw`
- `promotion_rows + clean_rejected = accounted_unique`
- `promoted + review + rejected + pending = promotion_rows`

## 指标观察表

| keyword | market | language | device | provider | match_type | checked_at | volume | cpc | kd | raw_value_ref |
|---|---|---|---|---|---|---|---:|---:|---:|---|
| | | | | | | | | | | |

每个不同 provider、market、device、match type 或日期保留独立观察行。

## SERP 复核表

| keyword | gate | market | language | device | search_type | checked_at | intent_group | page_type | direct_tool_count | brand_strength | gap_summary | counterevidence |
|---|---|---|---|---|---|---|---|---|---:|---|---|---|
| | pass/hold/fail | | | | | | | | | | | |

## 分支决策表

| root_or_branch | channel | window_size | new_keyword_rate | duplicate_rate | semantic_breadth | opportunity_density | drift_rate | stop_reason | remaining_unvisited | reopen_condition |
|---|---|---:|---:|---:|---:|---:|---:|---|---|---|
| | | | | | | | | | | |

## 产品机会族表

| family_id | tier | primary_keyword | secondary_keywords | user | moment | input | transformation | output | digital_deliverable | strongest_support | strongest_counterevidence | implementation_shape | difficulty | kill_risk | missing_evidence | cheapest_falsification | status |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| | deep_research/quick_test/observe/counterevidence_hold | | | | | | | | | | | | | | | | research_only |

## 状态写法

每一步使用结构化状态：

```yaml
status: pending | partial | complete | not_applicable | blocked
planned: 0
completed: 0
failed: 0
unvisited: 0
reason: ""
artifacts: []
reopen_condition: ""
```
