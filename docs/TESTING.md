# 测试记录

## 2026-11-05 本地回归

执行者：Codex，在作者的 Windows 本地环境实际执行。

- 源码基线：30df4b16faeb110ae41f7c22599edd9ba7b042f3。
- 环境：Windows / Python 3.13.5 / pytest 9.2.0。
- 使用已有 .venv；本次未执行全新依赖安装。
- 命令：仓库根目录执行 `.venv/Scripts/python -m pytest -v`。
- 原始结果摘要：`collected 7 items`、`7 passed in 9.73s`；退出码 0。

| 用例 | 验证内容 | 结果 |
| --- | --- | --- |
| test_api_payload | 模拟 API 地址、鉴权头、超时与返回文本 | PASS |
| test_api_failure | 模拟 HTTP 401 错误 | PASS |
| test_import | CSV 导入及负数拒绝 | PASS |
| test_privacy | 手机号脱敏与购买意向规则 | PASS |
| test_persistence | 临时数据库持久化 | PASS |
| test_pages | Streamlit AppTest 页面切换无异常 | PASS |
| test_product_to_draft | 人工编辑内容保存为草稿 | PASS |

页面与持久化测试使用临时数据目录，不写入正式用户数据库。

## 本次未验证

- 真实远程模型请求、网络故障与费用；API 测试替换了 requests.post。
- Ollama 服务和实际生成质量。
- EXE 打包、全新 Windows 安装与浏览器人工点击验收。
- XLSX 导入、Excel / Markdown 下载完整性及全部输入边界。
- GitHub Actions 本轮远程执行结果。

通过以上测试只说明已覆盖用例通过，不代表所有功能均已验收。

## 后续记录规范

每次验证记录日期、源码提交、环境、完整命令、结果及未测范围。失败时保留可复现步骤；真实服务与模拟服务结果分别标注。CI 工作流见 [.github/workflows](../.github/workflows/)。
