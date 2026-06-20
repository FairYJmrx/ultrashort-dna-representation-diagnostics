# 06 特征方案注册表与指标矩阵

本文件列出所有需要进入实验的 DNA 序列表达方式。任何新方案加入实验前，必须先在这里注册。

## 特征方案注册规则

每个方案必须包含：

```text
scheme_id:
name:
input_object:
preserved_information:
discarded_information:
main_risk:
required_controls:
required_metrics:
related_experiment_units:
status:
```

## 已注册方案

### F01：k-mer count vector

- input_object：read。
- preserved_information：全局 k-mer composition。
- discarded_information：顺序、绝对位置。
- main_risk：大 k 稀疏、错误敏感。
- required_controls：k sweep、same-composition-different-order。
- required_metrics：F1、sparsity、perturbation ratio。
- related_experiment_units：E01、E02、E03。
- status：planned。

### F02：relative frequency / normalized profile

- preserved_information：归一化 composition。
- main_risk：短 read 下计数波动被放大。
- controls：raw count、L1、L2。
- metrics：F1、feature norm、calibration。
- units：E02。
- status：planned。

### F03：TF-IDF k-mer profile

- preserved_information：样本集中更有区分度的 k-mer。
- main_risk：IDF 泄漏、稀有错误 k-mer 被放大。
- controls：train-only fit、count baseline。
- metrics：F1、ECE、feature stability。
- units：E02、E03。
- status：planned。

### F04：SVD compressed k-mer profile

- preserved_information：低秩 composition variation。
- discarded_information：可能丢失低方差判别信号。
- main_risk：全量 fit 泄漏、维度过低。
- controls：no SVD、train-only fit、components sweep。
- metrics：F1、explained variance、runtime。
- units：E03。
- status：planned。

### F05：multi-k fusion profile

- preserved_information：不同尺度 composition。
- main_risk：维度膨胀、重复信息。
- controls：best single-k。
- metrics：F1、near-species confusion、memory。
- units：E04。
- status：planned。

### F06：ordered k-mer token sequence

- preserved_information：局部 k-mer 顺序。
- discarded_information：通过 pooling 可能丢位置。
- main_risk：数据量不足、padding/mask 错误。
- controls：count-only、token shuffle、position shuffle。
- metrics：shuffle drop、F1。
- units：E05。
- status：planned。

### F07：token-id pseudo-sequence

- preserved_information：token 序列与 id 排列偶然信息。
- main_risk：把分类编号当连续数值，结论不可解释。
- controls：token-id permutation、Embedding-CNN。
- metrics：permutation sensitivity。
- units：E06。
- status：audit_required。

### F08：canonical k-mer / RC-consistent token

- preserved_information：双链等价信息。
- main_risk：可能丢失方向相关 signal。
- controls：non-canonical、strand flag。
- metrics：RC invariance error、F1。
- units：E07。
- status：planned。

### F09：hash / LSH k-mer token

- preserved_information：大 k token 近似身份。
- main_risk：hash collision。
- controls：exact vocab where feasible。
- metrics：collision rate、memory、F1。
- units：E08。
- status：planned。

### F10：small-k token with pretraining

- preserved_information：小 k 语言式上下文。
- main_risk：75bp 上上下文太短，预训练收益有限。
- controls：no pretraining、supervised only。
- metrics：OOD、hierarchical F1。
- units：E09。
- status：future。

### F11：one-hot / Voss raw-base

- preserved_information：完整碱基身份。
- main_risk：模型需自行学习 motif/composition。
- controls：scalar mapping、k-mer vector。
- metrics：F1、noise robustness、attribution。
- units：E10。
- status：planned。

### F12：tetrahedron representation

- preserved_information：多维几何碱基差异。
- main_risk：几何距离是否适合分类未知。
- controls：one-hot/Voss。
- metrics：F1、embedding separability。
- units：E10。
- status：planned。

### F13：EIIP / property channels

- preserved_information：理化属性先验。
- main_risk：属性碰撞，单独使用可能丢身份。
- controls：one-hot only、property-only、combined。
- metrics：collision、F1、ablation drop。
- units：E10、E11。
- status：planned。

### F14：三相标量信号

- preserved_information：三碱基周期/频域假设。
- discarded_information：碱基身份大量碰撞。
- main_risk：分类收益弱、解释过度。
- controls：one-hot、EIIP、random phase。
- metrics：spectrum separability、F1。
- units：E11。
- status：hypothesis。

### F15：高维多频相位 joint encoding

- preserved_information：位置 + k-mer/base 属性。
- main_risk：参数增加导致伪收益。
- controls：static prior、learnable-only、prior+residual。
- metrics：position task F1、ablation drop。
- units：E12。
- status：hypothesis。

### F16：attribute-gated positional encoding

- preserved_information：DNA 属性调制位置。
- main_risk：gate collision。
- controls：scalar gate、multi-property gate、learnable gate。
- metrics：gate entropy、F1。
- units：E13。
- status：hypothesis。

### F17：RoPE-like rotation

- preserved_information：相对位置结构。
- main_risk：75bp 太短，收益有限。
- controls：sinusoidal、learned、no PE。
- metrics：shift robustness、F1。
- units：E14。
- status：hypothesis。

### F18：spaced k-mer

- preserved_information：非连续 seed pattern。
- main_risk：pattern 选择影响大。
- controls：contiguous k-mer。
- metrics：substitution robustness、F1。
- units：E15。
- status：planned。

### F19：mismatch-tolerant k-mer aggregation

- preserved_information：近似 k-mer neighborhood。
- main_risk：过度聚合导致近缘物种混淆。
- controls：exact k-mer、spaced k-mer。
- metrics：noisy F1、false positive。
- units：E15。
- status：future。

### F20：prototype / interpretable motif representation

- preserved_information：可解释判别片段。
- main_risk：prototype 记忆训练数据。
- controls：black-box CNN、seed stability。
- metrics：prototype purity、attribution stability。
- units：E17。
- status：future。

## 指标矩阵

| 指标组 | 指标 | 必测方案 |
|---|---|---|
| 分类 | accuracy、macro-F1、per-class F1、confusion matrix | all |
| 层级 | species/genus/kingdom F1、hierarchical consistency | all classifiers |
| 置信 | ECE、Brier、coverage-precision-recall、abstention rate | E16/all final |
| 信息保留 | sparsity、collision rate、profile duplicate rate | vector/raw/token |
| 鲁棒性 | substitution degradation、N masking、trim degradation | all |
| 顺序贡献 | token shuffle drop、position shuffle drop | token/position schemes |
| 位置贡献 | shifted motif consistency、position ablation drop | F15/F16/F17 |
| 双链一致 | RC invariance error、RC KL divergence | canonical/sequence/raw |
| 成本 | runtime、memory、feature dimension、OOV/collision | all |
| 可解释 | top k-mer stability、prototype purity、attribution stability | final candidates |

## 进入主实验的最低要求

一个新特征方案进入主实验前，至少要：

1. 在 L0 toy 数据通过维度和基本行为测试。
2. 有一个明确 baseline。
3. 有一个直接消融实验。
4. 有记录失败模式的方法。
5. 明确它回答的是 composition、order、base identity、position、noise robustness、hierarchical confidence 中的哪一类问题。
