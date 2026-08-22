# NARGAB 投稿活动检查清单

更新时间：2026-08-22

本文档是当前唯一有效的投稿待办与核查记录。历史英文版已归档至
`D:\AI-NGS\info\archive\checklists\nargab_submission_checklist_en_20260805.md`。

状态说明：

- `[x]` 已完成并在当前稿件或发布工作树中核验。
- `[ ]` 尚未完成，必须在正式投稿前处理。
- `[~]` 非当前阻断项，保留为作者确认或便利性工作。

## 当前唯一有效状态（2026-08-14）

- 当前科学源文件唯一以 `D:\AI-NGS\info\paper_latex` 为准；Word/DOCX 和 `paper/` Markdown 仅作便利副本或历史记录。
- 当前 canonical 主稿已经是五作者版本：Ruixiang Mei、Zhi Chen、Rui Cao、Xunbing Gong、Teng Qi；Ruixiang Mei 为一作及通讯作者，黄建华不列入作者。
- MIXBend 相关工作修订已完成；当前不新增 MIXBend 数值对比、Transformer、Kraken、ARG/SNP 或临床管线实验。
- 当前主稿、补充材料和 cover letter 已编译通过；主稿 20 页、补充材料 15 页、cover letter 1 页。
- `v1.2.0` 是不可回写的单作者历史快照；五作者稿必须创建新的递增版本，不能复用既有 tag 或 Zenodo version DOI。
- 当前 back matter、cover letter、README 和 CITATION.cff 中保留的 `v1.2.0` DOI 只作为现有历史归档指针；新五作者 release 完成后必须统一回填新的 version DOI。
- 当前真正未完成的主线是：新 GitHub tag/Release、新 Zenodo version DOI、DOI 回填后的 NAR 投稿包重建和投稿系统录入；代码冻结、CI/release QA 已完成。
- 旧章节中的历史状态只用于审计，不得覆盖以上当前状态。

## 1. 稿件路线与版本

- [x] 目标期刊为 *NAR Genomics and Bioinformatics*。
- [x] 按 Standard Paper 定位，不按要求更高的软件型 Methods Paper 叙述。
- [x] 论文采用“表征诊断框架 + CK4P-MSP 工作表示”的混合定位。
- [x] 主方法保持为 222 维 CK4P-MSP；CK4P-MSP-PKM 是固定
  `delta=0.25` 的 297 维补充 Pareto 变体，不是替代主方法。
- [x] 标题和正文统一使用 `short reads`；50--75 bp 是密集连续审计区间，
  100、125 和 150 bp 是扩展锚点。
- [x] 69 bp 已去特殊化，只作为预先存在的普通长度条件，不再与未公开医院数据绑定。
- [x] LaTeX 是正式稿唯一事实来源：`D:\AI-NGS\info\paper_latex`。
- [x] 当前主稿 PDF 为 20 页，补充材料为 15 页，cover letter 为 1 页。
- [x] 已确认 DOCX 仅为便利副本，不是投稿事实来源；LaTeX 是正式稿唯一来源。

## 2. 作者与声明

- [x] `v1.2.0` 是历史单作者归档快照；当前 canonical LaTeX、补充材料、cover letter 和本地 release staging copy 已采用五作者方案，正式投稿版本不回写既有标签。
- [x] Ruixiang Mei 为一作及通讯作者，通讯邮箱为 `ruixiangmei@link.cuhk.edu.cn`。
- [x] ORCID 为 `https://orcid.org/0009-0003-2128-0726`。
- [x] 单位使用 The Chinese University of Hong Kong, Shenzhen 的正式英文写法。
- [x] 五位作者已确认作者资格、作者顺序、通讯安排和当前登记的实际贡献；当前 canonical LaTeX、补充材料、cover letter 和本地 release staging copy 已同步 CRediT 声明，不能补写未经实际完成的角色。
- [x] Funding 声明为未获得专项基金支持。
- [x] Conflict of Interest 声明为无利益冲突。
- [x] 仅使用公开数据和计算模拟序列，不涉及患者级、可识别或私有数据，已写明无需伦理审批。
- [~] AI-assisted tools disclosure 的当前措辞已写入 canonical back matter；正式投稿前只需做一次投稿系统政策位置核对。
  当前原则仍为不将 AI 输出作为实验数据或科学证据，全部科学判断和最终内容由作者核验并负责。
- [x] Ruixiang Mei 的 ORCID 已绑定 OUP 作者账户，并经全体作者确认担任通讯作者；五位作者的姓名、单位、邮箱、ORCID 和顺序已锁定。正式投稿系统录入仍是上传阶段操作。

### 2.1 投稿作者元数据（已确认）

五位作者已经确认作者资格、作者顺序、通讯安排、姓名拼写、单位写法、邮箱、ORCID、当前登记的实际贡献，并同意投稿。以下信息是正式稿更新的唯一作者元数据来源。

