# 03 突发情况处理与迭代机制

## 一、常见突发情况处理

### 1. 文献或参考代码编码异常

现象：

- 终端读取 markdown 出现乱码。

处理：

- 优先用编辑器或 Python 明确编码读取。
- 不在乱码基础上复制长文本。
- 只抽取稳定识别的结构信息和文件路径。
- 必要时转换为 UTF-8 备份。

### 2. 找不到用户提到的数据目录

现象：

- 用户说 `V3/datapre`，实际目录是 `code-V3/data_pre`。

处理：

- 先全局搜索 `datapre`、`data_pre`、`preprocess`。
- 记录实际路径。
- 规划中使用“参考路径候选”，不写死不存在路径。

### 3. toy 数据结果过高

现象：

- 所有模型接近满分。

解释：

- toy 数据可能只验证实现，不足以证明方案优劣。

处理：

- 增加近缘类别。
- 增加同 composition 不同顺序类别。
- 增加 substitution、N、trim、host-like background。
- 加入 label permutation sanity check。

### 4. toy 数据结果过低

现象：

- 所有模型接近随机。

处理顺序：

1. 检查标签是否正确。
2. 检查 train/test 是否过小或类别不平衡。
3. 检查特征是否全零或维度错误。
4. 用最简单的规则模型验证数据是否有可分信号。
5. 暂停复杂模型，回到表征审查。

### 5. 复杂模型不如简单模型

解释候选：

- 数据规模不足。
- 任务主要由 composition 决定。
- 模型容量过大导致过拟合。
- token 顺序没有额外信息。
- 训练超参数不稳定。

处理：

- 使用同一 split 和同一指标重跑。
- 增加 token shuffle 消融。
- 增加学习曲线。
- 增加模型容量扫描。
- 用更小模型作为首选对照。

### 6. position-aware 编码没有提升

解释候选：

- 数据任务不依赖位置。
- 位置编码实现无效。
- 位置信号被 pooling 抹掉。
- 模型没有足够容量利用位置。
- 75bp read 中绝对位置不稳定，应该测试相对位置或 motif-local position。

处理：

- 构造 motif-position toy task。
- 检查同一 motif 换位置后的 embedding 距离。
- 比较 no PE、learned PE、sinusoidal PE。
- 增加 attention/pooling 可视化。

### 7. SVD/TF-IDF 数据泄漏

风险：

- 如果 TF-IDF 或 SVD 在全量数据 fit，会泄漏 valid/test 分布。

处理：

- split 先于 fit。
- TF-IDF、SVD、normalizer 都只在 train fit。
- valid/test 只能 transform。
- 在 run config 中记录 fit scope。

### 8. 小数据指标波动大

处理：

- 固定随机种子。
- 重复 5 到 10 个 seeds。
- 报告均值和标准差。
- 不把单次 run 当结论。

## 二、结果不理想时如何持续提出新方案

### 核心机制：失败模式驱动，而不是随机试错

每次结果不理想时，必须先把失败归入下列至少一类：

| 失败类型 | 例子 | 下一步 |
|---|---|---|
| 表示信息不足 | count-only 区分不了顺序 | 转向 ordered token 或位置特征 |
| 表示碰撞过多 | scalar 把 A/T 或 C/G 合并 | 增加 one-hot/property channels |
| 数据任务不匹配 | toy 类别太容易或太难 | 重构 toy 数据 |
| 模型利用不了信息 | 有位置特征但 pooling 抹掉 | 更换模型或 pooling |
| 训练不稳定 | seed 方差大 | 简化模型、调学习率、重复 seeds |
| 评估口径错误 | SVD 泄漏或 split 不当 | 修复评估流程 |
| 临床约束缺失 | clean 数据满分 | 加噪声、host、near species |

### 新方案生成模板

每个新方案都必须写成下面格式：

```text
方案编号：
来源失败：
核心假设：
与已有方案的最小差异：
最小验证数据：
最小实现：
成功判据：
失败判据：
下一步：
```

### 候选新方案池

初始候选：

1. multi-k fusion：融合 3/4/5/6/7-mer profile。
2. spaced k-mer：降低 substitution 对连续 k-mer 的破坏。
3. minimizer/sketch feature：轻量化近似匹配。
4. mismatch-tolerant k-mer：允许 1 mismatch 的邻域聚合。
5. reverse-complement canonical + strand flag：兼顾链不变性与方向信息。
6. composition + order hybrid：count vector 与 token CNN 融合。
7. property-channel CNN：one-hot + GC/purine/EIIP 通道。
8. relative-position motif encoding：弱化绝对位置，强调 motif 内相对位置。
9. confidence-aware classifier：输出 unknown 或低置信拒识。
10. hard-negative mining：专门加入近缘 reads 作为困难负例。

## 三、如何保证思路不中断、不遗漏

这里不依赖记忆，而依赖项目内的显式记录和检查点。

### 1. 三本账

后续维护三个文件：

- `results/experiment_log.md`：记录每次实验做了什么。
- `results/failure_log.md`：记录每次失败和原因归类。
- `results/ideas_backlog.md`：记录所有候选新方案和状态。

### 2. 每轮固定闭环

每轮实验结束必须回答 6 个问题：

1. 这次验证的假设是什么。
2. 使用的数据是否能检验这个假设。
3. 哪个表示法赢了，哪个输了。
4. 失败最像哪一类失败。
5. 下一个最小实验是什么。
6. 是否需要把某个想法加入 backlog。

### 3. 实验状态机

每个方案只允许处于以下状态之一：

```text
idea -> planned -> implemented -> smoke_tested -> benchmarked -> accepted/rejected/revise
```

### 4. 结论分级

不把所有观察都写成结论：

- Level 0：代码功能通过。
- Level 1：toy 数据支持。
- Level 2：小真实序列支持。
- Level 3：噪声/近缘压力测试支持。
- Level 4：临床式混合数据支持。

这样可以避免 toy read 上的成功被误写成论文级结论。

### 5. 防遗漏检查清单

每次新增方案前检查：

- 是否已有相近方案。
- 是否有明确失败来源。
- 是否能用最小数据验证。
- 是否有必要新增模型，还是只改表示法即可。
- 是否有对应消融。
- 是否会引入数据泄漏。
- 是否记录运行配置。
