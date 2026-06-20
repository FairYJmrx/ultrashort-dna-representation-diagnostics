# 08 轻量人工数据集与污染/扰动设计

本文件把当前阶段的数据需求固定下来：我们优先使用人工构建的轻量 DNA 短序列数据集，而不是大规模模拟测序。目标是验证不同 DNA 信息表达方案的性质，而不是追求真实临床准确率。

## 一、用户意图拆解

当前实验意图包含四个核心变量：

1. 人工构建可控短序列数据集。
2. 加入污染、突变、N、trim 等扰动集合。
3. 比较不同 read length 下信息方案的变化。
4. k-mer 相关方案不预设固定 k，而是根据表达方式、读长和先验假设共同评估。

因此，实验对象不是“训练一个高准确率分类器”，而是：

```text
人工可控 DNA reads
  -> 多种信息表达方案
  -> 多种扰动/污染条件
  -> 多种读长
  -> 信息保留、鲁棒性、可分性、轻量分类参考
```

## 二、轻量数据规模

### D0：最小 smoke 数据

- 物种数：3。
- 每个物种：30-40 条 reads。
- 总数：约 100 条。
- 读长：默认 75bp，可附带 69bp。
- 用途：快速验证编码、指标、消融和脚本。

### D1：稳定轻量数据

- 物种数：3-5。
- 每个物种：100 条 reads。
- 总数：300-500 条。
- 读长：多读长版本。
- 用途：更稳定地比较特征方案。

### D2：困难轻量数据

- 物种数：5-8。
- 每个物种：100-200 条 reads。
- 总数：500-1600 条。
- 用途：加入近缘、污染、unknown、host-like 背景后的小型压力测试。

第一轮建议从 D0 开始，随后扩展到 D1。

## 三、人工物种设计

不需要真实 genome。先构造若干条人工 genome-like template，每条 2,000-10,000 bp，然后从中切 read。

### S1：GC-rich species

目的：

- 测试 composition 是否能区分 GC 偏好。

设计：

- GC 含量约 65%-70%。
- 含少量重复 motif。

### S2：AT-rich species

目的：

- 与 S1 形成 composition 级别强差异。

设计：

- AT 含量约 65%-70%。

### S3：near-SNP species

目的：

- 模拟与 S1 近缘，仅有少量 SNP 或局部 motif 差异。

设计：

- 从 S1 template 复制。
- 每 100-200 bp 注入 1 个 SNP。
- 保持总体 GC 含量接近 S1。

### S4：same-composition different-order species

目的：

- 专门测试顺序/位置表示是否优于 count-only。

设计：

- 使用与 S1/S3 接近的 k-mer 或 base composition。
- 通过 block shuffle、motif 重排、局部倒置改变顺序。

### S5：motif-position species

目的：

- 专门测试 position-base joint encoding、gated PE、RoPE-like 是否捕捉位置。

设计：

- 同一个 motif 出现在不同位置，例如 read 前端、中部、末端。
- composition 尽量保持相似。

### S6：host-like / contaminant species

目的：

- 作为污染或背景集合，不一定参与目标分类。

设计：

- 构造人源样式背景：较均衡 GC，低复杂度片段，重复区域。
- 或从 clean species 中生成非目标 reads。

## 四、污染与扰动类型

每种污染/扰动都应该保留原始 clean read id，方便比较扰动前后表示距离和预测变化。

### C0：clean

- 无突变，无 N，无 trim。
- 用作上限和 sanity check。

### C1：substitution

模拟 Illumina 主错误类型。

建议错误率：

- 0.5%。
- 1%。
- 2%。
- 5% stress test。

记录：

- mutation_count。
- mutation_positions。

### C2：terminal substitution gradient

模拟末端质量下降。

设计：

- read 后 20bp 错误率高于前段。
- 例如前 55bp substitution 0.5%，后 20bp substitution 3%。

用途：

- 测试 position-aware、trim、mask 是否受末端噪声影响。

### C3：N masking

模拟无法判定碱基。

建议比例：

- 1%、3%、5%、10%。

策略：

- 随机 N。
- 末端 N cluster。
- 中间短 N run。

### C4：trim / QC 后变长

模拟质控后读长变短。

目标读长：

- 69bp。
- 60bp。
- 50bp stress test。

策略：

- right trim。
- left trim。
- both-end trim。
- random crop。

### C5：insertion / deletion

虽然 Illumina 主要是 substitution，但 indel 可作为 stress test。

建议：

- 0.1%-0.5%。
- 单独作为 C5，不混入第一批主实验。

### C6：reverse-complement

用于测试双链一致性。

策略：

- 对 clean read 生成 RC 版本。
- 标签保持不变。

指标：

- 表示距离。
- 预测概率 KL。
- RC invariance error。

### C7：low-complexity contamination

模拟低复杂度片段。

例子：

- poly-A/T。
- ATATAT repeat。
- simple tandem repeat。

用途：

- 测试频域、熵、低复杂度特征。

### C8：adapter-like contamination