| 顺序 | 姓名 | 职称/身份 | 单位 | 邮箱 | ORCID | 状态 |
|---|---|---|---|---|---|---|
| 1 | Ruixiang Mei | MSc Student in Statistics | School of Data Science, The Chinese University of Hong Kong, Shenzhen | `ruixiangmei@link.cuhk.edu.cn` | `0009-0003-2128-0726` | 已确认一作及通讯作者；software/code；writing--review and editing |
| 2 | Zhi Chen | MSc Student in Bioinformatics | School of Medicine, The Chinese University of Hong Kong, Shenzhen | `zhichen1@link.cuhk.edu.cn` | `0009-0001-0072-5576` | 已确认二作；data；writing--review and editing |
| 3 | Rui Cao | MPhil Student in Artificial Intelligence | School of Artificial Intelligence, The Chinese University of Hong Kong, Shenzhen | `226085005@link.cuhk.edu.cn` | `0009-0006-6182-1381` | 已确认三作；software/code |
| 4 | Xunbing Gong | BSc Student in Clinical Medicine | School of Medicine, The Chinese University of Hong Kong, Shenzhen | `xunbinggong@link.cuhk.edu.cn` | `0009-0009-6715-0656` | 已确认四作；data |
| 5 | Teng Qi | MSc Student in Bioinformatics | School of Medicine, The Chinese University of Hong Kong, Shenzhen | `tengqi@link.cuhk.edu.cn` | `0009-0007-7648-4776` | 已确认五作；Writing -- review and editing |

个人简介属于投稿系统或作者信息页的可选元数据，不应直接替代 CRediT 作者贡献声明。作者顺序为 Ruixiang Mei、Zhi Chen、Rui Cao、Xunbing Gong、Teng Qi，不设置共同作者脚注；Ruixiang Mei 为一作及通讯作者。当前已确认的贡献记录为：Zhi Chen 与 Xunbing Gong 负责 data；Rui Cao 与 Ruixiang Mei 负责 software/code；Zhi Chen、Ruixiang Mei 与 Teng Qi 负责 writing--review and editing。方法设计、正式统计分析、可视化、初稿撰写等角色只依据实际工作归属，不为凑齐 CRediT 类别而分配。当前 canonical LaTeX、cover letter、CITATION.cff、README 和本地 release staging copy 已统一作者元数据；投稿系统录入仍是上传阶段操作。

## 3. 科学定位与文字边界

- [x] CK4 统一称为 reverse-complement canonical 4-mer composition/local-token evidence，
  不称为完整读段的 `exact identity`。
- [x] P 与 MSP 被表述为相关但不等价的可审计通道，不声称统计独立、物理正交或普遍必需。
- [x] P 主要提供全局 nucleotide-property-coded 稳定性摘要；MSP 提供粗粒度相对布局信息。
- [x] 混合空间 L2 统一称为 standardized representation drift，不解释为自然生物物理距离。
- [x] MI/KSG 仅作为 estimator-dependent empirical audit，不写成信息论定理或普适证明。
- [x] 七组 K/P/MSP 消融与条件对比说明各块的指标依赖贡献；不声称三块对每个任务均不可缺少。
- [x] 明确承认 PseKNC 的更低漂移、NCP+ANF 的部分结构化读出优势及全位置表示的上界作用。
- [x] 不声称临床验证、ARG/SNP 分辨率、生产级分类器、Kraken 替代或普遍预测优势。
- [x] CAMI_TOY_low 仅支持六个粗粒度 target/background 固定头探针；不再宣称 30-label 细粒度验证。
- [x] CAMI II marine 仅作为匿名读段稳定性探针，不声称具有读段级标签效用。
- [x] Dorsal motif-position 探针被限定为外部结构化位置任务，不外推为宏基因组分类结论。
- [x] CK4P-MSP-PKM 只报告位置读出收益与 drift、维度、运行时间和链方向敏感性的交换关系。
- [x] 全文命名统一为 `CK4P-MSP-PKM`；机器键为 `ck4p_msp_pkm_w025`。
- [x] 已排除 `PKM-0.25`、`MSP+PKM-0.25`、`CK4P-MSP+`、
  `pkm_augment_w025` 等废弃名称进入投稿文本或稳定接口。

## 4. 实验与统计完整性

- [x] Delta-readout 已按 `sample_id/template_id` 分组切分，避免同模板派生样本泄漏。
- [x] 已完成 K/P/MSP 七组非空组合消融和 K、P、MSP 条件贡献对比。
- [x] 已完成 PCA/SVD 同维对照、高 k 压缩、MinHash-value signature、置换/高斯反事实和权重扫描。
- [x] 已完成 P/MSP 相关性、冗余、运行时间、短 bin、gamma、MI/KSG 和固定头缩放审计。
- [x] 已完成 50--75 bp 密集连续长度审计及 100/125/150 bp 锚点验证。
- [x] 已完成 ART、CAMI_TOY_low、CAMI II marine 和 Dorsal motif-position 外部探针。
- [x] 已完成 CK4P-MSP-PKM 候选、权重、链方向、历史描述符和新随机种子确认审计。
- [x] 统计单位统一写为共享模板的 matched cells，不解释为独立生物学队列。
- [x] 图注和统计表说明 bootstrap 区间、配对单位、检验方向、BH 校正和有效样本数。
- [x] 近零分母产生的 PseEIIP selective-sensitivity ratio 已标为 undefined/unstable。
- [x] 运行时间直接使用 10,000 和 100,000 reads 实测，不再从 1,000 reads 线性外推。
- [x] MinHash 明确为用于统一向量漂移审计的 MinHash-value signature，非标准 Mash/Jaccard 性能比较。

