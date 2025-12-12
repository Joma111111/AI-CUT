复制
# 贡献指南

感谢你考虑为 AICraft 做出贡献！

## 如何贡献

### 报告Bug

如果你发现了Bug，请：

1. 检查 [Issues](https://github.com/yourusername/aicraft-client/issues) 确认问题未被报告
2. 创建新Issue，包含：
   - 清晰的标题
   - 详细的问题描述
   - 复现步骤
   - 预期行为
   - 实际行为
   - 系统环境信息
   - 截图（如果适用）

### 提出功能建议

1. 检查 [Issues](https://github.com/yourusername/aicraft-client/issues) 确认功能未被提出
2. 创建新Issue，标记为 `enhancement`
3. 描述功能的用途和价值
4. 提供使用场景示例

### 提交代码

#### 准备工作

1. Fork项目
2. 克隆你的Fork
3. 创建特性分支

```bash
git checkout -b feature/amazing-feature
开发流程
编写代码
添加测试
运行测试确保通过
更新文档
提交代码
复制
git add .
git commit -m "Add: 添加某某功能"
git push origin feature/amazing-feature
提交信息规范
使用清晰的提交信息：

Add: 添加新功能
Fix: 修复Bug
Update: 更新功能
Refactor: 重构代码
Docs: 更新文档
Test: 添加测试
Style: 代码格式化
创建Pull Request
访问你的Fork
点击 "New Pull Request"
填写PR模板
等待审核
代码规范
遵循 PEP 8
添加类型注解
编写文档字符串
保持代码简洁
添加必要的注释
测试要求
为新功能添加测试
确保所有测试通过
保持测试覆盖率 > 80%
复制
pytest
pytest --cov=.
开发环境
安装开发依赖
复制
pip install -r requirements-dev.txt
代码检查
复制
# 格式化代码
black .

# 代码检查
flake8 .
pylint **/*.py
运行测试
复制
# 运行所有测试
pytest

# 运行特定测试
pytest tests/test_video_analyzer.py

# 生成覆盖率报告
pytest --cov=. --cov-report=html
行为准则
我们的承诺
为了营造开放和友好的环境，我们承诺：

尊重不同的观点和经验
接受建设性的批评
关注对社区最有利的事情
对其他社区成员表示同理心
不可接受的行为
使用性化的语言或图像
人身攻击或侮辱性评论
公开或私下的骚扰
未经许可发布他人的私人信息
其他不道德或不专业的行为
许可证
提交代码即表示你同意将代码以 MIT 许可证发布。

问题？
如有任何问题，请：

查看 文档
搜索 Issues
加入 Discord
发送邮件到 support@yourwebsite.com
再次感谢你的贡献！🎉

复制

---

### `aicraft_client/.github/ISSUE_TEMPLATE/bug_report.md`

```markdown
---
name: Bug报告
about: 创建Bug报告帮助我们改进
title: '[BUG] '
labels: bug
assignees: ''
---

## Bug描述

简洁清晰地描述Bug。

## 复现步骤

1. 打开 '...'
2. 点击 '...'
3. 滚动到 '...'
4. 看到错误

## 预期行为

描述你期望发生什么。

## 实际行为

描述实际发生了什么。

## 截图

如果适用，添加截图帮助解释问题。

## 环境信息

- 操作系统: [例如 Windows 11]
- Python版本: [例如 3.10.5]
- 应用版本: [例如 1.0.0]

## 日志信息
