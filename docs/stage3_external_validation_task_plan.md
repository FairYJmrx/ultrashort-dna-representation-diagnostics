# Stage 3 外部验证与模拟合理性补强任务文档

生成日期：2026-06-22  
目标稿件：`manuscript/stage2_manuscript_v2.md` 与后续 v3 稿  
核心定位：本阶段不是把论文改成端到端临床分类器论文，而是补强“受控表征诊断”论文的可信度、外部性和数据设计逻辑。

## 1. 本阶段的中心论证

本研究采用模拟或受控数据，不是为了回避真实临床 mNGS 数据，而是因为本文研究的问题位于表征层：不同 DNA read 表征在短读长、扰动和链方向不确定条件下保留了哪些信息。这个问题需要 read-level truth、可控读长、可控扰动和可重复比较。

真实临床 mNGS 数据通常更接近最终应用，但它常见的问题是只有样本级诊断标签，缺少每条 read 的真实物种来源、真实错误来源、真实突变状态和真实扰动强度。因此真实临床数据更适合后续端到端 pipeline 验证，不适合作为本文机制拆解的唯一主证据。

本阶段要把数据体系解释为三层证据：

| 数据层 | 功能 | 解决的审稿问题 | 不承担的主张 |
|---|---|---|---|
| WGS-derived controlled reads | 机制拆解和主网格实验 | 为什么能知道 read-level truth、读长、扰动和物种来源 | 不代表完整临床 mNGS 样本复杂性 |
| ART Illumina simulated reads | 真实测序错误谱验证 | CSP 稳定性是否只是人工 substitution/N/trim 的特例 | 不声称覆盖所有平台、文库和临床背景 |
| CAMI low-complexity subset | 外部 benchmark readout probe | 结论是否能在领域公认 benchmark 上保持方向一致 | 不做 Kraken2/Centrifuge/Kaiju SOTA 对标 |

## 2. 论文结构修改任务

### 2.1 Introduction / Methods 开头新增写作主线

新增小节或段落标题建议：

```text
Rationale for controlled simulated reads
```

必须表达五点：

1. 本文研究的是 representation-level information-preservation diagnostics，而不是 end-to-end clinical classifier。
2. 真实临床 mNGS 往往缺少 read-level truth，因此难以用于表征机制拆解。
3. WGS-derived reads 提供可控物种来源、读长、扰动和 clean-perturbed pairing。
4. ART Illumina 使用领域通用测序错误谱，验证结论不是人工扰动特例。
5. CAMI low-complexity 作为领域公认 benchmark，用于外部轻量 readout probe。

写作语气要求：主动说明实验设计为何适合研究问题，而不是把模拟数据写成“不得已的替代品”。

### 2.2 Methods 中明确三类数据的功能

建议 Methods 拆成：

1. `Controlled WGS-derived reads`
2. `ART Illumina error-profile validation`
3. `CAMI low-complexity external probe`
4. `Representation baselines and compact controls`
5. `Metrics and readout probes`

Methods 中需要写清楚：

- WGS-derived reads 的 accession/manifest、物种、读长、采样数、扰动类型、随机种子。
- ART 输入 FASTA、profile、read length、coverage 或 reads-per-genome、输出 FASTQ 到 CSV 的转换方式。
- CAMI 数据版本、low-complexity 样本、截断到 69/75/100/125/150 bp 的规则、标签来源。
- MinHash sketch 的 k、sketch size、hash seed、canonicalization 策略。
- EIIP baseline 是纯 EIIP 数值向量或 EIIP summary，不与 CSP 中其他属性混合。

### 2.3 Results 中新增三段，但未完成前只能写 placeholder

新增结果段落：

1. `ART Illumina profiles reproduced the stability advantage under platform-like error distributions`
2. `Compact classical baselines did not explain away the CSP advantage`
3. `The CAMI low-complexity probe tested external signal readability without claiming clinical classification`

在结果未跑完前，稿件中只能写：

```text
[Planned validation: ART Illumina error-profile results will be inserted here after the stage-3 run.]
```

禁止把计划写成已完成结果。

### 2.4 Limitations 补充边界

Limitations 必须明确：

- 模拟数据不能替代真实临床 mNGS 的宿主背景、污染、丰度结构、数据库缺失、样本级不确定性。
- ART 能补真实测序错误谱，但仍不是完整 wet-lab 和临床流程。
- CAMI 能补外部 benchmark 可信度，但 CAMI 子集 probe 不是端到端临床诊断性能。
- 本文不声称 CSP-alone species identification、ARG allele calling、resistance SNP calling。

### 2.5 Future Work 接入后续大项目

Future work 要明确：

