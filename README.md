# ActionSchedule

一个基于 GitHub Actions 的自动化趋势洞察系统，每日定时抓取 arXiv、HackNews、 HuggingFace Papers、TechCrunch、GithubTrending 的最新文章，通过 AI 摘要与多源聚合，生成面向技术开发者与商业决策者的深度趋势洞察报告，并自动推送至邮箱

> 📬 从此，每天清晨，AI 为您阅读世界，提炼趋势

## 工作流程

```mermaid
graph TD
    A[每日定时触发<br>GitHub Actions] --> B[抓取 arXiv 最新论文]
    A --> C[抓取 HackNews 热门文章]
    A --> D[抓取 HuggingFace Papers 最新论文]
    A --> E[抓取 TechCrunch 最新文章]
    A --> F[抓取 Github Trending 最新项目]
    B --> G[AI 摘要生成<br>（使用 LLM 提取核心观点）]
    C --> G
    D --> G
    E --> G
    F --> G
    G --> H[聚合多个摘要（去重、归类、关联）]
    H --> I[生成趋势洞察报告（技术动向 + 商业机会）]
    I --> J[通过 SMTP 发送至邮箱]
```

## 使用说明
1. Fork 本项目
2. 配置环境变量，使用Actions secrets
环境变量说明：
- `GPT_API_KEY`：OpenAI API 密钥
- `GPT_API_URL`：OpenAI API URL
- `GPT_MODEL`：使用的 大语言模型
- `SMTP_SERVER`：SMTP 服务器地址（比如 QQ 邮箱是 `smtp.qq.com`）
- `SMTP_SENDER`：发件人
- `SMTP_PASSWORD`：SMTP 密码（比如QQ 邮箱是对应的授权码）
- `SMTP_RECEIVER`：收件人
- `WECHAT_WEBHOOK_URL`：企业微信机器人 webhook 地址（可选）
- `PUSH_ENDPOINT`：推送目标，可选值`email,wechat`，使用 `,` 分隔
- `FETCH_LIMIT`：每个数据源的抓取数量，默认 `5`
- `SUBSCRIPTION_SOURCES`：订阅的数据源，可选值`arxiv,hacker_news,huggingface_papers,tech_crunch,github_trending`，使用 `,` 分隔
3. 启用 GitHub Actions

## 📝 贡献指南

欢迎提交 Issue 和 Pull Request 来改进本项目！

## 📄 许可证

本项目采用 Apache-2.0 许可证，详情请见 [LICENSE](./LICENSE-APACHE) 文件。
