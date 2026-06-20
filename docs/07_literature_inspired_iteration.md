# 07 文献启发的新方案迭代机制

本文件回答：如果我们提出的特征方案不优秀，如何继续思考多个可能的新方案，并再次投入实验。

## 迭代原则

失败后不随机换模型，而是从三个来源产生新方案：

1. 既有文献路线。
2. LLM / sequence representation learning。
3. 信息论与 DNA 信息学。

每个新方案必须先写成最小实验，而不是直接扩大到完整 benchmark。

## 失败类型到文献启发的映射

| 失败现象 | 优先借鉴文献/方向 | 新方案候选 |
|---|---|---|
| 12mer vector 稀疏且噪声敏感 | spaced seeds、MinHash、MetaTransformer hash/LSH | spaced k-mer、hash embedding、mismatch aggregation |
| 4/7mer count 强但近缘区分差 | KmerAperture、discriminative k-mer、CLARK | synteny-aware mismatching k-mer、class-specific k-mer |
| ordered token 不优于 count | DeepMicrobes、MetaTransformer | canonical 12mer embedding、mask-aware pooling、attention pooling |
| Transformer 从头训练不稳定 | BERTax、DNABERT、BarcodeBERT | small-k MLM、domain pretraining、contrastive read embedding |
| raw-base CNN 不稳定 | Waggoner eDNA ProtoPNet、DeepVirFinder | shallow CNN、prototype subsequence、noise augmentation |
| 位置编码无收益 | RoPE、relative position、GSP | relative motif position、local phase encoding、position dropout |
| species 强制分类误报高 | DeepMicrobes threshold、BERTax unknown、ICCTax hierarchy | confidence threshold、hierarchical fallback、OOD rejection |
| RC 方向不一致 | ICCTax RC consistency、canonical k-mer | RC consistency loss、strand-invariant pooling |
| 宿主/低复杂度影响大 | GSP、low-complexity filters | spectral entropy、DUST-like complexity、host-adjusted TF-IDF |

## LLM 启发方向

### L01：small-k masked language modeling

来源：

- BERTax 使用 3-mer token 和预训练。
- DNABERT 类方法说明 DNA token pretraining 可学习局部语言结构。

75bp 适配：

- 使用 k=3/4 overlap tokens。
- masked-kmer prediction。
- downstream taxonomy head。
- 比较 no-pretrain vs pretrain。

最小实验：

- L0/L1 小数据自监督预训练。
- 再做 toy 分类和 near-species 分类。

风险：

- 75bp 太短，预训练语料太小。
- 如果只是同一模拟 genome 内预训练，可能引入泄漏。

### L02：contrastive read embedding

来源：

- LLM embedding 与 metric learning。
- ICCTax compactness / metric learning。

方案：

- 正样本：同 species 或同 genome 相邻 slices。
- 增强：substitution、RC、trim。
- 负样本：近缘 species hard negatives。

指标：

- retrieval top-k。
- holdout genus/species。
- embedding cluster purity。

### L03：adapter / prefix prompt-like taxonomy conditioning

来源：

- LLM prompt / adapter 思路。

方案：

- 不直接把 taxonomy 当输出类别，而是把 kingdom/genus context 作为条件向量，引导 species head。
- 可用于层级回退和多头一致性。

最小实验：

- kingdom/genus/species 三头模型 vs conditional species model。

## 信息论启发方向

### I01：k-mer 信息增益选择

方案：

- 计算每个 k-mer 对标签的 mutual information / chi-square / log-odds。
- 构建 top-N discriminative k-mer feature。

回答：

- 哪些 k-mer 真的提供标签信息。
- 7mer 强是否来自少量高信息 k-mer。

### I02：熵与复杂度特征

方案：

- Shannon entropy。
- spectral entropy。
- low-complexity score。
- k-mer entropy。

用途：

- 识别低复杂度、adapter-like、host-like 或错误 reads。
- 作为质量/拒识辅助特征。

### I03：信息保留曲线

方案：

- 对每种表示计算压缩后维度与下游 F1 的关系。
- 画 dimension vs performance。

用途：

- 判断 SVD/embedding/sketch 是否压掉关键信息。

### I04：扰动信息损失

方案：

- 对每条 read 注入 1/2/3 个 substitution。
- 计算原表示与扰动表示距离。
- 比较距离变化和分类变化。

用途：

- 定量说明哪种表示对错误最敏感。

## DNA 信息学启发方向

### D01：spaced k-mer / spaced seed

目的：

- 减少单碱基错误对连续 k-mer 的破坏。

最小实验：

- 7mer contiguous vs spaced pattern。
- substitution 0%、1%、2%、5%。

### D02：minimizer / sketch signature

目的：

- 轻量压缩 read 的局部 k-mer 集合。

最小实验：

- minimizer sketch + logistic/SVM。
- 与 SVD 7mer vector 比较内存和 F1。

### D03：synteny-aware k-mer mismatch map

来源：

- KmerAperture 提醒普通 k-mer set 会丢 synteny。

方案：

- 对近缘 reads 记录 mismatching k-mer 的原始位置。
- 构建 mismatch-position profile。

用途：

- 近缘种或菌株区分。

### D04：RC-invariant but strand-aware representation

方案：

- canonical k-mer + strand flag。
- RC pooled embedding。
- RC consistency loss。

目的：

- 在保持方向不变性的同时，不完全丢失方向线索。

### D05：host-adjusted k-mer profile

方案：

- 建立 host/background k-mer profile。
- 使用 observed - expected 或 log-odds adjusted feature。

目的：

- 临床 mNGS 中降低宿主背景影响。

## 新方案进入实验的流程

```text
失败日志
  -> 失败类型归类
  -> 查找文献/LLM/信息论/DNA 信息学启发
  -> 写入 ideas_backlog
  -> 设计最小实验
  -> 实现 smoke test
  -> 与最近 baseline 对比
  -> accept / revise / reject
```

## 候选新方案优先级

第一优先级：

1. spaced k-mer。
2. multi-k fusion。
3. canonical + RC consistency。
4. true Embedding-CNN 替代 token-id CNN。
5. confidence threshold + hierarchical fallback。

第二优先级：

1. small-k MLM pretraining。
2. contrastive read embedding。
3. prototype subsequence model。
4. host-adjusted k-mer profile。
5. synteny-aware mismatch-position profile。

第三优先级：

1. RoPE-like advanced variants。
2. complex-valued implementation。
3. adapter-like taxonomy conditioning。
4. minimizer/sketch large-scale index。

## 迭代不会遗漏的执行约束

每次失败复盘必须更新：

- `results/failure_log.md`
- `results/ideas_backlog.md`
- 对应 `docs/06_feature_scheme_registry.md` 的方案状态
- 对应实验单元的状态

任何没有进入这四处记录的新想法，都不能直接进入主实验。
