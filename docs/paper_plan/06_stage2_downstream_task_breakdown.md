# 06 Stage 2 下游任务推进拆解

## 1. 当前关键判断

完整 mNGS 物种鉴定暂时不应作为第一阶段核心下游任务。

原因是：完整物种鉴定会同时依赖数据库覆盖、近缘物种划分、宿主背景、分类模型容量、训练数据规模和阈值策略。若现在直接做 species classifier，模型层和数据层的不成熟会掩盖“DNA 信息表征是否更好”这个主问题。

更合适的阶段目标是：

> 用多个轻量、可复现、信息维度明确的下游任务，证明不同 DNA 表征在短 read 场景下分别擅长或不擅长什么。

这不是回避下游任务，而是把下游任务拆成更小、更能解释表征差异的单元。

## 2. 是否必须训练分类模型

不必须训练大型分类模型，但论文不建议完全没有下游任务。

最低可接受组合：

1. 无训练任务：paired retrieval、reverse-complement consistency。
2. 轻量模型任务：contamination/QC detection、motif-position classification、OOD rejection。
3. 困难诊断任务：near-SNP discrimination，作为当前方法边界和下一步优化目标。

如果要支撑二区及以上论文，建议至少加入 tiny CNN 或 tiny attention 作为小模型验证。它不需要追求临床准确率，而是验证某些表征是否更适合某类模型。

## 3. 本阶段已经完成

- 创建综合轻量压力数据集：`data/toy_reads/toy_downstream_stress.csv`。
- 扩展下游任务脚本：`scripts/run_lightweight_downstream_tasks.py`。
- 支持 canonical k-mer 基线：`ckmer5_count_l2`、`ckmer7_tfidf_l2`。
- 完成 75bp 核心压力任务：
  - T1 paired retrieval。
  - T2 reverse-complement consistency。
  - T5 contamination/QC detection。
  - T8 OOD rejection。
- 完成 75bp 轻量分类任务：
  - T3 same-composition order。
  - T4 motif-position。
  - T7 near-SNP discrimination。
- 生成阶段报告：`results/runs/lightweight_downstream_stage2_report.md`。

## 4. 当前实验结论

### T1 paired retrieval

该任务能测试扰动鲁棒性，但当前 75bp 设置仍偏容易。不同扰动下最优方法不同：substitution 类扰动中 one-hot/RoPE/property 类表示较强，trim/indel 类扰动中 high-k TF-IDF 表示也很强。

结论：T1 适合作为稳定性指标，但不能单独作为论文主证据。

### T2 reverse-complement consistency

canonical k-mer 当前明显优于普通 k-mer，也强于当前 RC pooling 方案。

结论：canonical k-mer 必须作为正式基线。RC-aware 新方法不能只和普通 k-mer 比，必须和 canonical k-mer 比。

### T5 contamination/QC detection

该任务最适合当前论文阶段。`spaced_kmer_phase`、`property_channels`、`one_hot`、`rc_rope_pool`、`rope_property` 在当前压力集上优于普通 high-k TF-IDF。

结论：这是最适合替代早期 species identification 的下游任务之一，因为它轻量、实际、有区分度。

### T8 OOD rejection

k-mer count/canonical k-mer 在 centroid OOD rejection 中表现最好。

结论：全局 composition 对粗粒度未知类分离仍然有价值。论文应避免宣称某个新表征在所有任务都最好，而应强调任务适配性。

### T3/T4 order 与 position

当前 same-composition order 太容易，多数方法可达满分。motif-position 能验证位置信息，但也需要更难的 jitter 和 distractor 设计。

结论：这两类任务应作为正控制和方法解释，不宜直接作为最强主结果，除非后续加硬。

### T7 near-SNP discrimination

当前浅层模型基本接近 chance，只出现小幅改善。

结论：这是目前最重要的短板。近缘/耐药突变级别差异很可能需要 alignment-aware prototype、contrastive objective、tiny CNN/attention，或者真实参考片段上下文。

## 5. 下一步任务顺序

### P1：加硬 T3/T4

目标：让 order/position 任务不再过于容易。

具体任务：

1. 构建 exact base-composition matched reads。
2. 构建低阶 k-mer spectrum 近似匹配 reads。
3. 为 motif-position 加入 jitter。
4. 加入 distractor motif。
5. 比较 count-only、one-hot、property、RoPE、spaced-kmer-phase。

预期用途：形成论文中“顺序/位置能力”主图或补充图。

### P2：改进 RC-aware 表征

目标：让新方法至少接近 canonical k-mer 的链方向稳定性，同时保留 property/position 信息。

候选方案：

1. canonical spaced-kmer phase。
2. min(read, RC(read)) pooling on property channels。
3. RC contrastive pair distance regularization 的轻量代理。
4. canonical k-mer + property residual hybrid。

预期用途：回应审稿人对 strand invariance 的质疑。

### P3：近 SNP 困难任务专题

目标：把当前负结果转化为方法创新来源。

候选方案：

1. prototype read matching。
2. mutation-aware spaced seed。
3. edit-distance weighted k-mer。
4. local alignment score as auxiliary feature。
5. tiny CNN on one-hot/property channels。
6. contrastive clean/perturbed positive pairs。

预期用途：决定本论文是否可以扩展到“近缘物种/耐药突变”主线。

### P4：tiny model 验证

目标：回答“新表征适合什么模型”。

最低实现：

1. logistic/nearest-centroid/kNN 作为浅层基线。
2. tiny 1D CNN for one-hot/property/spaced-kmer channels。
3. tiny attention for RoPE-property。

判断标准：不是追求最高临床准确率，而是看表征与模型结构是否匹配。

### P5：真实 genome-slice 轻量基准

目标：从完全人工数据过渡到可发表的半真实数据。

候选数据源：

1. `D:\AI-NGS\AI_NGS_blood_ALL_P0.xlsx` 中筛选的血流感染相关物种。
2. `code-V3\data` 中已有 WGS FASTA。
3. 必要时下载少量公开参考基因组。

设计原则：

1. 不做深测序。
2. 从参考基因组切片生成 69/75/100/150bp reads。
3. 每个物种每个长度几十到几百条即可。
4. 重点选择近缘组：Candida、Klebsiella、Acinetobacter、Burkholderia、Enterobacter。

## 6. 进入完整物种鉴定的条件

只有当以下条件满足时，才建议进入完整 species identification：

1. 至少一个新表征在 T5 或加硬 T3/T4 上稳定优于强基线。
2. RC-aware 方案不明显弱于 canonical k-mer。
3. 近 SNP 或真实 genome-slice 任务至少出现可解释改善。
4. tiny model 验证能说明新表征适合某种模型结构。

否则，论文主题应保持为：

> ultra-short DNA read representation diagnostics and biologically informed feature design

而不是直接宣称解决 mNGS 物种鉴定。

## 7. 结果不理想时的迭代机制

每个任务失败时不直接放弃，而按以下顺序复盘：

1. 任务是否太容易或太难。
2. 对照基线是否公平。
3. 表征是否丢失了该任务所需的信息。
4. 模型是否适配该表征。
5. 是否有已有文献中的近似方案可借鉴。
6. 是否能从 LLM tokenization、信息论、DNA biochemical priors、alignment/prototype matching 中提出新变体。

每次新想法必须写入 `results/ideas_backlog.md`，并绑定至少一个实验任务和一个失败原因，避免思路中断或遗漏。