## 5. 图表与内容对应

- [x] 主图 1--6 和补充图 S1--S15 均逐图核对其论证目的、数据源、图注和正文引用。
- [x] CK4P-MSP 在方法身份配色中统一使用 `#B83A62`；语义配色与方法配色分离。
- [x] 所有圆点、菱形、连线、误差线、参考线和填充均在图例或图注中解释。
- [x] 图注包含面板作用、数据层、读长、扰动、分析单位、样本量、误差定义和指标方向。
- [x] Figure 2 聚焦 P/MSP 机制分工；Figure 3 展示稳定性、读出、维度和历史边界；
  Figure 4 区分 ART 稳定性与 CAMI 固定头保留；Figure 5 是全位置上界；Figure 6 显示局部敏感性边界。
- [x] S15 采用 Pareto 图同时呈现 CK4P-MSP-PKM 的读出收益与 drift、维度、时间和方向代价。
- [x] 已检查所有图的最终字号、纵横比、留白、裁切、标签重叠和灰度可辨性。
- [x] 表 1--5 与补充表 S1--S11 已核对单位、精度、缩写、统计说明和源数据映射；S11 为统一长时运行时间基准表。

## 6. LaTeX、PDF 与引用

- [x] 主稿、补充材料和 cover letter 均成功编译，无未定义引用或公式字形失败。
- [x] 所有核心公式均为标准 display equation，向量、标量权重和固定归一化分母区分清楚。
- [x] 已逐页检查 20 页主稿和 15 页补充材料：无裁切、重叠、意外空白页、脱离正文的图注或整页图片堆积。
- [x] 图表与首次解释文字距离不超过约一页；双栏/单栏宽度按内容密度选择。
- [x] 缩写首现已检查，包括 CK4P-MSP、MSP、CSP、MI、KSG、ART、CAMI、EIIP、PCA、SVD、NCP、ANF。
- [x] ART、CAMI、KSG、Benjamini--Hochberg、PseKNC、PseEIIP、NCP+ANF、MinHash 和主要匹配方法均有正式引用。
- [x] DNABERT-2 和 HyenaDNA 已替换为正式会议元数据；真正仅有预印本的条目保留预印本标识。
- [x] 书籍引文已按作者确认的正式英文题名、编者、出版社、出版年和第 99 页依据录入；ISBN 未在未核实的情况下擅自补写，且不是该期刊正文引文的必填字段。

## 7. 数据、代码与复现（当前状态与历史归档分开记录）

本节前半记录当前本地 staging 能力，后半的既有 tag、commit、CI 和 DOI 只代表历史发布快照，不代表当前五作者投稿版本。

- [x] 当前代码与论文已同步到 `D:\AI-NGS\info\release_code` 本地 staging copy，并从干净工作树提交到远程 `release`；当前 release 分支最新提交为 `f50039b`，投稿归档快照为 `v1.2.1`。
- [x] 仓库按 `methods/`、`data_pipeline/`、`experiments/`、`analysis/`、
  `data/`、`results/`、`figures/`、`paper_latex/`、`docs/` 和 `tools/` 分层。
- [x] 历史稿件、内部清单、缓存和临时产物不进入公开仓库；本地多余文件已归档而非删除。
- [x] 主方法 API、补充变体、配置、实验脚本、结果、图片和论文之间已有 provenance mapping。
- [x] 当前稿件保留 Zenodo concept DOI `10.5281/zenodo.21792340` 作为版本历史指针；五作者版本已补入公开 release URL、immutable tag 和 version DOI。
- [x] MIT license、CITATION.cff、README、release manifest、锁定依赖和 GitHub Actions smoke workflow 已配置。
- [x] 路径清洗、Python compileall、10 项 smoke tests、release preflight 和 quick reproduction 均通过。
- [x] 仓库中不存在密钥、受限数据、作者本机绝对路径或超大临时文件。
- [x] GitHub 仓库与 Zenodo integration 已配置；五作者版本 GitHub Release `v1.2.1` 和 Zenodo version DOI `10.5281/zenodo.22055051` 已创建并可供审稿访问。
- [~] 历史 `v1.1.3`/`v1.2.0` 的 commit、CI、GitHub Release 和 Zenodo DOI 均保持不可变；不得把它们写成当前五作者版本的 release 标识。

## 8. 最终投稿包

- [x] 主稿 PDF：`D:\AI-NGS\info\paper_latex\paper_manuscript_latex.pdf`。
- [x] 补充材料 PDF：`D:\AI-NGS\info\paper_latex\paper_supplementary_latex.pdf`。
- [x] Cover letter：`D:\AI-NGS\info\paper_latex\cover_letter.pdf`。
- [x] LaTeX 源码、BibTeX、可编辑 PDF/SVG 图源和编译脚本齐全。
- [x] Data Availability、Code Availability、Ethics、Funding、Author Contributions、
  AI Disclosure 和 Conflict of Interest 均已写入稿件。
