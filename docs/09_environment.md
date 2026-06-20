# 09 环境说明

当前项目使用本地虚拟环境：

```powershell
D:\AI-NGS\信息学\.venv\Scripts\python.exe
```

创建环境使用的是：

```powershell
D:\anaconda\python.exe -m venv .venv
```

安装依赖：

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

当前依赖：

- numpy
- pandas
- scipy
- scikit-learn
- pyyaml
- matplotlib
- joblib
- tqdm
- tabulate
- openpyxl

说明：

- 本机 `conda` 命令当前不在 PATH 中，但 `D:\anaconda\python.exe` 可用。
- 如果后续需要 PyTorch 或更复杂深度模型，建议再单独建立深度学习环境，不与当前轻量实验环境混用。
- 当前第一阶段以轻量数据、特征诊断和 scikit-learn baseline 为主。

## Windows/OpenBLAS 线程限制

如果运行高维 k-mer 诊断时出现 OpenBLAS memory allocation 错误，先在 PowerShell 中限制线程：

```powershell
$env:OPENBLAS_NUM_THREADS='1'
$env:OMP_NUM_THREADS='1'
$env:MKL_NUM_THREADS='1'
```

本项目的小规模实验不需要多线程 BLAS。
