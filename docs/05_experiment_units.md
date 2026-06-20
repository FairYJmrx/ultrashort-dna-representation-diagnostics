# 05 细化实验单元矩阵

本文件把 `kmer信息学.md` 和相关文献整理中的方法学问题拆成具体实验单元。后续代码、配置、结果表都应按这些实验单元组织。

## 总体原则

实验从“DNA 序列信息假设”出发，而不是从模型名出发。每个实验单元必须回答：

1. 这个特征方案保留了什么信息。
2. 它丢弃了什么信息。
3. 它相对已有 baseline 的最小差异是什么。
4. 它在 75bp、噪声、近缘、未知类、宿主背景下是否仍然有效。
5. 它失败时说明什么，下一轮应该改什么。

## 实验单元总览

| 单元 | 信息假设 | 主要特征方案 | 关键对照 | 主要指标 |
|---|---|---|---|---|
| E01 | k 值存在 75bp 最优区间 | k-mer count/frequency | k=3/4/5/6/7/8/10/12 | F1、稀疏性、错误敏感性 |
| E02 | TF-IDF/L2 可增强 genome signature | TF-IDF、relative frequency、L1/L2 | raw count | F1、校准、特征稳定性 |
| E03 | SVD 只适合 vector route | TruncatedSVD/PCA | no reduction | F1、方差解释、泄漏检查 |
| E04 | 多 k 融合优于单 k | multi-k fusion | best single-k | F1、近缘混淆、维度/成本 |
| E05 | 顺序信息可能有额外价值 | ordered k-mer token | count-only、token shuffle | shuffle drop、F1 |
| E06 | token id 不能当连续数值证据 | token-id pseudo sequence | token-id permutation、embedding-CNN | permutation sensitivity |
| E07 | canonical/RC 影响双链一致性 | canonical k-mer、RC consistency | non-canonical | F1、RC invariance error |
| E08 | 大 k sequence 需要 embedding/hash | 12/13-mer token、hash/LSH | 7mer token、OOV baseline | OOV、memory、F1 |
| E09 | 小 k + 预训练/层级任务可能适合 unknown | 3-mer token、MLM、taxonomy head | no pretraining | OOD、genus fallback |
| E10 | raw-base 多通道保留碱基身份 | one-hot/Voss/tetrahedron | scalar mapping | F1、collision、noise |
| E11 | DNA 数值信号可提供频域/复杂度特征 | EIIP、三相标量、FFT | one-hot、count | spectrum separability |
| E12 | 位置-碱基联合编码可能捕获位置依赖 | joint phase/vector | no PE、learned PE | motif-position task |
| E13 | 属性门控 PE 是否带来生物先验收益 | gated PE | scalar gate、multi-property、learnable | ablation F1 |
| E14 | RoPE-like rotation 是否稳定相对位置 | rotary encoding | sinusoidal、learned、no PE | shift robustness |
| E15 | spaced/mismatch-tolerant k-mer 更抗错误 | spaced seed、mismatch neighborhood | contiguous k-mer | noisy F1、feature stability |
| E16 | 层级置信输出比强制 species 更合理 | confidence threshold、fallback | forced species | coverage-precision-recall |
| E17 | 可解释性是否支持临床判断 | prototype/motif attribution | black-box classifier | motif consistency |
| E18 | 数据库方法定义 clean 上限 | Kraken2/Centrifuge-like baseline | ML/DL features | clean/noisy/OOD gap |

## 读长与 k 值的共同原则

所有涉及 k-mer 的实验都不预设唯一 k。k 的选择必须由表达方案、读长和信息假设共同决定。

建议把读长作为正式实验变量：

```text
L = [69, 75, 100, 125, 150, 200]
```

第一轮可缩减为：

```text
L = [69, 75, 100, 150, 200]
```

k 值建议：

- vector composition：`k = [2,3,4,5,6,7,8,10,12]`
- token sequence：`k = [3,4,5,7,9,12,13]`
- biological-prior route：`k = [3,6,9]` 加上 `4/5/7` 对照
- position-base route：base-level、k=3/5/7、motif-level 都可测试

这里的关键不是“3-mer 一定正确”，而是检验：

1. 文献中纯 token/词表处理是否忽略了可用的生物先验。
2. 注入生物先验后，收益是否依赖 k=3。
3. 读长从 69/75 增长到 150/200 时，不同表示方案的信息增长是否同步。

## E01：k 值与 75bp 信息容量

### 假设

75bp 或 69bp read 中，4/5/6/7-mer 可能在信息量与稀疏性之间更平衡，12-mer vector 不会自然胜出；但当 read length 增长到 150/200bp 时，不同 k 的优劣可能变化。

### 特征方案