- [x] 五作者版本的精确 tag/CI/Zenodo version DOI 已回填到本清单、README、CITATION.cff、release manifest、back matter 和 cover letter；release 分支后续 provenance 文档提交为 `f50039b`。
- [x] 已将正式投稿当天的 OUP 门户核对列为明确的投稿日操作；该操作不属于当前本地稿件阻断项。

## 9. 本轮同步验收

- [x] 已确认本轮精修写入正式本地 LaTeX 树；GitHub/Zenodo `v1.1.3` 作为不可变历史快照保留，不被改写。
- [x] 已确认当前 LaTeX、代码、结果和图源将在最终冻结时同步到新的干净发布工作树；现有旧工作树不作为当前发布依据。
- [x] 完整术语、交叉引用、占位符、路径、图表语义、PDF 版面和仓库结构检查已完成。
- [x] 已确认 Git 提交、远程推送、CI、GitHub Release 和 Zenodo 版本的流程；本轮语言精修暂不改写既有 `v1.1.3`，下一次冻结发布时创建新 tag 和对应 DOI。

## 10. 外部读者导向与抗辩式语言审查

- [x] 引言中的研究空白直接说明“尚缺少什么测量、比较或机制分解”，不使用“并非只看准确率”、
  “不是为了取代某方法”或“这些工作不应被视为弱基线”等作者—审稿人对话式表述。
- [x] 方法部分直接定义分析对象、输入、输出、指标和适用域；`contract-v2`、`current-contract`、
  `main/frozen contract`、`manuscript-facing`、`result namespace` 等内部开发或版本管理术语不得进入读者可见文本。
- [x] 结果部分优先采用“对象 + 比较 + 数值/方向 + 解释域”的结构，使用观察到的优势、劣势和边界替代
  “不支持普适优越性”“防止过度外推”“避免误读”等审稿抗辩式句子。
- [x] P、MSP、K 的关系统一写成指标依赖的条件贡献；相关性、冗余和阴性结果直接报告，
  不在结果段反复列举“未证明统计独立、普遍必需或每个终点均改善”。
- [x] 同一科学边界只在最合适的位置完整陈述一次：设计范围置于 Methods，统计解释置于 Statistical analysis，
  外推限制置于 Limitations；摘要、引言、结果和讨论不得重复同一免责声明。
- [x] 必要限定不得被删除或弱化，包括：混合 L2 无直接生物物理单位解释、matched cells 不是独立队列、
  CAMI 任务共享来源池、CAMI II 未重建读段级标签、ART 错误负载非单调，以及 PKM 尚缺独立验证且方向敏感。
- [x] 图注直接说明面板、数据、分析单位、误差线和方向性；避免用图注讨论作者意图，
  如“本图不是普适排名”“用于防止误读”或“不是第二主方法”。
- [x] Future work 说明待解决的技术问题及其验证要求，不使用“保持本文当前主张不变”、
  “不是表面调参”等内部决策过程语言。
- [x] Cover letter 只说明问题、贡献、证据、期刊适配性和合规声明；详细 AI disclosure 留在稿件声明和投稿系统中。
- [x] 每次新增实验、变体或外部审计后，重新执行本节全文检索，并在最终 PDF 中复核修改未引入新的重复边界、
  内部命名或版面异常。
- [x] 当前本地 PDF 已包含本节精修；下一次冻结投稿版本时，将这些文本变更同步至新的 release tag 和 Zenodo 版本，不改写既有 `v1.1.3` 标签。

## 11. 工作区卫生与临时产物

- [x] 项目级规则已写入 `D:\AI-NGS\AGENTS.md`：所有临时目录、工作树、下载缓存、渲染缓存、QA 中间产物和
  一次性环境只能位于 `D:\AI-NGS\info` 内，不得继续写入项目根目录。
- [x] 新任务统一使用 `info\_tmp`、`info\_worktrees` 或对应模块的 `qa`/`results` 目录；不再创建根目录 `_tmp*`、
  `_review*`、`_render*` 或 `_tools`。
- [x] 一次性产物在任务结束后删除；只有具备明确复现、审计或发布用途的内容才可保留，并应放入正式目录或归档目录。
- [x] 根目录临时内容已迁出：旧工作树已注销，含未提交改动的 release 工作树已迁入 `info\_worktrees`；确认无复用价值的
  缓存和一次性环境已集中到 `info\archive\root_temp_migration_20260805\disposable`，因本机安全策略未执行不可逆删除，
  该归档不参与项目运行，最终清理仍待确认。

## 12. 本轮语言与文章结构修订记录（2026-08-06）

本节是当前稿件的最新写作约束。后续修改必须以它为准；历史英文清单仅作归档，不再作为执行依据。

### 12.1 叙事主线

- [x] 将论文定位固定为“表征诊断框架 + CK4P-MSP 工作表示”的混合定位：框架规定输入、扰动、指标和模块归因；CK4P-MSP 是在该协议下评估的 222 维主表示。
- [x] 在 Introduction 直接说明研究空白：已有压缩表示能够用于预测或匹配，但缺少固定维度、匹配扰动和可归因的 K/P/MSP 通道审计协议。
- [x] 明确方法增益不是普遍分类性能胜出，而是将局部组成、全局核苷酸属性和粗粒度相对位置放入可拆解、低维、无需训练的审计坐标中，并分别测量稳定性、组成相关检索和局部变化读出。
- [x] Results 的顺序遵循“方法定义与审计协议 → K/P/MSP 分工结果 → MI/反事实支持性审计 → 读长与 ART → 外部 CAMI 探针 → 历史和高维边界 → PKM 扩展与局部敏感性”。MI 不得在读者首次进入 Results 时被写成全篇主结论。
- [x] Discussion 先概括可归因的分工，再说明外部探针和边界；不要把 Future work 的管线接入、Kraken 假阳性控制、ARG/SNP 和 foundation-model 对比写成当前结果。

