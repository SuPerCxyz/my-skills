# Decompression

Use this file only when the input is a `.eslog` bundle. If the user already provides an
extracted `ecs.*` directory, skip to [directory-map.md](directory-map.md) and
[analysis-playbook.md](analysis-playbook.md).

## Input Selection 输入选择

- 用户指定 `.eslog` 文件或目录时, 通过 `--input` 原样传入。
- 用户未指定路径时, `--input` 默认使用当前工作目录, 输出也默认使用当前工作目录。
- 输入目录只匹配顶层 `*.eslog`, 不递归扫描其他位置。
- 指定单个 `.eslog` 文件且未传 `--output` 时, 输出默认使用该文件的父目录。
- 指定输入目录且未传 `--output` 时, 输出默认使用该输入目录, 即顶层压缩日志所在的目录。
- 显式传入 `--output` 时, 始终使用用户指定的输出目录。
- 同一 bundle 已有经过校验的对应输出目录时, 不重复解压。只有输出缺失、不完整或用户
  明确要求刷新时才重新解压; 刷新时使用新的输出目录, 或先明确旧目录会被合并。
- 发生明确刷新时, 同路径文件使用本次内容覆盖, 新文件追加, 本次 bundle 未包含的旧文件
  保留; 合并结果必须在报告中标明涉及的 bundle 和输出目录。

## Safe Script 安全脚本

使用仓库内置脚本, 不要从文档复制临时脚本:

```bash
# One explicit bundle; without --output, results are placed beside the bundle
bash scripts/decompress-eslog.sh --input /path/to/ecs.example.eslog

# Override the default output directory when needed
bash scripts/decompress-eslog.sh \
  --input /path/to/ecs.example.eslog --output /path/to/output

# All top-level .eslog files in the current directory
bash scripts/decompress-eslog.sh

# The script always creates readable .log files and keeps original .log.gz files
bash scripts/decompress-eslog.sh --input /path/to/ecs.example.eslog
```

脚本行为:

- 内层 ZIP 默认暂存在 `/var/tmp` 的权限隔离临时目录, 避免与大体积输出共同占用
  `/tmp`; 设置 `TMPDIR` 时使用该目录。目标不可用时才回退到输出目录。
- 退出时清理内层 ZIP 临时目录。
- 外层 bundle 一次只处理一个内层归档, tar 通过管道校验和解包, 不保留 tar 副本。
- 解包前校验 tar 成员路径, 拒绝绝对路径、`..` 路径逃逸及非 `ecs.*` 顶层目录。
- 直接向同名 `ecs.*` 目录增量覆盖, 避免为旧结果创建完整副本而耗尽磁盘配额。
- 解包失败时停止并报告已处理范围; 已覆盖文件不自动回滚。修复空间或归档问题后可
  使用同一命令再次解压, 让完整 bundle 补齐结果。
- 展开前按每个 `ecs.*` 目录汇总 gzip header 中的 uncompressed size, 并保留额外
  16 MiB 余量; 空间不足时在写 `.log` 前停止。
- 保留原始 `.eslog` 和 `.log.gz`; 先写唯一 `.log.part.<pid>`, 成功后再原子替换
  对应 `.log`, 失败时删除 partial file 并保留旧的可读日志。
- 后续分析和人工查看统一使用 `.log`, 不直接对 `.log.gz` 执行搜索。
- 所有 bundle 解压并生成 `.log` 后, 创建 `components/` 普通文件视图。该目录沿用原始
  组件路径, 例如 `components/openstack/cinder/`, 不保留 `ecs.node-*` 中间层。
- `components/` 复制 `.log` 普通文件而不是创建符号链接, 便于跨平台读取; 原始
  `ecs.*` 目录、`.log.gz` 和 `.log` 始终保留。
- 组件视图出现同名文件时按源文件大小处理: 较大文件覆盖较小文件, 较小或相同大小的
  文件不覆盖已有文件。复制先写临时文件并原子替换, 避免留下不完整日志。
- 创建组件视图前进行容量预检。组件视图会额外占用一份 `.log` 存储空间, 应将该空间
  计入输出目录容量规划。
- 展开前应确认输出目录空间; 空间不足时脚本失败并报告, 不回退到压缩日志分析。
- 默认密码来自 `ESLOG_PASSWORD`, 未设置时使用 EasyStack 默认值。

指定外部 bundle 且未传 `--output` 时, 解压完成后应在该 bundle 的父目录继续执行目录清单和
日志检索; 不要默认回到启动脚本的当前目录。

如果缺少 `unzip`、`tar`、`gzip` 等依赖, 先报告缺失命令和建议安装命令, 获得用户
确认后再安装。不要自动修改系统依赖。

## Output Layout 输出结构

```text
ecs.<hostname>.<date>.<N>/
|-- alcubierre/
|-- ceph/
|-- ceph-k8s/
|-- cloud-products/
|-- ecas/
|-- ecms/
|-- ems/
|-- kubernetes/
|-- libvirt/
|-- openstack/
|-- os/
`-- others/
```

组件视图位于输出目录下, 不属于任何一个 `ecs.*` 目录:

```text
components/
`-- openstack/
    `-- cinder/
        |-- cinder-api.node-1.20260807.log
        `-- cinder-volume.node-1.20260807.log
```

解压完成后先根据 bundle 文件名和日志 wrapper timestamp 确认覆盖时间窗, 再进入定向
检索。确认输出目录包含目标 bundle 的完整日志后, 停止解压并进入分析。明确刷新时仍是
增量合并: 同路径文件由当前 bundle 覆盖, 新文件追加, 当前 bundle 未包含的旧文件保留。
该过程不创建备份, 解压中途失败时不会自动回滚已经覆盖的文件。
