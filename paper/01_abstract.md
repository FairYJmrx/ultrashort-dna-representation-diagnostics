# 中文骨架

1. 在 `controlled short-read (69-150 bp) mNGS-motivated settings` 下，问题不是先问分类器能不能分对，而是先问表征层在分类前还保留了哪些信息。
2. 现有 `accuracy-led` 评价容易把表征层和分类层混在一起，因此看不到信息是在何处丢失的。
3. 本文提出 `representation-diagnostics framework`，把短读段表征拆成 `identity`、`biochemical stability`、`positional readability` 和 `local mutation sensitivity` 四个维度来检查。
4. `CK4P-MSP` 是主方法，目标是在低维下保留稳定、可解释、可读取的辅助信息。
5. `full-position matrices` 用作诊断上界，`CSP` 用作边界对照。
6. 结尾只给出有边界的架构结论：数据库匹配负责 read identity，CK4P-MSP 提供可分解的 composition/property audit coordinates，不让单一表征承担全部任务。

# English draft

Short-read metagenomic next-generation sequencing (mNGS) pipelines often process trimmed, ambiguous or locally perturbed reads. Useful evidence can be compressed before a classifier or database lookup is applied, so downstream accuracy alone does not reveal which sequence attributes were retained in the representation layer. Here, we present a representation-diagnostics framework for controlled 69-150 bp short-read settings. The framework separates canonical local k-mer composition, global biochemical summaries and coarse positional property pooling, and evaluates their stability, compactness and local-change readability under paired perturbations. CK4P-MSP combines a reverse-complement canonical 4-mer block (K), a global property block (P) and multi-scale property pooling (MSP) in a 222-dimensional block-normalized representation. A seven-group matched ablation revealed metric-specific roles. Property-only summaries had the lowest numerical drift but weakened nearest-clean retrieval; conditional contrasts assigned P primarily to global stability, MSP to grouped local-change readability and K to composition-linked retrieval. CK4P-MSP provided the most balanced block-decomposable profile, with mean paired cosine 0.989, mean drift 0.129 and grouped local-versus-noise macro-F1 of 0.979. Full-position encodings remained higher-dimensional upper bounds for fine positional information, and compressed high-k vector controls were less stable at the same 222-feature budget. These results show that compact biochemical and coarse positional summaries can provide interpretable representation-level audit coordinates alongside, rather than in place of, database-linked exact matching and alignment.