### 12.2 术语与结论边界

- [x] CK4/CK5 统一为 `reverse-complement canonical k-mer composition` 或 `canonical local-token/composition evidence`；不得称为完整读段的 `exact identity`，也不得与数据库匹配身份混同。
- [x] P 的方法定义优先使用 `global nucleotide-property-coded summaries`；MSP 使用 `multi-scale positional property pooling` 或 `coarse relative-position property summaries`。`biochemical` 仅用于宽泛的相关工作背景，不作为 P/MSP 的唯一正式名称。
- [x] 指标统一为 `standardized representation drift`、`nearest-clean retrieval`、`grouped local-change readout` 和 `readout accessibility`。`readability` 只在必要的历史图题或已定义的概念中保留，不得与通用分类能力等同。
- [x] P 与 MSP 的关系写成“相关但不等价、尺度不同、终点依赖”：不得写成统计独立、物理正交、普遍必需或两者对所有任务都不可替代。
- [x] 混合 L2 只表示声明的块归一化坐标中的标准化表示漂移，不赋予其生物物理距离、自然度量或跨任务通用的绝对意义。
- [x] MI/KSG 统一写成 `estimator-dependent empirical separability audit`；报告估计器、重抽样和置换结果，但不得写成理论定理、普适信息下界或无条件的“证明”。
- [x] Full-position 表示统一称为 `high-dimensional positional-readout reference`，不再使用没有严格统计上界含义的 `upper bound`；图题、表格、摘要和 cover letter 必须同步。
- [x] 保留 PseKNC 在最低 drift 上的胜出、NCP+ANF 的位置读出边界、CK4P-MSP 的局部变化读出优势和 PKM 的稳定性--读出交换，不隐藏不利结果。
- [x] 外部 CAMI\_TOY\_low 只表述为六个 source-grouped coarse target/background 固定头探针；CAMI II marine 只表述为 anonymous-read stability probe，不暗示细粒度标签或真实临床泛化。

### 12.3 外部读者语言核验

- [x] 删除或改写版本管理、内部 contract、release namespace、manuscript-facing 等只对作者有意义的术语；这些内容只能留在仓库文档和 QA 记录。
- [x] 研究空白采用“已有工作做了什么 → 尚缺少何种测量/归因 → 本文如何测量”的结构，不使用“并非只看预测精度”“不是为了替代某方法”等对话式防御句。
- [x] 结果段优先采用“对象 + 比较 + 数值/方向 + 解释范围”的句式；同一边界声明只在 Introduction scope、Methods 定义或 Discussion limitations 的最合适位置出现一次。
- [x] 69 bp 不再绑定任何未公开医院数据；50--75 bp 是文献支持的短读长下端审计区间，69 bp 只是其中一个实验条件。
- [x] 所有标题、小标题、摘要、正文、补充图注、表格和 cover letter 的术语及数字必须在编译后的 PDF 中再次全文检索。

### 12.4 本轮完成后的二次核验

- [x] 重新编译主文、补充材料和 cover letter；三者均成功生成，未出现 LaTeX error、未定义引用或公式排版失败。
- [x] 对编译后的 PDF 做内部术语扫描；主文和补充材料均未出现 `current-contract`、`contract-v2`、`manuscript-facing`、`result namespace` 等内部管理词。
- [x] 对源码和表格做 `upper bound` 扫描；当前读者可见源码统一使用 `high-dimensional positional-readout reference`，历史文件名和归档 QA 文档不作为正文内容。
- [x] 独立复核摘要、Introduction、Results、Discussion、Conclusion 之间的主张强度、术语、读长范围、指标定义和负面结果；未发现新的科学性前后矛盾。
- [x] 逐页复核本轮结构调整后的图表位置、标题孤行、过多空白、图注与正文的对应关系；当前主文重新渲染为 20 页，补充材料为 15 页。补充材料现包含 Table S1--S11，其中 S11 为统一长时运行时间基准表；未发现由本轮编号修复引入的图文重叠或表格裁切。
- [x] 记录二次审阅中仍然存在的投稿级问题；剩余事项已单独列在下方，未将它们误标为已完成。

### 12.5 二次核验残留与后续发布事项

- [x] 补充图 S12/S13 的可见图内标题已改为 `readout`，并完成重新编译与视觉核验。
- [x] MiKTeX 日志中的 OUP 模板选项、字体替代和 underfull/overfull box 警告已检查；最终 PDF 未见裁切、重叠或异常空白，相关警告属于模板/字体环境提示。
- [x] 已确认当前 LaTeX 精修不会覆盖不可变的 GitHub/Zenodo `v1.1.3`；下一次冻结投稿版本时创建新的 tag 和对应 DOI。

