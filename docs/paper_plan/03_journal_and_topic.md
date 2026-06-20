# 03 论文主题与目标期刊建议

## 论文主题

推荐主题：

> Biologically informed representation learning for ultra-short metagenomic DNA reads.

更具体标题候选：

1. **Biologically informed position-phase encodings for ultra-short metagenomic read representation**
2. **Beyond k-mer counts: representation-centric benchmarking of ultra-short DNA reads for metagenomic classification**
3. **Spaced phase and frame-aware nucleotide encodings improve lightweight representation of 69-75 bp metagenomic reads**

## 论文核心问题

不是“我们提出一个新分类器”，而是：

> 69-75bp 超短 mNGS reads 中，哪些 DNA 信息表示能更好保留 composition、order、position、strand consistency 和 noise robustness？

## 方法贡献

### Contribution 1

建立面向超短 mNGS reads 的 representation-centric benchmark。

### Contribution 2

系统比较 k-mer composition、ordinary token embedding、raw-base numerical encoding 与 position/base prior encodings。

### Contribution 3

提出一组 biologically informed encodings：

- spaced-kmer phase。
- codon-frame property channels。
- RoPE-property / RoPE-onehot。
- joint phase prior + residual。
- RC-consistent pooling。

### Contribution 4

给出 representation-to-model suitability map，说明不同 DNA 表示适合 CNN、attention、linear classifier 还是 k-mer vector models。

## 与 mNGS 物种鉴定/耐药检测的关系

本论文可定位为上游信息学表征论文：

- mNGS species identification 是主要应用动机。
- ARG/耐药检测是未来扩展任务。
- 本文先证明短 read 信息表示的合理性，再进入真实物种/耐药检测模型。

不要把第一篇写成“完成临床 mNGS 物种鉴定系统”。那需要更多真实数据、数据库比对和临床验证。

## 目标期刊梯队

### 第一梯队：较高风险

#### Bioinformatics

适合点：

- 新算法/表示方法。
- 有可复现 benchmark。
- 有明确生信问题。

风险：

- 需要更强真实数据和方法创新。
- 只靠 toy benchmark 不够。

#### Briefings in Bioinformatics

适合点：

- 如果写成系统性方法学综述 + benchmark。

风险：

- 门槛高，通常需要更全面验证和更大影响力。

### 第二梯队：较现实

#### BMC Bioinformatics

适合点：

- 算法、软件、模型、benchmark、bioinformatics method 都适配。
- 对方法学和可复现性友好。

风险：

- 仍然需要真实或半真实 biological dataset。

#### Computers in Biology and Medicine

适合点：

- 计算方法在生物医学问题中的应用。
- 可接受 ML/representation + biomedical task。

风险：

- 需要更明显的 biomedical application validation。

### 第三梯队：备选

- PLOS ONE：更注重技术严谨和可复现，不一定强调高度创新。
- Scientific Reports：可作为保底，但如果目标是二区及以上，需要核查当年分区。
- Computational and Structural Biotechnology Journal：若补强生物学解释和开源工具，可考虑。

## 最推荐投稿路线

如果补完 genome-slice、ablation、小模型：

1. 首选：BMC Bioinformatics。
2. 次选：Computers in Biology and Medicine。
3. 冲刺：Bioinformatics。

如果只保留轻量 toy + 方法草稿：

- 暂不建议投稿二区。
- 可作为预印本/内部技术报告/会议 workshop 草稿。
