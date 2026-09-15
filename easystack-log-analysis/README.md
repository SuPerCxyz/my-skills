# EasyStack Log Analysis

EasyStack OpenStack 集群日志(`.eslog`)安全解压、目录映射、跨服务跨节点根因定位。
可独立完成离线证据链和无表格、行首安全问题调查报告。用户已提供运行中环境检查结果时,
可按时间窗作为补充证据合并, 但不依赖在线调查。

## 功能

- 加密 `.eslog` 压缩包解压
- 容器化日志目录结构与组件映射
- 跨域关联分析(云主机生命周期 / 云硬盘挂载卸载 / 网络 / 镜像 / 裸金属 Ironic)
- 按异常信号关联 OS 系统层与控制面基础设施, 避免无条件全量扫描
- 行首安全、无表格的离线分析报告模板与实战 case

## 快速开始

```bash
# Explicit input; without --output, results are placed beside the bundle
bash scripts/decompress-eslog.sh --input /path/to/bundle.eslog

# Explicit input and output override
bash scripts/decompress-eslog.sh --input /path/to/bundle.eslog --output /path/to/output

# Default: input and output are the current directory
bash scripts/decompress-eslog.sh
```

脚本保留原始 `ecs.*`、`.log.gz` 和 `.log`, 并在输出目录下额外复制一份按组件整理的
`components/` 普通日志文件, 便于跨平台直接读取。组件视图不保留 `ecs.node-*` 中间层,
同名文件按源文件大小保留较大者。指定外部 bundle 且未传 `--output` 时, 输出目录就是
该 bundle 的父目录。

## 文件说明

| 文件 | 内容 |
|------|------|
| [SKILL.md](SKILL.md) | Skill 主入口,工作流与快速参考 |
| [analysis-playbook.md](analysis-playbook.md) | 标准端到端分析流程 + 报告模板 |
| [report-format.md](report-format.md) | 完整问题调查报告格式 |
| [source-analysis.md](source-analysis.md) | kernel 和系统软件包源码调研、版本对齐与证据记录 |
| [cross-domain-analysis.md](cross-domain-analysis.md) | 跨域关联分析矩阵(各场景必看哪些日志) |
| [decompress.md](decompress.md) | eslog 解压方法 |
| [scripts/decompress-eslog.sh](scripts/decompress-eslog.sh) | 安全解压与跨平台组件视图脚本 |
| [tests/test-decompress-eslog.sh](tests/test-decompress-eslog.sh) | `.log`、merge 和组件视图回归测试, 使用 `bash` 执行 |
| [log-format.md](log-format.md) | 日志行格式、字段、awk 配方 |
| [directory-map.md](directory-map.md) | 日志目录结构映射 |
| [search-patterns.md](search-patterns.md) | 按问题类型的搜索模式 |
| [troubleshooting.md](troubleshooting.md) | 故障排查场景与实战 case |
