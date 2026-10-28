# Readme

以下测试只使用本地临时文件和最小 DOM fixture, 不连接浏览器或云环境, 不调用模型.
测试直接提取当前文档中的 helper/示例并执行, 不维护另一套资源选择或结果实现.

| 文件 | 覆盖 |
|---|---|
| [test_validate_patterns.py](test_validate_patterns.py) | 校验器真实行为、动态结果漏例、嵌套对象、配置读取脱敏和实际 CLI |
| [test-ui-examples.cjs](test-ui-examples.cjs) | 精确项目/名称/UUID、选择集合、按钮映射、真实删除示例、32/36 位项目 ID、异步项目切换及全部 JS 示例语法 |

从 skill 目录运行, 需要已有 Python 3 和 Node.js, 缺失时报告而不自动安装:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -p 'test_*.py'
node --test tests/test-ui-examples.cjs
PYTHONDONTWRITEBYTECODE=1 python3 scripts/validate-patterns.py
```

Python 测试使用自动清理的唯一 `/tmp` fixture; 配置测试不会读取或修改真实环境文件.
Node fixture 只模拟 DOM 观察值和点击反馈. Angular 事件、权限、配额、后端异步、
实际数据校验及当前平台页面兼容性仍需真实 UI 场景验证, 不能由这些结果授予
`ready-validated`. 校验器支持文档中的 JS/JSON 对象记法, 不是任意 JavaScript
解释器或真实业务效果证明.
