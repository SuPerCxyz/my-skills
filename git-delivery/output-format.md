# Output Format 最终输出格式

执行结束后的回复应简洁, 优先报告结果, 不展示完整内部推理。至少包含:

```text
项目类型: company-gerrit 或 personal-git
提交范围: <本次提交涉及的逻辑范围>
提交方式: new commit / amend / git review
Commit: <SHA 前 12 位或未执行>
远程操作: <git review 结果 / push 结果 / 未执行>
验证: <已执行的验证>
未验证项: <无法执行的验证>
风险或阻塞: <已知风险或阻塞, 无则省略>
```

## 公司项目补充

- 判断为公司项目的主要依据
- Gerrit 目标分支
- 是新 Change 还是原 Change 的新 Patch Set
- 是否实际执行 `git review -R -r origin <branch>`

## 个人项目补充

- 是新提交还是 amend
- 是否实际执行 push
- push 使用的 remote 和 branch

## 诚实报告

不得声称没有执行过的操作已经完成。正常成功提交后的报告应保持简短, 只有出现
以下情况时才展开:

- 项目类型识别冲突
- staged diff 包含无关文件
- 目标分支无法确定
- 多个 Gerrit Change 混在提交栈中
- 应更新的 Change 不是 `HEAD`
- 测试失败
- Gerrit 上传失败
- 权限或 Change-Id 错误
- 可能需要 rebase 或历史改写
- 发现敏感信息
