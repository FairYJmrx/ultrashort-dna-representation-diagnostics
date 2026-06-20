# 01 发表可行性评估：审稿人视角

## 当前项目进度

信息学表征子项目已经完成第一轮轻量闭环：

- 构建了人工轻量 DNA read 数据集。
- 覆盖 69/75/100/150/200bp 多读长。
- 覆盖 clean、substitution、N、trim、reverse-complement 等扰动。
- 实现并比较了 k-mer composition、raw-base/signaling、token audit、position-base joint encoding、RoPE-like、spaced-kmer phase、codon-frame channels、RC pooling 等表示。
- 形成了最终轻量对比报告：`results/runs/final_lightweight_comparison_report.md`。

## 当前最强结果

在 `toy_order_position` 控制任务中：

- ordinary k-mer embedding proxy 最高 macro-F1 约 0.797。
- random embedding mean/std 最高 macro-F1 约 0.726。
- 新的 prior-aware encodings 中，`spaced_kmer_phase`、`codon_frame_channels`、`rope_property`、`rope_onehot`、`kmer_property` 可达到 0.98-1.00。

这说明新表示在控制性任务中确实更强，但该结论仍属于轻量 benchmark 级别。

## 是否已经足以发表二区论文？

当前结论：**尚不足以直接投稿二区及以上生信/计算生物学论文，但已经具备一篇方法学论文的雏形。**

原因：

1. 目前主要是人工 toy 数据，审稿人会质疑外推到真实 mNGS read 的有效性。
2. ordinary embedding proxy 不等于完整 Transformer / BiLSTM / CNN sequence model。
3. 目前没有真实或半真实 genome-slice 数据。
4. 尚缺少严格的 exact composition-matched order-only 数据。
5. 尚缺少跨 seed 重复统计和显著性检验。
6. 尚缺少真实下游任务，例如 read-level species/genus classification、host contamination、unknown rejection。
7. 尚缺少模型层实验：轻量 CNN / tiny attention 是否能利用这些 encoding。

## 创新是否值得继续？

值得。

当前创新不是“又一个分类模型”，而是一个更清晰的 DNA short-read representation framework：

> 面向 69-75bp 超短 mNGS reads，系统比较 k-mer composition、token sequence、raw-base numerical representation 与 position/base/phase-aware biological priors，并提出 spaced-kmer phase、codon-frame property channels 和 RoPE-property encoding 等轻量表示。

这个主题具有方法学价值，因为它避开了“模型名堆叠”，把焦点放在短 read 的信息表达能力上。

## 审稿人最可能的质疑

### Q1：toy 数据太简单，是否真实？

必须补：

- small genome-slice benchmark。
- near-species / strain-like benchmark。
- noisy 69/75bp benchmark。
- host-like contamination。

### Q2：为什么不直接用 one-hot + CNN 或 k-mer token Transformer？

必须补：

- one-hot CNN。
- k-mer embedding CNN。
- tiny Transformer / attention。
- RoPE-property attention vs learned PE attention。

### Q3：spaced-kmer phase 是不是只是人为设计适配 toy 数据？

必须补：

- substitution gradient。
- indel stress。
- random seed repetitions。
- exact composition-matched order-only benchmark。
- ablation：remove spaced pattern、remove phase、remove property。

### Q4：能否用于 mNGS species identification？

必须补：

- 选取少量真实 bacterial reference genomes。
- 生成 69/75/100/150bp reads。
- 设置 in-database、near-genome holdout、unknown/OOD。
- 和 k-mer vector、ordinary token embedding、Kraken-like exact matching简化版或 Kraken2 外部结果比较。

### Q5：是否有生物解释？

必须补：

- top discriminative spaced-kmer / motif 分析。
- frame/channel contribution。
- RC consistency metric。
- perturbation sensitivity。

## 最现实的论文定位

不是现在就写成“新方法显著提升 mNGS 物种鉴定准确率”，而应写成：

> Representation-centric analysis and biologically informed encodings for ultra-short metagenomic reads.

也就是一篇短读长 DNA 表征方法学论文。mNGS species identification 是应用场景，但第一篇论文的核心卖点是 representation framework + controlled benchmark + biologically informed encodings。

## 当前结论

- **可以进入论文准备阶段。**
- **不能直接投稿。**
- **需要补完一个小而严格的 benchmark 和轻量模型验证。**
- 如果这台电脑无法完成深度模型训练，可以先完成草稿和轻量实验，把 heavy validation 列为 future work 或待补实验。