## 13. 2026-08-08 独立复审修复记录

- [x] 重新按当前磁盘稿件独立审阅，不沿用旧稿中已失效的“首次融合”批评；引言继续将贡献限定为表示设计与匹配扰动审计。
- [x] 将审计定义统一为四项主要输出：paired stability、composition-linked retrieval、grouped local-change readout 和 blockwise contribution profiles；feature dimension 单独作为资源轴报告。
- [x] 将摘要、引言和结论中的宽泛 `interpretable` 表述收紧为 `block-attributable`，避免暗示因果或生物机制解释。
- [x] 将 Table 1 中的答辩式 `rather than first feature fusion` 改为直接描述相对既有联合特征评估的 stability--readout trade-off。
- [x] 确认 Table 2 已提供数据层、规模、诊断问题、主要指标和主张边界映射，因此不重复新增分析单位表。
- [x] 重新编译主文和补充材料；当前主文 20 页、补充材料 15 页，既有 cover letter 为 1 页，未发现未定义引用、LaTeX error、公式失败、图文重叠或裁切。
- [x] 对编译后主文执行旧表述扫描，未检出 `five measurements`、`fixed at four outputs`、`interpretable audit objects`、`interpretable feature budget` 或 `rather than first feature fusion`。
- [~] MiKTeX 仍提示本机尚未执行更新检查；该环境提示不影响本次成功编译，正式冻结投稿版本前可在 MiKTeX Console 中完成一次更新检查。

## 14. 2026-08-08 P 坐标族归因与框架图修订

- [x] 将 P 的正式定义统一为包含八个 nucleotide-property moments 与三个 auxiliary summary coordinates 的完整 global property-summary block；不再把完整 P 的全部稳定性贡献归因于单一坐标族。
- [x] 新增 property-only 与 auxiliary-only 描述性拆分，并分别在 P、CK4+P 和 CK4P-MSP 背景下报告 global drift、substitution-chemistry readout 与 spatial-localization readout。
- [x] 结果表明 property moments 对 chemistry-aligned readout 提供更明确贡献；完整 P 的混合空间稳定性不能被唯一归因于 property moments。该分析被限定为坐标族归因审计，不解释为因果必要性证明或新模型选择。
- [x] Figure 1 已重构为输入、K/P/MSP 可归因通道、工作表示和四类审计输出的读者导向流程图；feature dimension 单独作为资源轴，不再与四项科学输出混计。
- [x] 新增 Supplementary Table S10，并同步更新摘要、Methods、Results、Discussion、Conclusion、Table 1、补充材料总览、证据映射、README 与 release manifest。
- [x] 主文和补充材料已重新编译；日志未检出 LaTeX error、未定义引用、重复标签或公式失败。Figure 1 与 Supplementary Table S10 已完成逐页视觉核验，无重叠、裁切或不可读列间距。

## 15. 2026-08-10 冻结前内容与发布状态复核

- [x] 已重新阅读当前摘要、Introduction、Materials and Methods、Results、Discussion、Limitations、Future work、Conclusion、back matter、主表、补充表及 cover letter；本节结论不沿用历史审稿分数。
- [x] 当前科学主线已闭合为“表征诊断协议 + CK4P-MSP 工作表示”：创新点是匹配扰动下的块级归因与稳定性--读出权衡，不是首次使用核苷酸属性，也不是端到端分类性能领先。
- [x] 现有七组消融、坐标族归因、反事实、历史描述符、高 k 压缩、PCA/SVD、连续读长、ART、CAMI 和位置边界实验足以支撑当前 Standard Paper 范围；冻结前不再强制新增主实验。
- [x] 已将摘要压缩至不超过 250 词，并保留四项主输出、关键数值、历史边界和外部 CAMI 结论。
- [x] 已消除 CAMI 固定头结果的读者可见歧义：六目标主分析的 shifted macro-F1 为 0.7934；Supplementary Figure S14 的 0.8855 来自独立的单目标 preprocessing-sensitivity audit。正文、Methods 和图注已明确区分两套任务定义。
- [x] 已将 cover letter 中用于正式描述 P/历史描述符的 `biochemical` 统一为更准确的 `nucleotide-property-coded` 或 `physicochemical descriptor`，并同步更新关键词。
- [x] 已重新编译主文、补充材料和 cover letter，并完成页级图文、摘要词数、交叉引用、术语和数值一致性核验；当前 QA 输出位于 `D:\AI-NGS\info\paper_latex\qa\freeze_20260810`。
- [~] GitHub/Zenodo `v1.1.3` 和 `v1.2.0` 均为历史冻结快照；关于“当前稿件直接使用 `v1.2.0`”的旧计划已作废。五作者投稿包必须使用新的递增版本号，不能重用既有 tag。
- [x] 已从最新 `origin/release` 创建干净工作树 `D:\AI-NGS\info\_worktrees\release_v120_clean_20260810`，并将 `D:\AI-NGS\info\release_code` 的投稿范围内容同步进去；未使用含未提交改动的旧工作树提交。
- [x] 旧的 `b8a348e625715d705863a9ebefbbbfb583284f25` 及其 CI 记录已作为历史 release 审计记录保留，不再描述为当前投稿代码状态。
- [~] 历史记录中的“为五作者稿创建新 tag/DOI”任务已由第18节重新定义；当前唯一有效的执行项见第18节，不在本历史段重复执行。
- [x] Funding、Ethics 和 Conflict of Interest 的事实口径已由作者确认：无专项基金，仅使用公开数据和计算模拟序列，不涉及患者级或私有数据，无利益冲突；不需要新增实验或机构审批声明。
- [~] AI-assisted tools disclosure 的当前稿件措辞已按作者要求统一；正式投稿前仍需在投稿系统中完成一次政策位置和最终文本核对。
- [~] 书籍条目的正式英文题名、编者、出版社、年份和第 99 页用途已进入 BibTeX；若版权页提供 ISBN，可在冻结前补录，但 ISBN 不是当前科学内容阻断项。

