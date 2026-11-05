# 项目目录与文档索引

返回 [项目首页](../README.md)。

| 路径 | 职责 |
| --- | --- |
| app.py | Streamlit 应用入口 |
| jiemian.py | 页面与用户交互 |
| hexin.py | 表格导入、评论规则、脱敏、模型请求与 Excel 导出 |
| shujuku.py | SQLite 数据读写 |
| peizhi.py | 配置与数据路径 |
| qidong.py | 本地服务启动与浏览器打开 |
| dabao.ps1 | Windows 打包 |
| shouji_xuke.py | 第三方许可证收集 |
| requirements.txt | 固定版本依赖 |
| ceshi/ | 核心逻辑、模型请求模拟、页面与草稿流程测试 |
| .github/workflows/ | GitHub Actions 自动检查 |
| docs/ | 文档索引与测试记录 |

## 阅读顺序

1. [README](../README.md)：能力与边界。
2. [使用说明](../使用说明.md)：实际操作与故障排查。
3. [测试记录](TESTING.md)：复现验证。
4. [更新日志](../CHANGELOG.md)：变更历史。

本地生成的 .venv、build、dist、缓存和数据库不作为源码目录发布。
