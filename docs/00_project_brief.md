# 00 项目总述

## 一句话定位

本项目研究 75bp 临床 mNGS read-level 场景中，k-mer 及其相近序列表征方法在信息保留、分类性能、鲁棒性和可解释性上的差异。

## 不先做什么

暂不优先使用超大模拟数据或完整临床规模数据。原因是当前阶段的关键问题不是算力规模，而是：

- 表示法是否正确实现。
- 是否真的保留顺序或位置信息。
- 不同方案的比较口径是否公平。
- 失败时能否知道失败在哪里。

因此第一阶段采用少量人工构造 DNA reads，快速验证每个方案的数学和代码行为。

## 主要研究对象

### A. k-mer composition

输入：

```text
read -> k-mer count / frequency / TF-IDF / normalized vector
```

核心问题：

- 75bp 下 4/5/6/7/8/12-mer 的有效信息和稀疏性如何变化。
- TF-IDF、relative frequency、L1/L2 normalization、SVD 是否带来稳定收益。
- 统计型特征在噪声和近缘物种下的失效边界在哪里。

### B. ordered k-mer token

输入：

```text
read -> overlapping k-mer token sequence -> embedding/model
```

核心问题：

- 顺序信息是否真的比 count-only 多提供可分类信号。
- canonical k-mer、token shuffle、position shuffle、token-id permutation 等消融后性能如何变化。
- 小 k 和大 k 在 75bp 下哪个更稳定。

### C. raw-base numerical representation

输入：

```text
read -> A/C/G/T one-hot, Voss, EIIP, tetrahedron, scalar signal
```

核心问题：

- 直接保留碱基身份是否优于 k-mer 汇总。
- 单通道标量编码是否因碰撞损失过多信息。
- FFT/spectrum 等信号处理特征是否能提供补充诊断。

### D. position-base joint encoding

输入：

```text
read or k-mer token + position -> joint vector/signal
```

核心问题：

- 位置信息与碱基/k-mer 属性融合后是否增加有效信息。
- sinusoidal PE、learned PE、RoPE-like rotation、attribute-gated PE 的收益来自哪里。
- 如果没有收益，是假设不成立、实现不对，还是数据任务不需要位置。

## 成功标准

第一阶段成功不要求模型准确率很高，而要求：

1. 每条路线都有可运行的最小实现方案。
2. 每个实验能明确说明保留和丢失的信息。
3. 每个对比有统一数据、统一 split、统一指标。
4. 每个失败结果能导出下一轮具体问题。

## 阶段里程碑

| 阶段 | 目标 | 产物 |
|---|---|---|
| P0 | 项目规划 | docs、configs、实验矩阵 |
| P1 | toy reads 与基础编码 | toy 数据、编码脚本、单元测试 |
| P2 | composition baseline | k-mer count/TF-IDF/SVD baseline |
| P3 | sequence token baseline | token sequence、shuffle 消融 |
| P4 | raw-base baseline | one-hot/Voss/scalar/FFT 特征 |
| P5 | position-aware encoding | PE/RoPE-like/gated PE 对比 |
| P6 | 统一 benchmark | 指标表、失败模式表、可视化 |
| P7 | 新方案迭代 | 新候选方案、小实验、复盘 |
