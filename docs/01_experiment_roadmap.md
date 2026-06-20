# 01 实验流程拆解

## 总体流程

```text
研究假设
  -> 构造数据层
  -> 实现输入表示
  -> 表征审查
  -> 下游模型
  -> 消融实验
  -> 鲁棒性测试
  -> 结果复盘
  -> 提出下一轮方案
```

本 roadmap 的执行单位不是“某个模型”，而是 [05_experiment_units.md](05_experiment_units.md) 中的 E01-E18。每个单元都包含：信息假设、特征方案、数据构造、消融、指标、失败解释和下一步。

## 从文献整理导出的核心实验问题

`kmer信息学.md` 与准确率口径审计共同指向八个必须验证的问题：

1. 75bp 下 4/5/6/7-mer 是否比 12-mer vector 更稳定。
2. count、relative frequency、TF-IDF、background-adjusted frequency、SVD 后 dense vector 到底谁贡献有效信息。
3. sequence route 是否真的利用顺序，而不是 token id、composition 或数据 split 偶然信号。
4. raw-base one-hot/Voss/tetrahedron 是否优于单通道标量映射。
5. 三相标量、EIIP、FFT 等信号处理特征是否提供互补信息，还是只适合质量/低复杂度检测。
6. 位置-碱基联合编码、attribute-gated PE、RoPE-like rotation 是否在位置相关任务中有真实收益。
7. noisy 75bp、QC trimmed、near species、unknown taxa、host background 是否改变各表示法排序。
8. species-level 强制分类是否不如带 confidence threshold 的 genus/kingdom 层级回退。
9. 读长从 69/75bp 增长到 100/150/200bp 时，不同表达方案的信息保留和鲁棒性是否线性增强。
10. k 值是否应由表达方案和读长共同决定，而不是固定为 3mer、7mer 或 12mer。

## 当前数据策略

当前阶段采用轻量人工数据集，详见 [08_lightweight_dataset_design.md](08_lightweight_dataset_design.md)。

第一轮推荐：

```text
species = 3
reads_per_species = 20-40
lengths = [69, 75, 100, 150, 200]
conditions = [clean, substitution_1%, N_3%, trim_to_69, reverse_complement]
```

这会生成约 960-3000 条 reads，仍然非常轻量，但足以观察：

- k 值与读长共同变化。
- clean/noisy/RC 条件下的特征鲁棒性。
- 近缘物种与 composition 差异物种的不同难度。
- 是否需要轻量分类器或小神经网络。

准确率只是辅助可分性指标，不作为真实临床性能结论。

## 实验单元优先级

### 第一优先级：建立可靠 baseline 与审计当前风险

- E01：k 值与 75bp 信息容量。
- E02：TF-IDF、relative frequency 与 normalization。
- E03：SVD/PCA 降维边界与 train-only fit。
- E05：ordered k-mer token 的顺序贡献。
- E06：token-id pseudo-sequence CNN 审计。
- E07：canonical k-mer 与反向互补一致性。

### 第二优先级：建立所有表达方式的公平对照

- E10：raw-base 多通道表示。
- E11：三相信号与频域特征。
- E12：高维多频相位 joint encoding。
- E13：属性调制位置编码。
- E14：RoPE-like 旋转编码。

### 第三优先级：从临床约束和失败模式扩展

- E04：multi-k fusion。
- E08：大 k token、hash 与 LSH。
- E09：小 k 预训练与层级任务。
- E15：spaced / mismatch-tolerant k-mer。
- E16：层级置信、拒识与回退。
- E17：可解释性与临床证据。
- E18：数据库 baseline 与 benchmark 难度审计。

## P1：toy-read 数据层

### 目标

用少量人工 DNA reads 验证所有编码、模型输入维度、消融逻辑和指标计算。

### 初始数据设计

构造 3 到 5 个“物种/类别”，每类 5 到 20 条 75bp reads。reads 不必真实来自完整基因组，但需要有可控结构：

- 类别 A：GC 偏高。
- 类别 B：AT 偏高。
- 类别 C：与 A 近缘，只含少量 SNP。
- 类别 D：局部 motif 相同但位置不同。
- 类别 E：混入 N、末端 substitution、短截断。