- count vector。
- relative frequency。
- k = 2, 3, 4, 5, 6, 7, 8, 10, 12。
- read length = 69, 75, 100, 125, 150, 200。

### 数据

- L0 toy：GC-rich、AT-rich、near-SNP、same-composition-different-order。
- L1 clean 75bp genome slices。
- L2 substitution/noisy 75bp。

### 指标

- accuracy、macro-F1、per-class F1。
- non-zero feature count per read。
- average collision / duplicate profile rate。
- single substitution feature perturbation ratio。
- runtime、memory。

### 判据

如果 7mer 或 5/6/7mer 稳定优于 12mer，并且 12mer 稀疏性和错误敏感性更高，则支持“75bp 下大 k 不天然更好”。

如果 150/200bp 下 10/12mer 的表现明显变好，说明大 k 的问题可能主要来自超短读长的信息容量，而不是 k 本身无用。

## E02：TF-IDF、relative frequency 与 normalization

### 假设

TF-IDF、relative frequency 和 L2 normalization 能增强 genome signature，但必须 train-only fit，避免泄漏。

### 特征方案

- raw count。
- relative frequency。
- TF-IDF。
- L1/L2 normalization。
- background-adjusted frequency。

### 必做检查

- split 后 fit TF-IDF。
- valid/test 只 transform。
- 记录 vocabulary 与 IDF 的 fit scope。

### 指标

- macro-F1。
- calibration ECE / Brier score。
- confusion matrix。
- feature norm distribution。

## E03：SVD/PCA 降维边界

### 假设

TruncatedSVD 适合 sparse k-mer vector，不适合已经变成 token sequence 的输入；SVD 必须 train-only fit。

### 特征方案

- no reduction。
- TruncatedSVD n_components = 16/32/64/128/256/512。
- PCA 只用于小 dense smoke test。

### 指标

- explained variance。
- downstream macro-F1。
- runtime/memory。
- leakage audit pass/fail。

### 失败解释

若 SVD 后 F1 下降，不代表 k-mer 无效，可能是投影维度太低或 signal 在低方差方向。

## E04：multi-k fusion

### 文献启发

PlasFlow 和 resource-saving k-mer 提示小/中 k distribution 很强，multi-k 可能比单 k 更稳定。

### 特征方案

- concat fusion：3+4+5+6+7-mer。
- probability fusion：各 k 独立分类后平均/加权。
- late fusion：stacking。

### 指标

- best single-k vs multi-k。
- 近缘物种 confusion reduction。
- 维度、运行时间、内存。

## E05：ordered k-mer token 的顺序贡献

### 假设

ordered k-mer token 只有在顺序信息真实有用时，才应优于 count-only；这个收益必须通过 shuffle 消融验证。

### 特征方案

- overlapping k-mer token sequence。
- k = 3/5/7/12。
- embedding + mean pooling。
- embedding + 1D CNN。
- embedding + GRU/BiLSTM。
- lightweight Transformer。

### 消融

- token shuffle。
- position shuffle。
- count-only。
- same-composition-different-order toy task。

### 指标

- F1。
- shuffle drop。
- same-composition task accuracy。
- attention/pooling mask correctness。

## E06：token-id pseudo-sequence CNN 审计

### 背景

旧代码中的 CNN 可能把 token id 当 float 输入 Conv1d，不是标准 embedding sequence model。

### 实验

- token-id CNN。
- token-id permutation CNN。
- random-id repeated seeds。
- Embedding -> CNN。
- count vector CNN/MLP。

### 判据

如果 token-id permutation 后性能大幅变化，说明模型利用了 id 数值排列偶然信号，不能作为标准 sequence 证据。

## E07：canonical k-mer 与反向互补一致性

### 假设

canonical k-mer 能降低双链冗余，RC consistency 可以提高方向不变性。

### 实验

- canonical vs non-canonical。
- read 与 reverse-complement read 的预测一致性。
- RC augmentation。
- RC consistency loss。

### 指标

- F1。
- RC invariance error。
- class probability KL divergence between read and RC(read)。

## E08：大 k token、hash 与 LSH

### 文献启发

DeepMicrobes/MetaTransformer 使用 12/13-mer token，但依赖 canonical、embedding、hash/LSH、attention 和较完整工程。

### 实验

- 12/13-mer vocab embedding。
- hashing trick embedding。
- LSH/sketch embedding。
- 7mer embedding 对照。

### 指标

- OOV 或 hash collision rate。
- memory。
- F1。
- noisy degradation。

## E09：小 k 预训练与层级任务

### 文献启发

BERTax 表明 3-mer + 预训练 + 层级 head 可服务 unknown taxa，但原文读长是 1500nt，不能直接外推到 75bp。