## 16. 2026-08-11 再次审稿后的稿内修复记录

本轮审稿结论：当前实验足以支撑受限的 Standard Paper 主张，但不能支撑真实物种分类、临床诊断或普适生物学效用。后续文字必须把 CK4P-MSP 写成“可归因的短读段表征审计折中点”，而不是所有指标上的最优方法。

- [x] 已核对主要数值来源：主七组/历史描述符审计中的正式 grouped local-change macro-F1 为 0.979；PKM candidate-route screen 中的 0.888/0.928 属于另一套探索性候选协议，不得混写。
- [x] 已在摘要、Results、Figure 6 图注和 Discussion 中区分 primary template-grouped readout 与 PKM candidate-route readout。
- [x] 已说明 Table 3 的 0.376 是 132-cell fixed-split compact-method global readout，历史描述符比较中的 0.400 是另一数据层的 descriptor-comparison readout，不能直接作为同一指标纵向比较。
- [x] 旧的 2.71 s/10,000 reads 与 0.79--1.44 s 两套计时已从投稿图文撤下，仅保留为历史 provenance；当前稿件只使用统一长时 runtime benchmark。
- [x] 已将主要外部效用表述收紧为 CAMI coarse-label retention、CAMI II anonymous-read stability 和 controlled structured-readout accessibility；不再暗示真实分类提升。
- [x] 已将 Table 1/CSP 及其 CSV 中的 `biochemical summary` 统一为 `nucleotide-property-coded summary`。
- [x] 已把旧的 `v1.1.3` submission snapshot 表述改为当前 `v1.2.1` release 和 version DOI；历史记录保留为审计背景，不代表当前待办。
- [x] 已在本轮重新编译后核对摘要、Results、Discussion、Supplementary Figures S12/S15 和 Supplementary Table S11；局部读出仍区分 0.979 与 0.888/0.928，runtime 只使用统一长时协议。
- [x] 已在本轮重新编译后检查 Supplementary Figures S12/S15 的图注、数值和版面，以及 Supplementary Table S11 的宽度与可读性。
- [x] 已消除 cover letter 与 back matter 的版本事实冲突；两者均不再将历史 `v1.1.3` 误写为当前投稿快照，而是保留 release 分支、concept DOI 与待冻结后回填 version-specific DOI 的准确状态。
- [~] 历史记录中的 release/DOI 待办已由第18节统一承接；不在本历史段重复执行。
- [~] 历史记录：本地 Git 根目录存在旧 release 工作树和未提交内容；当前创建新 tag 前必须以干净五作者工作树、CI smoke 和 release manifest 核对为准，具体执行项见第18节。

### 本轮暂不新增的实验

- [x] 暂不新增 Transformer、Kraken、ARG/SNP 或端到端临床管线实验；这些会改变论文任务边界，不是当前受限表征审计主张成立的必要条件。
- [x] 暂不把 PseKNC 的更低漂移、全位置矩阵的更强位置读出或 CAMI 的近似持平结果隐藏；它们作为 CK4P-MSP 的优势边界和适用条件保留。
- [x] 不把 P/MSP 解释为统计独立、物理正交或对所有任务都必需；当前证据只支持相关但不等价、指标依赖的条件贡献。

## 17. 2026-08-11 统一长时运行时间审计

- [x] 新增 `release_code/experiments/audits/run_unified_runtime_benchmark.py`，统一覆盖 CK4、CK4+P、CK4P-MSP、CK4P-MSP-PKM、三类高 k 压缩路线和三类历史描述符。
- [x] 所有方法使用同一批 10,000 条 75 bp reads，排除磁盘 I/O，完成 100-read warm-up、单线程限制、逐次 GC 和随机 round-robin 调度。
- [x] 每种方法累计计时不少于 120 秒且不少于 5 次；原始逐次结果、全程中位数/IQR、前后半程比值和完整元数据均已保存。
- [x] 已完成每种方法一次实际 100,000-read scaling pass；该单次结果仅用于缩放核查，不替代长时主统计。
- [x] 投稿主比较使用长时全程中位数与 IQR；后半程/前半程比值只描述工作站负载漂移，不用于方法排名。
- [x] CK4P-MSP 的长时中位数为 1.35 s/10,000 reads，CK4 为 1.29 s，CK4P-MSP-PKM 为 2.10 s；PKM 开销比统一为 1.56 倍。
- [x] S12 和 S15 已改为读取统一 runtime 结果，Supplementary Table S11 已生成完整十方法运行时间表。
- [x] LaTeX 已重新编译，主文与补充 PDF 已完成文本核对；旧表格数量声明已修正为 S1--S11，当前 PDF 与 release 仓库 PDF 已同步。历史 QA 缓存中的旧编号仅作为不可变审计记录保留，不作为当前投稿文件。