后续将基于“身份证据 + 稳定性辅助证据”的分层架构，开发面向真实宏基因组样本的端到端分类流程。其中 canonical k-mer、alignment 或数据库索引提供高分辨率身份判定，CSP-like auxiliary block 提供扰动稳定、质量审计和低质量 reads 的辅助置信信息。

## 3. 实验 A：ART Illumina 错误谱验证

### 3.1 目的

验证 CSP 在真实测序错误谱下的稳定性优势，不只是人工均匀 substitution、N mask、trim 和 local mismatch 下的特例。

### 3.2 输入

- 现有 21 株 WGS 参考基因组 manifest。
- 读长：69、75、100、125、150 bp。
- 可选 PE150 proxy：先不作为 ART 主实验，避免 insert-size 和 paired-end 建模引入额外变量。
- ART Illumina profile：优先使用 ART 内置 HiSeq profile；若版本明确支持 NovaSeq，再增加 NovaSeq。

### 3.3 输出

目录建议：

```text
data/stage3/art_illumina/
results/stage3/art_illumina/
```

核心文件：

```text
art_reads_manifest.csv
art_clean_or_reference_reads.csv
art_error_reads.csv
art_stability_metrics.csv
art_summary.md
```

### 3.4 实验设计

1. 从每个 WGS 参考中抽取相同位置的 clean reference reads，作为 paired clean truth。
2. 使用 ART Illumina 对同一区域或同一参考生成测序错误 reads。
3. 将 ART FASTQ 转为统一 CSV schema：

```text
read_id, clean_read_id, sequence, quality, label, genus, species_id,
condition, source_rule, source_length, length, template_start, mutation_profile, notes
```

4. 对 clean/error paired reads 运行同一组表征：

```text
ckmer5_count_l2
ckmer7_count_l2
cspaced_count_l2
cspaced_property_l2
hybrid_ckmer5_csp
hybrid_ckmer7_csp
minhash_k5_s128
eiip_l2
eiip_summary_l2
```

5. 指标：

- paired cosine mean / p05
- L2 drift mean / p95
- nearest-clean retrieval top1
- feature dimension
- density
- quality-score 分层后稳定性，如果 FASTQ quality 可用

### 3.5 结果解释规则

- 如果 CSP 仍在 paired stability 上领先：说明主结论能泛化到领域通用测序错误谱。
- 如果 hybrid 稳定性低于 CSP 但 readout 更好：说明身份信息与稳定性证据确实有分工。
- 如果 ART 结果削弱 CSP：保留并解释，可能说明人工 N/local mismatch 放大了 CSP 优势；论文结论需要收窄。

### 3.6 风险和处理

| 风险 | 处理 |
|---|---|
| 本地未安装 ART | 先写 wrapper 和检查脚本；需要时在 conda 环境安装或服务器运行 |
| ART 无 NovaSeq profile | 以 HiSeq profile 为主，论文写 Illumina-like / ART profile，不强写 NovaSeq |
| 无法准确 paired clean/error reads | 改为同参考、同位置窗口近似配对，或只做 distributional stability |
| 数据量过大 | 每物种每长度先抽 100-300 reads，保持本地可复现 |

## 4. 实验 B：MinHash sketch + EIIP 基线

### 4.1 目的

证明 CSP 的优势不是“只是因为维度低”或“只是因为用了生化数值”，而是在同类紧凑/经典表征下仍有可解释的优势区间。

### 4.2 新增表征

| 表征 | 定义 | 对照意义 |
|---|---|---|
| `minhash_k5_s128` | canonical 5-mer 的 128 维 MinHash sketch | 经典紧凑 alignment-free sketch |
| `minhash_k7_s128` | canonical 7-mer 的 128 维 MinHash sketch | 更高分辨率 sketch |
| `eiip_l2` | 每位置 EIIP 标量，padding/truncation 后 L2 | 纯 DNA 数值信号 |
| `eiip_summary_l2` | EIIP mean/std/min/max/entropy-like summary | 低维数值摘要 |

### 4.3 运行范围

先在现有 WGS-derived grid 上跑，随后自然接入 ART 和 CAMI。

默认表征列表：

```text
ckmer5_count_l2,ckmer7_count_l2,cspaced_count_l2,cspaced_property_l2,
hybrid_ckmer5_csp,minhash_k5_s128,minhash_k7_s128,eiip_l2,eiip_summary_l2
```

### 4.4 指标

同 stage2 representation grid：

- paired cosine
- L2 drift
- nearest-clean retrieval
- feature dimension
- density
- readout macro-F1 / accuracy

### 4.5 结果解释规则

