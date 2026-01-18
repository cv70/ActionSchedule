import html
import json
import feedparser
import requests
from datetime import datetime
from pathlib import Path
import time
import arxiv
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
# Replaced dependency on hn_sdk with direct Hacker News API calls
from bs4 import BeautifulSoup
import random
from google import genai
from google.genai import types
from datetime import datetime, timedelta

yesterday = datetime.now() - timedelta(days=1)
today = yesterday.strftime("%Y-%m-%d")

article_max_chars = 1500

# Gemini settings
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
model = None #genai.Client(api_key=GEMINI_API_KEY)

# Email settings
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


def trim_article_content(content):
    content = content.strip()
    return content[:article_max_chars] + '...' if len(content) > article_max_chars else content


def fetch_arxiv_papers(query, delay=3):
    client = arxiv.Client()
    search = arxiv.Search(
        query=query,
        max_results=10,  # Increase max_results to get more papers
        sort_by=arxiv.SortCriterion.SubmittedDate,
        sort_order=arxiv.SortOrder.Descending
    )
    results = client.results(search)
    papers = []
    
    # 在arxiv论文处理循环中添加翻译字段
    for result in results:
        papers.append({
            "title": result.title,
            "pdf_link": result.pdf_url,
            "translated_title": translate(result.title),
            "translated_summary": translate(result.summary) if hasattr(result, 'summary') else ""
        })
    return papers


def fetch_hacknews_storys():
    def get_top_stories():
        """Return list of top story IDs from Hacker News API"""
        resp = requests.get("https://hacker-news.firebaseio.com/v0/topstories.json", timeout=20)
        resp.raise_for_status()
        return resp.json()

    def get_item_by_id(item_id):
        """Return item JSON for a given Hacker News item id"""
        resp = requests.get(f"https://hacker-news.firebaseio.com/v0/item/{item_id}.json", timeout=20)
        resp.raise_for_status()
        return resp.json()

    def extract_main_content(url):
        try:
            response = requests.get(url, timeout=20, headers={'User-Agent': 'Mozilla/5.0'})
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # 移除无关元素
            for tag in soup(['script', 'style', 'nav', 'footer', 'header', 'aside']):
                tag.decompose()
            
            # 尝试获取正文 - 可根据目标网站调整选择器
            main_content = soup.find('article') or soup.find('main') or soup.find('body')
            text = main_content.get_text(separator='\n', strip=True) if main_content else soup.get_text()
            
            return trim_article_content(text)
        except Exception as e:
            return f"无法提取内容: {e}"

    # 1. 获取首页热门故事的ID列表
    try:
        top_story_ids = get_top_stories()  # 返回ID列表
    except Exception as e:
        print(f"获取热门故事ID失败: {e}")
        return []

    # 2. 根据ID获取故事的详细信息
    storys = []
    for story_id in top_story_ids:
        try:
            story_detail = get_item_by_id(story_id)
            if not story_detail:
                continue
            link = story_detail.get('url', '')
            story_content = extract_main_content(link) if link else ''
            storys.append({
                'source': 'HackNews',
                "title": story_detail.get('title', ''),
                "link": link,
                "title_cn": translate(story_detail.get('title', '')),
                "summary": translate(story_content)
            })
        except Exception as e:
            print(f"处理 story_id {story_id} 出错: {e}")
            continue

    return storys


def fetch_techcrunch_rss():
    rss_url = "https://techcrunch.com/feed/"
    feed = feedparser.parse(rss_url)
    
    articles = []
    print(len(feed.entries))
    for entry in feed.entries:        
        article = {
            'source': 'TechCrunch',
            'title': entry.title,
            'link': entry.link,
            'title_cn': translate(entry.title),
            'summary': translate(html.unescape(entry.summary)),
        }
        articles.append(article)
        # time.sleep(1)  # 礼貌延迟
    
    return articles


