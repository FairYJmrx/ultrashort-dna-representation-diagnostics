# 02 二区论文所需实验清单

本文档从审稿人角度拆解：若要把该子项目发展成一篇质量合格的二区及以上论文，还需要哪些实验。

## 总体实验结构

```text
Controlled toy benchmark
  -> exact composition/order benchmark
  -> small genome-slice benchmark
  -> noisy/trimmed short-read benchmark
  -> near-species / OOD benchmark
  -> lightweight model benchmark
  -> ablation and interpretability
```

## A. 数据集实验

### A1：Controlled toy benchmark

状态：已初步完成。

还需补：

- 每个数据集 5-10 个随机 seeds。
- 每组报告 mean ± std。
- exact composition matched 数据。

目的：

- 验证表达方式是否保留 composition、order、position、RC、noise 信息。

### A2：Exact composition-matched order-only benchmark

必须新增。

设计：

- 多类别 reads 具有相同单碱基组成。
- 尽量匹配 2-mer/3-mer composition。
- 类别差异来自 motif order、local inversion、block permutation。

目的：

- 防止 composition baseline 通过 GC/AT 差异“作弊”。
- 专门检验 ordered token、RoPE-property、spaced-kmer phase、codon-frame channels。

### A3：Motif-position benchmark

状态：已有初版。

还需补：

- motif 前端、中部、末端、随机位置。
- motif 长度 6/9/12。
- 位置 jitter。
- reverse-complement motif。

目的：

- 检验 position encoding 是否真的有用。

### A4：Small genome-slice benchmark

必须新增。

设计：

- 选 5-10 个细菌 reference genomes。
- 每个 genome 随机切 69/75/100/150bp reads。
- 每物种 1000-5000 reads 即可。

若本机资源有限：

- 先使用 NCBI 小型 fasta 或已有 `code-V3` 数据。
- 只跑轻量模型。

目的：

- 回应 toy 数据真实性不足的问题。

### A5：Near-species / strain-like benchmark

必须新增。

设计：

- 从同一 genus 选 2-3 个近缘物种。
- 或从同一人工 genome 注入低比例 SNP 得到 strain-like 类别。
- 设置 genome holdout。

目的：

- 检验新表示是否帮助近缘区分。

### A6：Noise and QC benchmark

部分已完成。

还需补：

- substitution 0.5%、1%、2%、5%。
- terminal substitution gradient。
- N random / cluster / terminal。
- trim to 69/60/50。
- indel stress。

目的：

- 验证 spaced-kmer phase 是否真的更抗噪。

### A7：Host/background and OOD benchmark

必须新增。

设计：

- host-like reads 作为污染背景。
- unknown species 测试时出现，训练不出现。
- 输出 forced species vs confidence fallback。

目的：

- 连接 mNGS 临床场景。

## B. 表示方法实验

### B1：Baseline representations

必须包括：

- k-mer count/frequency/TF-IDF。
- k=3/4/5/6/7/8/10/12。
- one-hot/Voss。
- tetrahedron。
- EIIP。
- hydrogen scalar。
- ordinary k-mer token embedding proxy。

### B2：Proposed representations

当前应主打：

1. spaced-kmer phase。
2. codon-frame property channels。
3. RoPE-property / RoPE-onehot.
4. joint phase prior + residual。
5. RC-consistent pooling。

### B3：Ablation

必须做：

| 方法 | 消融 |
|---|---|
| spaced-kmer phase | remove spaced pattern, remove phase, remove property |
| codon-frame channels | remove frame channel, collapse frames |
| RoPE-property | learned PE, sinusoidal PE, no PE, property no rotation |
| joint phase residual | prior only, residual only, prior + residual |
| RC pooling | no RC, average only, difference only |

## C. 模型实验

### C1：Non-neural lightweight classifiers

已部分完成。

继续保留：

- kNN。
- nearest centroid。
- logistic regression。
- linear SVM。

目的：

- 评价表示本身的线性/局部可分性。

### C2：Shallow CNN

建议必须补。

原因：

- raw-base one-hot 和 property channels 最适合 CNN。
- Waggoner/eDNA 类文献支持短序列浅层 CNN。
- 审稿人会问为什么不用 CNN。

### C3：Embedding-CNN

建议必须补。

目的：

- 正式对照普通 k-mer token embedding。

### C4：Tiny attention / Transformer

建议补，但如果电脑资源有限，可以做极小模型。

必须比较：

- learned PE。
- sinusoidal PE。
- RoPE-property。
- gated PE。

目的：

- 回答“你的新方法适合什么模型”。

### C5：No heavy model fallback

如果本机跑不动：

- 保留 sklearn/lightweight 结果。
- 写明 tiny attention 为待补实验。
- 论文草稿中将深度模型设为 future work 或 external validation requirement。

## D. 评价指标

必须包括：

- accuracy。
- macro-F1。
- per-class F1。
- mean ± std across seeds。
- feature dimension。
- observed vocabulary size。
- sparsity。
- perturbation distance。
- RC consistency distance / KL。
- runtime。
- memory。

若做 OOD：

- AUROC。
- abstention rate。
- coverage-precision-recall。

## E. 图表需求

### Figure 1

方法框架图：从 read 到四类表示：composition、token、raw-base、position/base prior。

### Figure 2

k 值与读长的信息容量：theoretical vocab、observed vocab、sparsity、nnz/read。

### Figure 3

controlled toy benchmark：各表示在 composition/order/position/noise 任务上的表现。

### Figure 4

proposed encoding ablation：spaced-kmer phase、codon-frame、RoPE-property、joint residual。

### Figure 5

small genome-slice / mNGS-like benchmark。

### Figure 6

model suitability map：representation × model。

## F. 当前电脑可完成程度

可完成：

- toy/exact-composition benchmark。
- genome-slice 小数据。
- sklearn baselines。
- shallow CNN 小模型。
- tiny attention 小模型。

可能吃力：

- 大规模 mNGS benchmark。
- 完整 Transformer pretraining。
- Kraken2 大库比对。

## G. 最小可投稿版本

若要形成最小投稿版本，至少补完：

1. exact composition/order benchmark。
2. small genome-slice benchmark。
3. ablation for top 3 proposed encodings。
4. shallow CNN / embedding-CNN / tiny attention 三个模型对照。
5. mean ± std across seeds。
6. final manuscript with figures and tables。
