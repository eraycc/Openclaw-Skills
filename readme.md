# Openclaw-Skills 技能备份库

这是一个个人使用的Openclaw技能备份仓库。本仓库中的所有技能均为自用备份用途。（部分skill来自互联网）

## 📦 安装方法

如需安装本仓库中的任何技能，只需将对应的下载链接发送给Openclaw，让AI帮你自动完成安装。例如：

> "请帮我下载解压后安装这个技能："
> ```
> https://raw.githubusercontent.com/eraycc/Openclaw-Skills/refs/heads/main/All-skills-zip/skill-security-auditor.tar.gz
> ```

Openclaw会自动处理技能的下载、解压和安装过程。

## 📚 当前技能汇总

| 技能名称 | 功能描述 |
|---------|---------|
| **Agent Browser** | 基于Rust构建的高速无头浏览器自动化工具（支持Node.js备用），通过结构化命令让AI代理能够导航、点击、输入和截图页面。 |
| **clawddocs** | Clawdbot文档专家，提供决策树导航、搜索脚本、文档获取、版本追踪以及所有Clawdbot功能的配置代码片段。 |
| **find-skills** | 当用户询问"如何做某事"、"寻找某个技能"、"是否有技能可以..."或表示想要扩展功能时，帮助用户发现和安装相应的技能。 |
| **multi-search-engine** | 集成17个搜索引擎的多引擎搜索工具（8个中文 + 9个全球）。支持高级搜索运算符、时间过滤、站内搜索、隐私搜索引擎和WolframAlpha知识查询。无需API密钥。 |
| **openclaw-file-exporter** | 导出OpenClaw配置文件、技能或其他文件并上传至tmpfile.link供下载。自动压缩文件，提供格式化的下载链接和文件详情。 |
| **pua** | 强制进行穷举式问题解决，采用职场PUA话术风格。在任务多次失败、准备放弃、建议手动操作、陷入循环、行为被动或用户表达 frustration 时触发。 |
| **self-improvement** | 记录学习经验、错误和修正，实现持续改进。适用于命令执行失败、用户纠正、请求不存在的功能、外部API故障、知识过时或发现更好的解决方案等场景。 |
| **skill-security-auditor** | 面向AI代理的安全优先技能审查工具（v2.0.0）。在从ClawdHub、GitHub或其他来源安装任何技能前使用。检查危险信号、权限范围、可疑模式和恶意代码。安全技能自动安装；可疑/不安全技能需用户批准。 |
| **tavily-search** | 通过Tavily API进行AI优化的网络搜索。为AI代理返回简洁、相关的结果。需要配置TAVILY_API_KEY环境变量。 |
| **terminal-mode** | 终端模拟模式，当用户说"打开终端"、"进入终端模式"、"模拟终端"、"terminal mode"或类似表达时触发。提供类似Linux终端的交互体验，支持cd、ls、cat、pwd、mv、cp、rm、touch、mkdir、rmdir、find、grep、head、tail、chmod等常用命令，用于浏览和操作用户文件系统。支持带参数的命令如"ls -la"、"ls -lath"等。 |
| **blogwatcher** | 监控博客和RSS/Atom订阅源更新，使用blogwatcher CLI。 |
| **rss-ai-reader** |   📰 RSS AI 阅读器 — 自动抓取订阅、LLM生成摘要、多渠道推送！
  支持 Claude/OpenAI 生成中文摘要，推送到飞书/Telegram/Email。
  触发条件: 用户要求订阅RSS、监控博客、抓取新闻、生成摘要、设置定时抓取、
  "帮我订阅"、"监控这个网站"、"每天推送新闻"、RSS/Atom feed 相关。 |
| **z-image-turbo-generator** | 使用tongyi-mai/z-image-turbo通过hugging face推理提供者生成图像，使用用户提供的hugging face API密钥。当用户希望ChatGPT从提示中创建图像并使用此固定模型时使用，尤其是当用户提及z-image-turbo、hugging face API密钥、hf令牌、负面提示、随机数种子、图像大小或希望仅输出图像时。如果当前对话中缺少hugging face API密钥，则请求该密钥，然后运行捆绑的脚本，除非用户明确要求设置或调试细节，否则仅返回生成的图像。 |

## 🛡️ 安全提示

本仓库作为个人技能备份使用。建议在安装任何来源的技能前，始终使用 `skill-security-auditor` 进行检查，确保技能的安全性和可靠性。

## 🔧 技能依赖说明

部分技能可能有特定的运行要求：
- **环境变量**：某些技能需要配置API密钥或其他环境变量（例如 `tavily` 需要 `TAVILY_API_KEY`）
- **依赖程序**：部分技能可能需要特定的程序支持，如Node.js

具体依赖请参考各个技能的元数据说明。

---

*本仓库仅供个人备份使用*