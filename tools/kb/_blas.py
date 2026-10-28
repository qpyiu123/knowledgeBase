"""必须最先导入：在 numpy 加载前置好 BLAS 线程数。

**结论（在权重预转置成 C 连续之后重测，i5-12500H 12 核 / OpenBLAS 0.3.34）：**
  线程数 越大越快（前提是权重已预转置，否则小矩阵上多线程反而是灾难）
    1 线程  -> 300 字约 124 ms，batch8 约 5.9s
    4 线程  -> 300 字约 100 ms，batch8 约 4.5s
    8 线程  -> 300 字约  94 ms，batch8 约 3.4s
   12 线程  -> 300 字约  99 ms，batch8 约 3.2s   （最佳）
  默认取 12，可用环境变量 KB_BLAS_THREADS 覆盖。

注意：早期版本这里写的是 1，那是因为当时 `x @ W.T` 的权重是 F-contiguous 视图，
BLAS 每次都要重新打包，多线程调度开销被放大。npbert.wT() 预转置之后限制就解除了。
"""
import os

_n = os.environ.get("KB_BLAS_THREADS", "12")
for var in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS",
            "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(var, _n)