def fetch_huggingface_papers():
    # 目标URL
    url = "https://huggingface.co/papers"
    
    # 设置请求头，模拟浏览器访问
    try:
        # 发送HTTP请求
        response = requests.get(url, timeout=20, headers={'User-Agent': 'Mozilla/5.0'})
        response.raise_for_status()  # 检查请求是否成功
        
        print(response.content)

        # 使用BeautifulSoup解析HTML
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # 初始化结果列表
        papers = []
        
        # 查找包含论文信息的元素
        # 根据页面结构，论文条目通常在<article>标签或特定class的<div>中
        # 这里使用更通用的选择器，可能需要根据实际页面结构调整
        paper_elements = soup.find_all('article')
        
        # 如果找不到<article>标签，尝试其他选择器
        if not paper_elements:
            paper_elements = soup.select('[data-target="paper-card"]')
        
        # 如果还找不到，尝试查找具有论文特征的div
        if not paper_elements:
            paper_elements = soup.select('div[class*="paper"], div[class*="card"]')
        
        # 提取每个论文的信息
        for i, element in enumerate(paper_elements):
            try:
                # 提取论文标题
                title_element = element.find(['h1'])
                
                title = title_element.get_text(strip=True) if title_element else ""
                
                # 提取论文链接
                link_element = element.find('a', href=True)
                if link_element:
                    link = link_element['href']
                    # 确保链接完整
                    if link.startswith('/'): 
                        link = f"https://huggingface.co{link}"
                else:
                    link = ""
                
                # 提取论文摘要/内容
                content_element = element.find(['p'], class_=lambda x: x and any(keyword in str(x).lower() for keyword in ['text-blue']))
                if not content_element:
                    # 尝试查找第一个段落
                    content_element = element.find('p')
                
                content = content_element.get_text(strip=True) if content_element else ""
                
                # 创建论文信息字典
                paper_info = {
                    'source': 'HuggingFace',
                    'title': title,
                    'link': link,
                    'title_cn': translate(title),
                    'summary': translate(content),
                }
                
                papers.append(paper_info)
                
                # time.sleep(1)  # 礼貌延迟
                
            except Exception as e:
                print(f"  处理第 {i+1} 个论文元素时出错: {str(e)}")
                continue
        
        
        return papers
        
    except requests.exceptions.RequestException as e:
        print(f"网络请求出错: {e}")
        return []
    except Exception as e:
        print(f"程序执行出错: {e}")
        return []


def translate(text):
    if text:
        text = text.strip()
    if not text:
        return ''
    return text
    try:
        system_instruction = "你是一位专业、严谨的学术翻译助手，翻译时严格保留专业术语和原文风格。"
        prompt = f"{system_instruction}\n请将以下学术内容准确翻译为中文：\n{text}"
        response = model.generate_content(prompt, genai.GenerationConfig(temperature=0.3))
        return response.text
    except Exception as e:
        print(f"翻译失败: {str(e)}")
        return text + " [翻译失败]"  # 返回原文前100字符+错误标记


def send_email(subject, body):
    msg = MIMEMultipart()
    msg['From'] = SMTP_USERNAME
    msg['To'] = EMAIL_RECIPIENT
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    server = smtplib.SMTP(SMTP_SERVER)
    server.starttls()
    server.login(SMTP_USERNAME, SMTP_PASSWORD)
    text = msg.as_string()
    server.sendmail(SMTP_USERNAME, EMAIL_RECIPIENT, text)
    server.quit()


def main():
    # query = "cs.NE OR cs.MA OR cs.LG OR cs.CV OR cs.CL OR cs.AI"

    # arxiv_papers = get_arxiv_papers(query)

    # hacknews_storys = fetch_hacknews_storys()
    # print(hacknews_storys)

    huggingface_papers = fetch_huggingface_papers()

    # total = len(arxiv_papers) + len(hacknews_storys) + len(huggingface_papers)
    # random_quote = random.choice(FAMOUS_QUOTES)
    print(huggingface_papers)

    # subject = "Articles Update"
    # body = f"Today, we have collected {total} articles.\n\n" 
    #        f"New papers have been updated. Check the website for details.\n\n" 
    #        f"{random_quote}"

    # Send email notification
    # send_email(subject, body)

if __name__ == "__main__":
    main()