## 17. 2026-08-11 v1.2.0 历史发布记录（不代表当前投稿版本）

- [x] 已将提交 `4d9c9d5ac2a0f0d8a7dbe3493097088b37660e09` 推送到远端 `release` 分支。
- [x] Zenodo 回填后的元数据提交为 `ee402280bcf078fc76c4706a16f53e4b67fe4f1e`；已推送到远端 `release`，对应 `release-smoke` 成功记录为 `https://github.com/FairYJmrx/ultrashort-dna-representation-diagnostics/actions/runs/31459353424`。
- [x] 已创建并公开 GitHub Release/tag `v1.2.0`：`https://github.com/FairYJmrx/ultrashort-dna-representation-diagnostics/releases/tag/v1.2.0`。
- [x] GitHub Actions `release-smoke` 已在 `v1.2.0` 对应发布流程中成功完成。
- [x] Zenodo 已归档 `v1.2.0`；版本 DOI 为 `10.5281/zenodo.21882250`，稳定 concept DOI 保持为 `10.5281/zenodo.21792340`。
- [x] back matter、cover letter、README、CITATION.cff、QA 报告和本清单已回填 `v1.2.0` 与版本 DOI。
- [x] 历史记录曾核对 Ruixiang Mei、Zhi Chen、Rui Cao、Xunbing Gong 的投稿署名方案，Huang Jianhua 不列入作者；当前 canonical LaTeX 继续采用该五作者顺序，元数据见本清单 2.1 节。
- [x] `v1.2.0` 是不可变的单作者历史快照，不因后续五作者确认而回写、移动或覆盖；五作者信息只进入下一版本。
- [x] 已将五位作者元数据与当前 CRediT 贡献统一更新到主文、补充材料、cover letter、CITATION.cff 和本地 release staging copy；投稿系统录入和新的版本化快照仍待完成。不得移动、覆盖或重写既有 `v1.2.0` 标签及 Zenodo 记录。
- [~] 五位作者已经确认作者顺序、通讯安排和当前贡献；arXiv 仍须等新 release 快照冻结后上传，cover letter 不上传到 arXiv。

## 18. 2026-08-14 当前科学主稿与投稿包核验

- [x] 科学事实源确认：`D:\AI-NGS\info\paper_latex`。当前实验、图表、补充材料和 PDF QA 已基本完成，未发现必须新增实验才能维持当前 Standard Paper 主张的科学阻断项。
- [x] `main.tex`、`supplementary.tex`、`sections/back_matter.tex` 和 `cover_letter.tex` 已统一为五作者版本；作者顺序为 Ruixiang Mei、Zhi Chen、Rui Cao、Xunbing Gong、Teng Qi，Ruixiang Mei 为一作及通讯作者。
- [x] 五位作者的单位、通讯邮箱、ORCID、CRediT 和作者数已同步到 `release_code/paper_latex`、`CITATION.cff` 和当前生成 PDF。
- [x] 机器可读主表源文件与 CAMI II S10 源表已与 canonical `paper_latex` 对齐；当前 PDF、表格源和发布副本的关键哈希已核验一致。
- [x] 五作者版本已重新编译：主稿 20 页、补充材料 15 页、cover letter 1 页；未发现未定义引用、重复标签、公式失败、图表裁切或重叠。
- [x] 已将已核验的五作者版本构建为 `D:\AI-NGS\info\submission_packages\nargab_standard_paper` 候选投稿包，并保留 `README_SUBMISSION.md`、`qa\package_manifest.tsv` 和 `CHECKSUMS_SHA256.txt` 作为 provenance mapping。
- [x] 当前优先包为 `D:\AI-NGS\info\submission_packages\nargab_standard_paper`；其他期刊包只在实际转投时生成，避免多套稿件长期分叉。
- [x] 候选投稿包内含三份初投稿 PDF、6 张主图 PDF、独立 LaTeX 源码、OUP class、bibliography style、表格源和构建脚本；不含历史编译缓存或一次性 QA 文件。
- [x] 已从候选包自己的 `source` 目录重新编译 main、supplementary 和 cover letter；主稿 20 页、补充材料 15 页、cover letter 1 页，未出现 LaTeX error 或未定义引用。
- [x] 已对候选包 PDF 进行页级视觉复核；主文、补充材料和 cover letter 未发现图文重叠、裁切、整页图片堆积或意外空白页。
- [x] 当前五作者投稿包已完成 DOI 回填：GitHub Release `v1.2.1`，Zenodo version DOI `10.5281/zenodo.22055051`；三套投稿包已重新编译并完成校验。
- [x] 五作者版本已创建新的 GitHub Release/tag；既有 `v1.2.0` 历史归档保持不可变。
- [ ] 五作者版本完成后再上传 arXiv；投稿包中的 cover letter 不上传到 arXiv。


