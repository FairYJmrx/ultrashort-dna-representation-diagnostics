# 04 结果复盘协议

## 每次实验后的最小报告

每次 run 结束后，在对应 `results/runs/<run_id>/report.md` 中记录：

```text
run_id:
date:
data:
split:
representation:
model:
ablation:
seed:
metrics:
main_observation:
failure_mode:
next_action:
```

## 指标表模板

| run_id | data | representation | model | ablation | accuracy | macro_f1 | runtime_s | memory_mb | note |
|---|---|---|---|---|---:|---:|---:|---:|---|

## 失败模式表模板

| run_id | symptom | likely_cause | evidence | next_minimal_test | status |
|---|---|---|---|---|---|

## 判断规则

### 不足以支持方案有效的情况

- 只在一个 seed 上提升。
- 只在过于简单的 toy 数据上提升。
- 没有与 count-only 或 no-position baseline 对比。
- 没有 shuffle/permutation 消融。
- train/test 有潜在泄漏。
- 指标提升但 runtime/memory 不可接受。

### 可以推进到下一阶段的情况

- 至少 3 个 seed 方向一致。
- 对应消融支持信息来源。
- confusion matrix 显示改善发生在预期类别。
- 失败边界清楚。
- 代码和配置可复现。

## 复盘输出

每次复盘只允许产生三种决策：

```text
accept: 保留为候选主方案。
revise: 修改一个明确变量后重测。
reject: 当前证据不支持，归档原因。
```

避免“继续随便试试”的状态。
