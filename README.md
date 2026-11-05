# CTF 知识库

离线查询编程文档、CTF 方法、题型和配套代码。先看关键词结果，再按需补充语义检索或模型解释。

## 开始使用

在 Windows 双击 [启动.cmd](启动.cmd)，浏览器会打开 [本地查询页](http://127.0.0.1:8765/)。双击默认只查资料，不加载生成模型。使用项目内的独立 Python，无需另装系统 Python。

在项目目录打开终端，也可以运行：

```powershell
.\启动.cmd -Status                 # 查看状态
.\启动.cmd -Stop -NoModel          # 停止查询服务
.\启动.cmd -CheckEnvironment       # 检查 Python 和依赖
.\启动.cmd -Start                  # 启动查询和默认解释模型
.\启动.cmd -ChatModel qwen35-4b     # 启动查询和 4B 解释模型
```

从仅查询切到解释模式前，先停止现有查询服务。查函数名、报错或题面特征时，可以直接粘贴原文。

## 更多说明

- [查询和模型解释](docs/guide/使用与查询.md)
- [换盘与打包](docs/guide/换盘与打包.md)
- [开发、评测和版本记录](docs/README.md)