本项目不预设 3-mer 必然最佳。3-mer 只是三碱基先验和 BERTax-like small-token route 的一个候选点。需要与 4/5/7mer 以及 6/9mer 这类多三碱基单元对照。

### 实验

- 3-mer non-overlap / overlap。
- MLM 或 masked-kmer prediction。
- taxonomy multi-head：kingdom/genus/species。
- unknown/holdout split。

### 指标

- seen species F1。
- holdout genus accuracy。
- unknown rejection AUROC。
- hierarchical consistency error。

## E10：raw-base 多通道表示

### 假设

one-hot/Voss/tetrahedron 比单通道标量更能保留碱基身份。

### 特征方案

- one-hot / Voss。
- tetrahedron。
- EIIP。
- hydrogen-bond scalar。
- property channels：GC、purine、pyrimidine、EIIP、N mask。

### 指标

- F1。
- representation collision count。
- noisy F1。
- feature attribution stability。

## E11：三相信号与频域特征

### 假设

三相标量信号和 DNA signal processing 特征可能捕获低复杂度、周期性或宿主/微生物差异，但不应替代保留碱基身份的 baseline。

### 特征方案

- 三相标量。
- EIIP signal。
- FFT power spectrum。
- spectral entropy。
- low-complexity score。

### 指标

- spectrum class separability。
- low-complexity detection AUC。
- downstream F1。
- 与 one-hot/count 的互补性。

## E12：高维多频相位 joint encoding

### 假设

将 k-mer 属性强度、相位和位置融合，可能在位置相关任务中优于普通 learned embedding。

### 特征方案

- static prior。
- fully learnable。
- prior + learnable residual。

### 数据

- motif 在固定位置出现。
- 同 motif 不同位置。
- 同 composition 不同 order。

### 指标

- motif-position accuracy。
- shift robustness。
- F1。
- ablation drop。

## E13：属性调制位置编码

### 假设

DNA 属性门控位置编码能让模型按 k-mer 生物属性调节位置权重。

### 对照

- no PE。
- sinusoidal PE。
- learned PE。
- scalar gate。
- multi-property gate。
- learnable-only gate。

### 指标

- F1。
- gate entropy。
- gate collision rate。
- ablation drop。

## E14：RoPE-like 旋转编码

### 假设

RoPE-like 旋转可更好表达相对位置，使同一局部片段在不同 read 位置下表示更稳定。

### 对照

- no PE。
- sinusoidal PE。
- learned PE。
- RoPE-like 2D real rotation。

### 指标

- shifted motif consistency。
- F1。
- attention distance pattern。

## E15：spaced / mismatch-tolerant k-mer

### 文献启发

spaced seed 可提升对 mismatch 的容忍度；75bp 中连续 k-mer 容易被 substitution 破坏。

### 特征方案

- spaced k-mer patterns。
- mismatch neighborhood aggregation。
- minimizer/sketch。

### 指标

- substitution noisy F1。
- feature perturbation ratio。
- memory。
- false-positive rate。

## E16：层级置信、拒识与回退

### 假设

75bp read 未必足够支持 species-level，层级回退比强制 species 分类更符合临床证据。

### 实验

- confidence threshold。
- species -> genus -> kingdom fallback。
- unknown class。
- open-set holdout。

### 指标

- coverage-precision-recall curve。
- abstention rate。
- ECE/Brier。
- hierarchical consistency error。

## E17：可解释性与临床证据

### 假设

可解释 motif/prototype 能帮助判断模型是否学到 biologically plausible signal，而不是数据泄漏或 id 排列。

### 实验

- prototype subsequence。
- top k-mer attribution。
- saliency/integrated gradients。
- class-specific discriminative k-mer list。

### 指标

- prototype class purity。
- attribution stability across seeds。
- known motif overlap where available。

## E18：数据库 baseline 与 benchmark 难度审计

### 假设

Kraken2/Centrifuge 在 clean in-database 数据上接近满分说明 benchmark 太容易，不说明新方法无价值。

### 实验

- clean in-database。
- noisy reads。
- near species。
- strain/genome holdout。
- unknown taxa。
- host contamination。

### 指标

- clean/noisy/OOD performance gap。
- false positive rate。
- unclassified rate。
- runtime。

## 实验单元执行顺序

优先级顺序：

1. E01/E02/E03：先稳住 vector baseline 和数据泄漏审计。
2. E05/E06/E07：审计 sequence route 是否真的利用顺序和 embedding。
3. E10/E11：建立 raw-base 和信号处理对照。
4. E12/E13/E14：验证我们的位置-碱基联合编码。
5. E15/E16：加入鲁棒性和临床可信输出。
6. E04/E08/E09/E17/E18：作为扩展与论文增强实验。