- MinHash 如果在 retrieval 上强：说明 sketch identity evidence 有价值，不能简单写 CSP 全面更强。
- EIIP 如果很稳但 readout 弱：说明纯数值稳定不等于身份信息充足。
- CSP 如果在稳定性和可读性之间更平衡：支撑“spaced identity + property summary”的设计合理性。

## 5. 实验 C：CAMI low-complexity 子集 probe

### 5.1 目的

在领域公认 metagenomic benchmark 上进行外部轻量 readout probe，验证 CSP/hybrid 的价值不是只来自本地 21 WGS panel。

### 5.2 输入

- CAMI low-complexity simulated community reads。
- gold standard taxonomy / binning / profiling label 中能映射到 read 或 contig 的标签。
- 本地只保留小子集，避免数据体积过大。

### 5.3 数据处理

1. 下载或引用 CAMI low-complexity 数据。
2. 抽样 reads。
3. 截断或裁剪到：

```text
69, 75, 100, 125, 150 bp
```

4. 标签层级优先级：

```text
species > genus > target/background
```

如果 species label 太稀疏，则退回 genus 或 target/background probe。

### 5.4 任务

| Probe | 标签 | 目的 |
|---|---|---|
| target/background | 指定目标属或物种 vs 其他 | 测试轻量实际可读性 |
| genus-level probe | genus label | 外部分类可读性 |
| noise degradation probe | clean-like vs quality-filtered/shortened | 测试性能衰减 |

### 5.5 表征与模型

表征：

```text
ckmer5_count_l2
ckmer7_count_l2
cspaced_count_l2
cspaced_property_l2
hybrid_ckmer5_csp
minhash_k5_s128
eiip_l2
eiip_summary_l2
```

模型：

```text
nearest_centroid
logistic
mlp
```

### 5.6 结果解释规则

- CAMI 只作为外部 readout probe，不做主流工具 SOTA 对标。
- 如果 hybrid 优于 pure k-mer 或 pure CSP：支撑分层证据架构。
- 如果 canonical k-mer 仍最强：说明外部身份识别任务仍由高分辨率 identity evidence 主导，CSP 保持辅助定位。
- 如果 CSP 在 noisy/short subset 中性能衰减更小：这是最理想结果。

### 5.7 风险和处理

| 风险 | 处理 |
|---|---|
| CAMI 数据太大 | 只下载 low-complexity 小样本或在服务器处理 |
| read-level label 不易解析 | 使用 CAMI gold standard 映射；不行则改为 sample-level target/background |
| 标签分布不均 | balanced sampling，每类设置上限 |
| 本地运行慢 | 先 nearest_centroid/logistic，MLP 可后置 |

## 6. 脚本任务清单

### 6.1 立即可做

1. 扩展 `src/stage2_features.py`：
   - 支持 MinHash sketch；
   - 支持 EIIP summary baseline；
   - 保持 `build_feature_matrix` 统一入口。
2. 新增 `scripts/run_stage3_compact_baselines.py`：
   - 在现有 WGS-derived grid 上运行 MinHash/EIIP/CSP/k-mer 对照。
3. 新增 `scripts/run_stage3_art_validation.py`：
   - 检查 ART 是否安装；
   - 生成 ART 命令 manifest；
   - 如果 FASTQ 已存在，转换并运行 stability metrics。
4. 新增 `scripts/run_stage3_cami_probe.py`：
   - 支持从 CAMI FASTQ + label map 输入；
   - 输出 readout probe 结果。

### 6.2 需要数据或工具后执行

1. 安装 ART Illumina 或在服务器配置。
2. 下载 CAMI low-complexity 子集。
3. 跑完整 ART grid。
4. 跑 CAMI readout probe。
5. 生成结果图表并更新 publication assets。

## 7. 论文更新规则

### 7.1 现在就可以写入

- Rationale for controlled simulated reads。
- 三类数据的功能说明。
- ART/CAMI/MinHash/EIIP 的 planned validation 位置。
- Limitation 与 Future work 边界。
- ART、CAMI、Mash、EIIP 等规范引用。

### 7.2 结果跑完后才能写入

- ART 中 CSP 是否仍然最稳。
- MinHash/EIIP 与 CSP 的定量差异。
- CAMI readout macro-F1 / accuracy / degradation slope。
- 任何“显著提升”“优于”“降低衰减”的定量表述。

## 8. 完成标准

本阶段完成需要满足：

1. stage-3 任务文档完成。
2. 稿件新增模拟合理性主线。
3. 脚本支持 MinHash/EIIP 新基线。
4. ART 和 CAMI 脚本即使没有数据，也能给出明确输入 schema 与待运行命令。
5. 已完成结果只写已完成结果，未完成结果保留 placeholder。
6. Limitations/Future work 明确真实临床 mNGS pipeline 是后续大项目，不把本文包装成临床分类器。

