# 04 下一阶段执行计划

## 当前状态判断

信息学表征子项目已经完成轻量 proof-of-concept，但还不是可直接投稿的二区论文。

下一阶段目标：

> 把轻量 proof-of-concept 升级为可投稿的方法学论文证据链。

## 阶段 1：补强 controlled benchmark

### Task 1.1 exact composition-matched order-only 数据

目标：

- 构造完全或近似匹配 1-mer/2-mer/3-mer composition 的多类别 reads。
- 类别差异仅来自顺序、motif order、block inversion。

产物：

- `data/toy_reads/toy_exact_order.csv`
- 对比：k-mer count vs token transition vs RoPE-property vs spaced-kmer phase。

### Task 1.2 motif-position jitter 数据

目标：

- 同一 motif 出现在前/中/后。
- 加入 ±3bp jitter。
- 加 reverse-complement motif。

产物：

- `data/toy_reads/toy_motif_position_jitter.csv`

### Task 1.3 多 seed 重复

目标：

- 每个 controlled benchmark 跑 5 个 seed。
- 输出 mean ± std。

## 阶段 2：补强 proposed methods ablation

### Task 2.1 spaced-kmer phase 消融

对比：

- full spaced-kmer phase。
- no spaced pattern。
- no phase。
- no property。
- contiguous kmer property。

### Task 2.2 codon-frame channels 消融

对比：

- full frame channels。
- collapsed frame。
- frame only。
- property only。

### Task 2.3 RoPE-property 消融

对比：

- RoPE-property。
- property no rotation。
- sinusoidal PE。
- learned proxy PE。
- no PE。

### Task 2.4 RC consistency

指标：

- read vs RC(read) feature distance。
- prediction consistency。
- probability KL if classifier supports probability。

## 阶段 3：补强模型适配

### Task 3.1 shallow CNN

输入：

- one-hot。
- property channels。
- codon-frame channels。
- spaced-kmer phase channels。

目的：

- 回答 raw/base/channel 表示适合 CNN 的问题。

### Task 3.2 embedding-CNN

输入：

- ordinary k-mer token embedding。
- k=3/5/7/12。

目的：

- 正式对照普通 token embedding route。

### Task 3.3 tiny attention

对比：

- learned PE。
- sinusoidal PE。
- RoPE-property。
- gated PE。

目的：

- 回答“新方法是否适合 Transformer/attention”。

资源判断：

- 小模型可在本机 CPU 跑。
- 不做大规模 pretraining。

## 阶段 4：small genome-slice benchmark

### Task 4.1 选择小型真实 genome

候选：

- 5-10 个细菌 reference genomes。
- 优先同属近缘 + 远缘混合。

数据来源：

- 可复用 `code-V3` 已有数据。
- 或从已有小 fasta 构建。

### Task 4.2 生成 reads

读长：

- 69/75/100/150bp。

扰动：

- clean。
- substitution 1%。
- N 3%。
- trim。

### Task 4.3 对比方法

必须包括：

- k-mer count/TF-IDF。
- ordinary embedding proxy。
- one-hot/property。
- spaced-kmer phase。
- codon-frame。
- RoPE-property。

## 阶段 5：论文写作与图表

### Figure 1

Representation framework。

### Figure 2

k/read length information capacity。

### Figure 3

Controlled benchmark performance。

### Figure 4

Ablation of proposed methods。

### Figure 5

Small genome-slice benchmark。

### Figure 6

Representation-model suitability map。

## 投稿判断节点

### 可以投稿 BMC Bioinformatics / CBM 的最低条件

- controlled benchmark 完整。
- proposed method ablation 完整。
- small genome-slice benchmark 完整。
- 至少 shallow CNN 或 tiny attention 中一种模型验证完成。
- 结果跨 5 seeds 报告 mean ± std。

### 可以冲 Bioinformatics 的最低条件

- 以上全部完成。
- tiny attention / CNN 均完成。
- 真实或半真实 mNGS-like 数据更充分。
- 代码和数据可复现。

## 当前推荐

先补阶段 1-3。若结果仍强，再做阶段 4，并将 `manuscript/draft_manuscript.md` 扩展成投稿版。