### 要回答的问题

- k-mer count 能否区分 GC/AT 差异。
- ordered token 能否区分同 motif 不同位置或不同顺序。
- raw-base 编码能否保留碱基身份。
- position-aware 编码能否区分位置相关模式。

## P2：composition baseline

### 方案

- k = 3, 4, 5, 6, 7, 8, 12。
- count、relative frequency、TF-IDF。
- no reduction、TruncatedSVD。
- Logistic Regression、Linear SVM、RandomForest、MLP。

### 必做消融

- k 值扫描。
- normalization 对比。
- TF-IDF vs count。
- SVD 组件数扫描。
- reverse-complement canonical vs non-canonical。

### 预期失败

- 12-mer 在 75bp toy 或小样本中极度稀疏。
- SVD 在小数据上不稳定。
- count-only 无法区分同组成不同顺序。

## P3：ordered k-mer token baseline

### 方案

- read -> overlapping k-mer tokens。
- token id -> embedding。
- 平均池化、1D CNN、BiLSTM/GRU、轻量 Transformer。

### 必做消融

- token shuffle：打乱 token 顺序。
- position shuffle：保留 token 但打乱位置编码。
- token-id permutation：随机重映射 token id，验证模型是否误用 id 数值大小。
- count-only vs ordered-token。

### 关键判断

如果 ordered token 优于 count-only，并且 token shuffle 后明显下降，才说明顺序信息确实有贡献。

## P4：raw-base numerical representation

### 方案

- one-hot / Voss。
- EIIP。
- tetrahedron。
- hydrogen-bond scalar。
- GC/purine/pyrimidine property channel。
- FFT/power spectrum exploratory features。

### 必做消融

- 单通道 scalar vs 多通道 one-hot。
- 是否加入 N mask。
- 末端噪声与 substitution 噪声。
- CNN vs 简单线性模型。

### 关键判断

如果 scalar 编码表现差但 one-hot 表现好，说明信息碰撞明显，不应把标量编码当作主路线。

## P5：position-base joint encoding

### 方案

- no PE。
- sinusoidal PE。
- learned PE。
- attribute-gated PE。
- RoPE-like 2D real rotation。
- prior + learnable residual。

### 必做消融

- 去掉位置。
- 去掉碱基属性。
- 固定 prior vs learnable。
- 改变 motif 位置的 stress test。

### 关键判断

若位置编码收益只出现在位置相关 toy 任务，而不出现在 composition 任务，说明它捕获的是正确类型的信息；若所有任务均无收益，要排查实现、模型容量和任务设定。

## P6：统一 benchmark

### 数据层级

| 层级 | 数据 | 目的 |
|---|---|---|
| L0 | toy controlled reads | 验证实现与假设 |
| L1 | small genome slices | 小规模真实序列 sanity check |
| L2 | noisy 75bp reads | 测鲁棒性 |
| L3 | near-species / strain holdout | 测近缘和泛化 |
| L4 | host background / low abundance | 临床式压力测试 |

### 指标

- Accuracy。
- Macro-F1。
- per-class F1。
- confusion matrix。
- top-k accuracy。
- unknown rejection AUROC。
- calibration ECE。
- runtime。
- memory。
- feature sparsity。

## P7：结果不理想后的新方案迭代

新方案不直接凭感觉加入主实验。每个新方案必须优先从文献、LLM 表征学习、信息论或 DNA 信息学中寻找启发，并填写：

```text
失败现象：
失败可能原因：
新增假设：
最小可验证实验：
预期改善指标：
如果失败，下一步分支：
```

例如：

```text
失败现象：ordered token 不优于 count-only。
失败可能原因：toy 数据没有顺序相关信号，或模型只学到了 composition。
新增假设：只有同组成不同排列的 reads 才能显示顺序价值。
最小实验：构造相同 5-mer 频率但不同 motif 顺序的数据。
预期改善指标：ordered token > count-only，shuffle 后下降。
如果失败：检查 tokenizer、embedding、模型容量和标签设计。
```

具体机制见 [07_literature_inspired_iteration.md](07_literature_inspired_iteration.md)。
