# 02 代码脚本规划

## 设计原则

1. 先做小而可验证的脚本，再扩展到大数据。
2. 表示法与模型解耦，避免把模型差异误认为表示法差异。
3. 每个脚本都能通过配置文件控制输入、输出、随机种子和实验编号。
4. 每次运行写入 `results/runs/<run_id>/`，保留配置、指标、日志和图表。

## 第一批脚本

第一批脚本服务 E01/E02/E03/E05/E06/E07/E10/E11，不急于实现所有深度模型。优先把特征、消融、指标和日志跑通。

### 1. toy 数据构造

路径：

```text
scripts/make_toy_reads.py
```

功能：

- 构造 75bp reads。
- 支持多读长：69、75、100、125、150、200bp。
- 支持类别模式：GC-rich、AT-rich、near-SNP、same-composition-different-order、motif-position、host-like。
- 支持污染/扰动：substitution、terminal substitution、N masking、trim、indel stress、reverse-complement、low-complexity、adapter-like、host/background、unknown/OOD。
- 输出 FASTA/CSV 两种格式。

输出：

```text
data/toy_reads/toy_reads.csv
```

字段：

```text
read_id, sequence, label, species_id, condition, source_rule, length, clean_read_id, mutation_profile, notes
```

### 2. k-mer composition 特征

路径：

```text
src/kmer_composition.py
scripts/run_composition_baseline.py
```

功能：

- count k-mer。
- canonical reverse complement。
- relative frequency。
- TF-IDF。
- normalization。
- TruncatedSVD。

输出：

```text
results/runs/<run_id>/features.npz
results/runs/<run_id>/metrics.json
```

### 3. ordered token 特征

路径：

```text
src/kmer_token_sequence.py
scripts/run_token_baseline.py
```

功能：

- overlapping k-mer tokenization。
- token vocabulary。
- canonical token。
- padding/mask。
- shuffle 消融。

模型：

- mean embedding baseline。
- 1D CNN。
- GRU/BiLSTM。
- lightweight Transformer。

### 4. raw-base numerical encoding

路径：

```text
src/base_encoding.py
scripts/run_base_encoding_baseline.py
```

功能：

- one-hot / Voss。
- EIIP。
- tetrahedron。
- hydrogen-bond scalar。
- GC / purine / pyrimidine channels。
- N mask。
- optional FFT features。

### 5. position-aware encoding

路径：

```text
src/position_encoding.py
scripts/run_position_encoding_baseline.py
```

功能：

- sinusoidal PE。
- learned PE。
- attribute-gated PE。
- RoPE-like 2D real rotation。
- prior + learnable residual。

### 6. 统一评估

路径：

```text
src/evaluation.py
scripts/summarize_runs.py
```

功能：

- accuracy、macro-F1、per-class F1。
- confusion matrix。
- runtime、memory。
- feature sparsity。
- 消融对比表。

### 7. 失败诊断与下一轮建议

路径：

```text
scripts/review_run.py
```

功能：

- 读取 metrics、confusion matrix、配置。
- 自动生成失败模式摘要。
- 将下一轮候选方案写入 `results/ideas_backlog.md`。

## 配置文件

路径：

```text
configs/experiment_matrix.yaml
```

内容包括：

- 数据层级。
- k 值。
- 表示法。
- 模型。
- 消融项。
- 随机种子。
- 评价指标。

## 与 code-V3 的关系

可复用：

- `D:\AI-NGS\code-V3\data_pre\trans_kmer.py` 中的 k-mer count 逻辑。
- `D:\AI-NGS\code-V3\data_pre\trans_kmer_sequence.py` 和 `kmer_sequence.py` 中的 token sequence 思路。
- `D:\AI-NGS\code-V3\data_pre\dim_reduction.py` 中的降维流程。

不直接照搬：

- 大规模下载与模拟流程。
- 与现有目录强耦合的路径逻辑。
- 未经过 train-only fit 审查的 SVD/TF-IDF artifact。

## 推荐开发顺序

1. `make_toy_reads.py`：服务 E01/E05/E10/E12，并支持读长阶梯和污染/扰动条件。
2. `evaluation.py`：先统一所有指标和日志格式。
3. `kmer_composition.py`：服务 E01/E02/E03。
4. `run_composition_baseline.py`：跑 k sweep、TF-IDF、SVD。
5. `kmer_token_sequence.py`：服务 E05/E06/E07。
6. `run_token_audit.py`：token shuffle、position shuffle、token-id permutation、Embedding-CNN。
7. `base_encoding.py`：服务 E10/E11。
8. `run_base_signal_baseline.py`：one-hot/Voss/tetrahedron/EIIP/三相信号/FFT。
9. `position_encoding.py`：服务 E12/E13/E14。
10. `run_position_encoding_baseline.py`：joint encoding、gated PE、RoPE-like。
11. `summarize_runs.py`：跨实验单元汇总。
12. `review_run.py`：失败诊断与新方案 backlog。

这个顺序能保证每一步都有可验证的产物，不会在复杂模型里迷路。