模拟接头或固定 motif 污染。

策略：

- 在 read 头部或尾部拼接固定 8-20bp motif。
- 或替换末端若干 bp。

用途：

- 测试 position-aware、FFT、quality filtering。

### C9：host/background mixture

模拟临床背景。

策略：

- 在数据集中加入 host-like reads，作为 background 或 non-target。
- target:background 比例：1:1、1:3、1:9。

第一阶段不必做复杂 abundance，只需在 read-level 观察误判和距离。

### C10：unknown / OOD species

模拟未见物种。

策略：

- 构造 S7 unknown species。
- 训练/fit 阶段不出现。
- 测试时要求拒识或回退到较高层级。

## 五、读长设计

我们确实需要比较 75bp、69bp，也建议加入更长 reads 看信息随长度变化。

### 推荐第一轮读长

```text
L = [69, 75, 100, 125, 150, 200]
```

理由：

- 69：质控后可能读长。
- 75：当前真实核心场景。
- 100/125：短读长过渡点。
- 150：常见 Illumina short read / DeepMicrobes 与 MetaTransformer 更接近。
- 200：观察信息增长，但不拉到太大。

### 更精细但仍轻量的读长阶梯

若需要观察更连续变化，可用：

```text
L = [50, 60, 69, 75, 90, 100, 125, 150, 175, 200]
```

第一轮不建议全部跑复杂模型；可先只跑非训练指标和轻量分类器。

## 六、k 值选择原则

k 不固定为 3，也不固定为 7 或 12。k 必须绑定表达方案、读长和信息假设。

### 1. vector composition route

建议扫描：

```text
k = [2, 3, 4, 5, 6, 7, 8, 10, 12]
```

关注：

- 维度 `4^k`。
- 每条 read 的 token 数 `L-k+1`。
- 非零比例。
- 错误扰动比例。
- 分类/距离可分性。

### 2. token sequence route

建议扫描：

```text
k = [3, 4, 5, 7, 9, 12, 13]
```

注意：

- 小 k 可与“DNA 语言”或三碱基先验相关，但不是必须。
- 大 k 更接近 DeepMicrobes/MetaTransformer，但需要 embedding/hash/canonical。
- 如果只是 token id 直接卷积，必须做 token-id permutation 审计。

### 3. biological-prior route

不强制 k=3。

可测试：

- k=3：三碱基周期/密码子式先验的最小验证。
- k=6/9：多个三碱基单元组合。
- k=4/5/7：与传统 composition 强 baseline 对照。

重点是比较：

```text
是否注入先验 > k 是否等于 3
```

### 4. position-base route

k 可以是：

- base-level，无显式 k。
- k=3/5/7 token-level。
- motif length 自定义。

先用 motif-position toy task 验证位置编码，再扩展到真实 read-like 数据。

## 七、指标优先级

### 不需要训练的核心指标

第一优先级：

- feature dimension。
- non-zero feature count。
- sparsity。
- collision / duplicate profile rate。
- intra-class vs inter-class distance。
- clean vs perturbed feature distance。
- substitution perturbation ratio。
- RC distance。
- entropy / spectral entropy。

### 轻量模型指标

第二优先级：

- Logistic Regression accuracy/F1。
- Linear SVM accuracy/F1。
- kNN / nearest centroid。
- train/test 多 seed 均值和方差。

这些指标只是辅助判断可分性，不作为真实临床准确率。

### 小神经网络指标

仅在必要时使用：

- Embedding-CNN。
- tiny GRU。
- tiny Transformer。
- joint encoding + small classifier。

用途：

- 验证某些表达方式必须通过可学习模型承接时是否可利用。

## 八、第一轮推荐数据组合

为了实验次数少但覆盖关键问题，第一轮使用：

```text
species = [S1_GC_rich, S2_AT_rich, S3_near_SNP]
reads_per_species = 40
lengths = [69, 75, 100, 150, 200]
conditions = [C0_clean, C1_substitution_1%, C3_N_3%, C4_trim_to_69, C6_reverse_complement]
```

约：

```text
3 species * 40 reads * 5 lengths * 5 conditions = 3000 reads
```

这仍然很轻量，但足以观察：

- 读长变化。
- k 值变化。
- clean/noisy 差异。
- RC 一致性。
- 近缘物种难度。

如果要更小：

```text
3 species * 20 reads * 4 lengths * 4 conditions = 960 reads
```

也可以完成第一轮验证。

## 九、第二轮扩展数据组合

加入：

- S4 same-composition different-order。
- S5 motif-position。
- S6 host-like contaminant。
- C2 terminal substitution gradient。
- C7 low-complexity。
- C8 adapter-like contamination。
- C10 unknown / OOD species。

用途：

- 专门服务 sequence、position-aware、frequency/GSP、层级拒识实验。

## 十、结论

当前阶段数据应轻量、可控、可解释。准确率不是主要目标，特征行为才是主要目标。只有当某个表达方案需要可学习 embedding、position encoding 或 prototype 时，才使用小型训练模型。
