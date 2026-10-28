# Scenarios

> 来源:`easystack-cloud-web-e2e/instance/instance.md`,按原文标题边界拆分。

## Scenarios 场景列表

### Scenario 场景 1: 创建云主机时添加数据盘

- 在 Step 1 的 Data Disk 配置中添加
- 选择 Volume Type 和 Size
- 可配置是否随实例删除

### Scenario 场景 2: 创建后挂载云硬盘

- 从 Volume 页面选择可用卷 → Attach → 选择实例
- 或从 Instance 页面 → More → Attach Volume

### Scenario 场景 3: 从云硬盘创建实例

- Volume 页面选择可启动卷 → Create Instance
- 或创建实例时选择 Boot Source 为 Bootable Volume

### Scenario 场景 4: 实例快照恢复

- Instance → More → Create Snapshot
- Instance → More → Snapshot Rollback

### Scenario 场景 5: 云硬盘随实例删除

- 创建实例时配置 Root Disk / Data Disk 的 "Delete with Instance" 选项
- 勾选后,删除实例时自动删除关联的云硬盘
