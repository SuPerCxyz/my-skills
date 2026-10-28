# Page And Dialogs

> 来源:`easystack-cloud-web-e2e/image/image.md`,按原文标题边界拆分。

## Page Information 页面信息

| 项目 | 值 |
|------|-----|
| URL | 当前主路径:`https://<IP>/container-registry/image` |
| VM 镜像入口 | 通过 Computing -> Instance Image 现场识别; `/glance/images` 不是容器页面别名 |
| 导航路径 | Service Catalog → Image Repository → Image Management |
| 页面标题 | Image Management |

## Page Description 页面说明

镜像仓库是支持镜像全生命周期管理的服务,提供易用、安全可靠的镜像管理功能,帮助用户快速部署容器化服务。

### Sidebar 左侧导航

在"Image Repository"标题下:

| 菜单项 | 定位方式 | 说明 |
|--------|--------|------|
| Image Management | `侧边栏菜单项` | 当前选中 |
| Workspaces | `侧边栏菜单项` | 工作空间管理 |

## Toolbar Buttons 工具栏按钮

| 按钮 | 定位方式 | 状态 |
|------|--------|------|
| Refresh | 工具栏 icon 按钮 | 始终可用 |
| Upload Image | `buttonByText("Upload Image")` | 始终可用 |
| Push Image | `buttonByText("Push Image")` | 始终可用 |
| Delete | `buttonByText("Delete")` | 默认禁用,选中 1+ 行后可用 |
| Setup | `buttonByText("Setup")` | 始终可用 |

## Filter Fields 过滤器字段

定位方式:`input[placeholder="Click here for filters."]`

| 过滤字段 |
|----------|
| Name |
| Domain |
| Project |
| Workspace |
| Access Level |
| Tags |
| Create Time |

## Table Columns 表格列(9 列)

| 列名 | 可排序 | 说明 |
|------|--------|------|
| (选择框) | ❌ | 全选 checkbox |
| Name | ✅ | 镜像名称,点击进入详情页 |
| Domain | ✅ | 域名 |
| Project | ✅ | 项目 |
| Workspace | ✅ | 工作空间 |
| Access Level | ✅ | 访问级别:Private / Public |
| Tags | ✅ | 标签数量(徽章) |
| Create Time | ✅ | 格式:`16 Jun 2026 at 11:40:21` |
| Operation | ❌ | 行内操作:Edit、Delete |

## Setup 列配置

可配置列:Name、Domain、Project、Workspace、Access Level、Tags、Create Time、Operation

按钮:Restore Defaults、Select All、Cancel、Confirm

资源操作契约见 [image-ops.md](../../patterns/image-ops.md). 以下字段只属于容器镜像.

## Upload Image 弹窗

| 字段 | 必填 | 定位方式 | 说明 |
|------|------|--------|------|
| Domain | ❌ | `input`(disabled) | 默认值 "default",不可编辑 |
| Project | ❌ | `input`(disabled) | 当前 Project,不可编辑 |
| Workspace | ✅ | `nz-select` 下拉 | 选择工作空间 |
| Image | ✅ | 文件上传按钮 | `.tar` 或 `.tar.gz` 格式,≤ 2GB |

Workspace 下拉选项以当前环境实时结果为准, 不复用观察环境中的名称。

弹窗按钮:Cancel、Upload

> ⚠️ 帮助文本:"It is recommended to upload a image package made with the container engine client version 1.10.0 or later. The files must be in .tar or .tar.gz formats and their file size must be less than or equal to 2 GB."
> ⚠️ 警告:"If the image version you uploaded already exists, the existing image version will be overwritten, please be careful."

## Push Image 弹窗

两个标签页:**Containerd**(默认)、**Docker**

### Containerd 标签页

操作步骤:

1. 登录安装了 containerd 的节点(root 用户),配置 `/etc/hosts` 映射平台访问地址到仓库域名
2. 上传镜像,执行命令:

```bash
# 标记镜像
sudo ctr -n k8s.io image tag {Image Name}:{Image Tag} hub.ecns.io/{Workspace}/{Image Name}:{Image Tag}

# 推送镜像
sudo ctr -n k8s.io image push -u {token} -k hub.ecns.io/{Workspace}/{Image Name}:{Image Tag}
```

`{token}` 只表示运行时从 UI 或凭据源获取的临时值,不写入 skill 文档、测试
报告或仓库文件。

弹窗按钮:Confirm

## Edit Image 弹窗

| 字段 | 必填 | 定位方式 | 说明 |
|------|------|--------|------|
| Domain | ❌ | `input`(disabled) | 当前域名,不可编辑 |
| Project | ❌ | `input`(disabled) | 当前项目,不可编辑 |
| Workspace | ❌ | `input`(disabled) | 当前工作空间,不可编辑 |
| Name | ❌ | `input`(disabled) | 当前镜像名,不可编辑 |
| Description | ❌ | `textarea` | 支持 Markdown 格式 |

占位符:`"Description content supports Markdown format."`

弹窗按钮:Cancel、Confirm

## Image Details 镜像详情页

URL 格式:`https://<IP>/container-registry/image/{image_name}?workspace={workspace_name}&type=false`

面包屑:Image Management / Detail

### Details Header 详情页头部

| 元素 | 说明 |
|------|------|
| 返回箭头 | 返回镜像列表 |
| 镜像名称 | 三级标题 |
| Refresh | 刷新按钮 |
| More Actions | 下拉菜单 |

### More Actions 菜单

| 操作 |
|------|
| Edit |
| Delete |

### Basic Information 基本信息

| 字段 | 示例值 |
|------|--------|
| Name | alpine |
| Workspace | devops |
| Access Level | Public |
| Tags | 1 |
| Downloads | 4 |
| Space Used | 4.01 MiB |
| Create Time | 16 Jun 2026 at 11:36:18 |
| Domain | Default |
| Project | <CURRENT_PROJECT> |

### Details Tabs 详情页标签页

| 标签 | 定位方式 | 说明 |
|------|--------|------|
| Image Tags | `tab "Image Tags"` | 默认,镜像版本列表 |
| Description | `tab "Description"` | 镜像描述 |

### Image Tags 标签页

工具栏按钮:Refresh、Delete(默认禁用,选中 1+ 行后可用)

表格列:

| 列名 | 可排序 | 说明 |
|------|--------|------|
| (选择框) | ❌ | 全选 checkbox |
| Tag | ✅ | 镜像标签/版本 |
| Size | ✅ | 镜像大小 |
| Image Address | ✅ | 格式:`hub.ecns.io/{workspace}/{image_name}:{tag}` |
| Create Time | ✅ | 创建时间 |
| Operation | ❌ | Delete |

## Pagination 分页

| 项目 | 值 |
|------|-----|
| 默认每页 | 10 条 |
| 总数显示 | "Total N items, last updated..." |
| 翻页 | 上一页/下一页箭头、页码 |
