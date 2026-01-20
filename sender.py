from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os
import random
import requests
import smtplib

from config import Config


SMTP_SERVER = "smtp.qq.com"
SMTP_USERNAME = os.getenv('SMTP_USERNAME')
SMTP_PASSWORD = os.getenv('SMTP_PASSWORD')
EMAIL_RECIPIENT = os.getenv('EMAIL_RECIPIENT')

# List of famous quotes
FAMOUS_QUOTES = [
    "The only way to do great work is to love what you do. - Steve Jobs",
    "Believe you can and you're halfway there. - Theodore Roosevelt",
    "Success is not final, failure is not fatal: It is the courage to continue that counts. - Winston S. Churchill",
    "The best way to predict the future is to invent it. - Alan Kay",
    "Do not wait to strike till the iron is hot; but make it hot by striking. - William Butler Yeats"
]

class Sender:
    def __init__(self, config: Config):
        self.config = config

    def send(self, articles, report):
        html_content = None
        markdown_content = None

        if self.config.PUSH_ENDPOINT_EMAIL in self.config.PUSH_ENDPOINT:
            if not html_content:
                html_content = self.build_html_content(articles, report)
            self.send_email(html_content)
        
        if self.config.PUSH_ENDPOINT_WECHAT in self.config.PUSH_ENDPOINT:
            if not markdown_content:
                markdown_content = self.build_markdown_content(articles, report)
            self.send_wechat_message(markdown_content)


    def send_email(self, body):
        try:
            msg = MIMEMultipart()
            msg['From'] = self.config.SMTP_SENDER
            msg['To'] = self.config.SMTP_RECEIVER
            msg['Subject'] = 'Tech Insight'
            msg.attach(MIMEText(body, 'html'))

            server = smtplib.SMTP(self.config.SMTP_SERVER)
            server.starttls()
            server.login(self.config.SMTP_SENDER, self.config.SMTP_PASSWORD)
            text = msg.as_string()
            server.sendmail(self.config.SMTP_SENDER, self.config.SMTP_RECEIVER, text)
            server.quit()
        except Exception as e:
            print(f"邮件发送失败: {e}")


    def send_wechat_message(self, markdown_content):
        if not self.config.WECHAT_WEBHOOK_URL:
            return
        
        payload = {
            "msgtype": "markdown",
            "markdown": {
                "content": markdown_content
            }
        }
        
        try:
            response = requests.post(self.config.WECHAT_WEBHOOK_URL, json=payload, timeout=30)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            print(f"微信消息发送失败: {e}")


    def build_html_content(self, articles, report):
        html_content = """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; line-height: 1.6; color: #333; max-width: 800px; margin: 0 auto; padding: 20px; }
                .article { border-left: 4px solid #4A90E2; background-color: #f8f9fa; padding: 20px; margin-bottom: 25px; border-radius: 0 8px 8px 0; box-shadow: 0 2px 5px rgba(0,0,0,0.05); }
                .article-header { border-bottom: 1px solid #eaeaea; padding-bottom: 10px; margin-bottom: 15px; }
                .source { display: inline-block; background-color: #e9ecef; color: #495057; font-size: 0.85em; padding: 3px 10px; border-radius: 12px; margin-bottom: 8px; }
                .title { font-size: 1.4em; font-weight: bold; color: #2c3e50; margin: 5px 0; }
                .title-cn { font-size: 1.1em; color: #7f8c8d; font-style: italic; margin-bottom: 10px; }
                .link a { display: inline-block; background-color: #4A90E2; color: white !important; text-decoration: none; padding: 8px 15px; border-radius: 5px; font-size: 0.9em; margin: 10px 0; }
                .link a:hover { background-color: #357ABD; }
                .meta-info { color: #666; font-size: 0.9em; margin: 10px 0 15px 0; padding: 8px 0; font-family: 'Courier New', monospace; }
                .summary { background-color: #fff; padding: 15px; border-radius: 5px; border: 1px solid #eee; font-size: 0.95em; color: #555; }
                .summary h4 { color: #4A90E2; margin-top: 0; border-bottom: 1px dashed #ddd; padding-bottom: 5px; }
                .separator { height: 1px; background: linear-gradient(to right, transparent, #ddd, transparent); margin: 30px 0; }
            </style>
        </head>
        <body>
            <h2 style="color: #2c3e50; text-align: center;">📚 今日趋势洞察速递</h2>
            <p style="text-align: center; color: #7f8c8d;">筛选了 <strong>{count}</strong> 篇精选文章, {quote}</p>
            <p style="text-align: center; color: #7f8c8d;">{report}</p>
        """

        # 替换文章数量占位符
        html_content = html_content.replace('{count}', str(len(articles)))
        random_quote = random.choice(FAMOUS_QUOTES)
        html_content = html_content.replace('{quote}', random_quote)
        html_content = html_content.replace('{report}', report)

        for index, article in enumerate(articles):
            # 构建单篇文章的HTML块
            article_html = """
            <div class="article">
                <div class="article-header">
            """
            
            # 来源
            if 'source' in article:
                article_html += f'<div class="source">📌 {article["source"]}</div>'

            # 标题
            title_html = ''
            if 'title' in article:
                title_html = f'<div class="title">{article["title"]}</div>'
            
            # 中文标题
            if 'title_cn' in article:
                title_html += f'<div class="title-cn">{article["title_cn"]}</div>'
            
            article_html += title_html + '</div>'  # 关闭 article-header
            
            # 链接
            if 'link' in article:
                # 使用更友好的链接文字
                article_html += f'<div class="link"><a href="{article["link"]}" target="_blank">阅读全文 →</a></div>'

            # Meta 信息标签
            if 'meta' in article:
                article_html += f'<div class="meta-tag">📊 {article["meta"]}</div>'

            # 摘要
            if 'summary' in article:
                summary = article['summary']
                # 将纯文本的换行转换为HTML换行
                summary = summary.replace('\n', '<br>')
                article_html += f"""
                <div class="summary">
                    <h4>✍️ 核心摘要</h4>
                    {summary}
                </div>
                """
            
            article_html += "</div>"  # 关闭 article
            
            # 在文章间添加分隔线（除了最后一篇）
            if index < len(articles) - 1:
                article_html += '<div class="separator"></div>'
            
            html_content += article_html

        # 闭合HTML
        html_content += f"""
        </body>
        </html>
        """
        
        return html_content


    def build_markdown_content(self, articles, report):
        # 构建头部
        markdown_content = f"# 📚 今日趋势洞察速递\n\n"
        markdown_content += f"筛选了 {len(articles)} 篇精选文章, \"{random.choice(FAMOUS_QUOTES)}\"\n\n"
        markdown_content += f"{report}\n\n"
        
        # 遍历每篇文章
        for index, article in enumerate(articles):
            # 添加文章标题和来源
            markdown_content += f"## 📌 {article.get('source', '未知来源')}\n"
            
            if 'title' in article:
                markdown_content += f"### {article['title']}\n"
            
            # 添加中文标题（如果存在）
            if 'title_cn' in article:
                markdown_content += f"**中文标题**：{article['title_cn']}\n\n"
            
            # 添加链接（如果存在）
            if 'link' in article:
                markdown_content += f"[阅读全文 →]({article['link']})\n\n"
            
            # 添加元信息（如果存在）
            if 'meta' in article:
                markdown_content += f"📊 {article['meta']}\n\n"
            
            # 添加摘要（如果存在）
            if 'summary' in article:
                summary = article['summary']
                # 将纯文本换行转换为 Markdown 换行（两个空格 + 换行）
                summary_lines = summary.split('\n')
                summary_markdown = '\n  '.join(summary_lines)  # 用两个空格实现换行
                markdown_content += f"✍️ **核心摘要**:\n\n  {summary_markdown}\n\n"
            
            # 在文章间添加分隔线（除了最后一篇）
            if index < len(articles) - 1:
                markdown_content += "---\n\n"
        
        return markdown_content
