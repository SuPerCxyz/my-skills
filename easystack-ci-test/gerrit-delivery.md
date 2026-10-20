# Gerrit Delivery

## Handoff And Authorization 转接与授权

本文件只定义 CI 结束后的交付转接, 不执行 amend 或上传, 不维护另一套 Git 命令.
CI 通过不授权 Git 写入, 测试或修复授权也不能推导 commit、amend 或远程操作权限.

1. 报告实际 CI 范围、代码版本、cover/pep8 结果和未验证项. 修改后必须使用对应新结果,
   不沿用旧结果或把仓库 CI 通过当作资源功能验收.
2. 用户明确要求交付后, EasyStack 公司项目先读取
   [项目默认值与交付约定](../easystack-workflow/project-relationships.md),
   再进入 [git-delivery](../git-delivery/SKILL.md). 独立分发时按当前环境实际发现能力定位,
   不假设相邻目录或已安装状态; 不可获取时说明缺口, 不猜测默认身份或命令.
3. 向交付能力传递本次目标、已有修改、授权动作和实际 CI 证据.
   由它核对当前提交、新建 Change 或原 Change 更新、最终 Author/Committer、原 Change-Id、
   真实 remote 和目标分支, 并仅执行用户实际授权的操作.

公司评审站点不代替 Git remote. 目标分支不能省略或仅由本地分支名猜测;
目标不明确时由交付能力说明缺口, 不自行运行上传命令.
最终分别报告实际 Git 操作和成功/失败状态, 仅使用真实取得的 Change 链接.
