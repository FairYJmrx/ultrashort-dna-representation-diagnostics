# 05 轻量下游任务设计：替代完整物种鉴定

## 核心判断

论文不必一开始做完整 mNGS species identification。完整物种鉴定会同时受到模型容量、训练数据规模、数据库覆盖、近缘物种、宿主背景和分类头设计影响，容易掩盖“信息表征是否更好”这个核心问题。

更合理的策略是：

> 使用多个轻量、可复现、针对性强的下游任务，证明新表示在短 read 的关键信息能力上优于普通 k-mer count 或普通 token embedding。

这些任务仍然是下游任务，能回应审稿人“你的表征有什么实际用处”的问题，但比完整物种鉴定更可控。

## 推荐任务总览

| 任务编号 | 任务名 | 目标信息能力 | 是否需要训练 | 推荐指标 |
|---|---|---|---|---|
| T1 | clean-perturbed paired retrieval | 扰动鲁棒性 | 否 | top-1/top-5 retrieval, mean rank |
| T2 | reverse-complement consistency | 链方向稳定性 | 否 | RC distance, nearest-RC hit rate |
| T3 | same-composition order discrimination | 顺序信息 | 轻量分类 | macro-F1, shuffle drop |
| T4 | motif-position localization/classification | 位置信息 | 轻量分类 | macro-F1, position jitter robustness |
| T5 | low-complexity / adapter contamination detection | 污染/质控 | 轻量分类 | AUROC, F1 |
| T6 | read-length transfer | 读长泛化 | 轻量分类/检索 | train L1 test L2 F1 |
| T7 | near-SNP strain-like discrimination | 近缘差异 | 轻量分类 | macro-F1, confusion |
| T8 | unknown/OOD rejection | 拒识能力 | 轻量分类 | AUROC, abstention rate |

## T1：clean-perturbed paired retrieval

### 问题

同一条 read 加 substitution、N、trim 后，表示空间中是否仍然靠近原始 clean read？

### 为什么适合本文

它直接测试短读长表示的噪声鲁棒性，不需要完整分类模型。

### 数据

- clean read。
- substitution 1/2/5%。
- N masking。
- trim。
- indel stress。

### 方法

对每个 perturbed read，在 clean read 表示库中检索最近邻。

### 指标

- top-1 paired retrieval accuracy。
- top-5 paired retrieval accuracy。
- mean reciprocal rank。
- clean-perturbed distance。

### 预期

spaced-kmer phase、property channels、RC-aware encodings 应比普通连续 high-k 表示更稳。

## T2：reverse-complement consistency

### 问题

read 和 reverse-complement read 是否具有一致表示或一致预测？

### 为什么适合本文

mNGS read 的分类标签应基本与链方向无关。这个任务能体现 canonical、RC pooling 和 RoPE/phase 设计的必要性。

### 指标

- feature distance between read and RC(read)。
- nearest-RC hit rate。
- prediction consistency。

### 预期

RC pooled encodings、canonical k-mer 应更强。

## T3：same-composition order discrimination

### 问题

当不同类别具有相同或近似相同 composition 时，表示是否还能区分顺序结构？

### 为什么适合本文

这是 k-mer count 的弱点，也是 position/order encoding 的主战场。

### 指标

- macro-F1。
- token shuffle drop。
- count baseline gap。

### 预期

RoPE-property、spaced-kmer phase、codon-frame channels、transition features 应优于 count-only。

## T4：motif-position localization/classification

### 问题

相同 motif 出现在 read 前/中/后，表示是否能区分？

### 为什么适合本文

它直接验证 position encoding。

### 指标

- macro-F1。
- jitter robustness。
- no-position ablation drop。

### 预期

RoPE-property、gated PE、joint phase residual 应更强。

## T5：low-complexity / adapter contamination detection

### 问题

表示能否识别低复杂度片段、adapter-like 片段、N cluster？

### 为什么适合本文

这是 mNGS 质控相关的真实轻量任务，比 species identification 简单，但有实际意义。

### 指标

- AUROC。
- F1。
- precision/recall。

### 预期

entropy-gated PE、FFT/三相信号、property channels 有优势。

## T6：read-length transfer

### 问题

在 75bp 训练的轻量分类/检索规则，能否转移到 69bp 或 100/150bp？

### 为什么适合本文

我们关心 69/75bp 与更长 reads 的信息差异。

### 指标

- train 75 test 69。
- train 75 test 100/150。
- performance vs length curve。

### 预期

base-level and position-aware encodings 可能比 fixed k-mer vocabulary 更容易跨长度。

## T7：near-SNP strain-like discrimination

### 问题

当两个类别只有少量 SNP 差异时，表示是否能捕捉微小差异？

### 为什么适合本文

它接近近缘物种/菌株差异，但比真实物种鉴定更可控。

### 指标

- macro-F1。
- confusion matrix。
- perturbation sensitivity。

### 预期

spaced-kmer phase 在高噪声下可能优于 continuous k-mer；raw one-hot/CNN 也可能强。

## T8：unknown/OOD rejection

### 问题

测试时出现未见类，表示空间能否让它远离已知类？

### 为什么适合本文

临床 mNGS 中强行 species 分类会过度自信。拒识比闭集 accuracy 更有价值。

### 指标

- max similarity threshold AUROC。
- abstention rate。
- known coverage vs precision。

## 是否必须训练模型？

不必须训练大模型，但应至少有轻量模型或检索任务。

最小可接受组合：

1. T1 paired retrieval：无训练。
2. T2 RC consistency：无训练。
3. T3/T4 轻量分类：kNN/linear/SVM。
4. T5 contamination detection：logistic/linear。

如果要更强：

- 加 shallow CNN。
- 加 tiny attention。

## 对论文的意义

这些任务能让论文主题更清楚：

> 我们不是声称已经解决 mNGS 物种鉴定，而是证明新 DNA 表示在超短 read 的关键下游能力上更强，包括噪声鲁棒、顺序识别、位置识别、链一致性、污染识别和读长泛化。

这比直接做一个不成熟的 species classifier 更符合科研逻辑。
