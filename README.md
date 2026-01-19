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
