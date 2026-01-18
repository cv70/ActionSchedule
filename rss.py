import html
import feedparser
from datetime import datetime, timedelta
import time

def fetch_techcrunch_rss(max_results=10):
    """
    从TechCrunch官方RSS获取最新文章
    """
    rss_url = "https://techcrunch.com/feed/"
    feed = feedparser.parse(rss_url)
    
    articles = []
    print(len(feed.entries))
    for entry in feed.entries[:max_results]:
        # 提取发布日期并转换为datetime对象
        published_time = datetime(*entry.published_parsed[:6])
        
        article = {
            'source': 'TechCrunch',
            'title': entry.title,
            'link': entry.link,
            'summary': html.unescape(entry.summary) if 'summary' in entry else '',
            'published': published_time,
            'author': entry.author if 'author' in entry else '未知'
        }
        articles.append(article)
    
    return articles


# 使用示例
if __name__ == "__main__":
    s = 'STEP3-VL-10B achieves superior multimodal performance through unified pre-training with a language-aligned Perception Encoder and Qwen3-8B decoder, combined with scaled post-training and Parallel Coordinated Reasoning for efficient large-scale visual reasoning.'
    print(len(s))
    print("获取TechCrunch最新文章...")
    tc_articles = fetch_techcrunch_rss(5)
    for article in tc_articles:
        print(f"标题: {article['title']}")
        print(f"链接: {article['link']}")
        print(f"发布时间: {article['published']}")
        print(article['summary'])
        print("-" * 50)
    
    time.sleep(2)  # 礼貌延迟
    


    # print("获取The Information最新文章...")
    # ti_articles = fetch_techcrunch_rss(5)
    # for article in ti_articles:
    #     print(f"标题: {article['title']}")
    #     print(f"链接: {article['link']}")
    #     print(f"发布时间: {article['published']}")
    #     print(article['summary'])
    #     print("-" * 50)
