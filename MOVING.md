# 移动硬盘迁移

离线包包含独立 Python、网页、资料和语义查询所需的模型与索引。换机后不需要安装 Python、Node.js 或 Git。

## 制作和复制

在开发仓库运行：

```powershell
runtime/python-portable/python.exe -X utf8 tools/pack_release.py --models both
```

输出为 `release/CTF知识库-R5-both`。默认 9B，可切换 4B。`--models 9b`、`--models 4b`、`--models none` 分别只带一种解释模型或仅查询；`--destination <新目录>` 可指定输出位置。不会覆盖现有目录或修改源模型。

复制整个目录到 Windows x64 的可写位置。9B 是大于 4 GB 的单文件，移动盘建议用 NTFS 或 exFAT。打开包内 `开箱说明.md`，先运行 ` .\start.ps1 -CheckEnvironment` 和 ` .\start.ps1 -NoModel`。

## 环境和模型

- 要缩小新包，直接按所需模型打包。已复制的双模型包可先切换并验证保留的权重，再移走迁移副本中不用的文件。语义查询使用的 BGE ONNX 和索引应一起保留。
- `-PythonExe`、`KB_PYTHON` 或 `[runtime].python` 可选择解释器。开发用 `.venv` 依赖原电脑的 Python，不随包复制。
- 外部取证工具是可选项：可通过 `KB_TOOLS_DIR` 指向自备目录，也可放在项目内 `tools/_bin` 或同级 `tools`。基本附件分析使用包内 Python。

## 迁移自己的记录

新包不带个人工作区。在旧项目运行 ` .\backup.ps1`，再用 ` .\backup.ps1 -Restore <备份.zip> -Destination <新空目录>` 解出备份，按需复制 `work/workspaces`、`work/attachments` 和 `work/feedback`。先核对同名记录再合并。

只搬路径不需要重建索引。改了资料后，先停服务，运行 ` .\start.ps1 -Reindex` 再启动。比赛机离线验收见 [R5 实施记录](docs/R5-实施记录.md)。
