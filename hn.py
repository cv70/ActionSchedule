# 安装：pip install hn-sdk
from bs4 import BeautifulSoup
from hn_sdk.client.v0.client import get_top_stories, get_item_by_id

import requests


def extract_main_content(url):
    try:
        response = requests.get(url, timeout=10, headers={'User-Agent': 'Mozilla/5.0'})
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # 移除无关元素
        for tag in soup(['script', 'style', 'nav', 'footer', 'header', 'aside']):
            tag.decompose()
        
        # 尝试获取正文 - 可根据目标网站调整选择器
        main_content = soup.find('article') or soup.find('main') or soup.find('body')
        text = main_content.get_text(separator='\n', strip=True) if main_content else soup.get_text()
        
        # 截取前5000字符作为摘要
        chars = 5000
        return text[:chars] + '...' if len(text) > chars else text
    except Exception as e:
        return f"无法提取内容: {e}"


# 1. 获取首页热门故事的ID列表
top_story_ids = get_top_stories()  # 返回ID列表
print(f"热门故事ID: {top_story_ids[:min(len(top_story_ids), 10)]}")

# 2. 根据ID获取某个故事的详细信息
story_id = top_story_ids[0]  # 取第一个故事
story_detail = get_item_by_id(story_id)
print(f"故事标题: {story_detail['title']}")
print(f"故事链接: {story_detail.get('url', '无外部链接')}")
print(f"作者: {story_detail['by']}")

print(story_detail)


c = extract_main_content("https://disconnect.blog/escaping-the-trap-of-us-tech-dependence/")
print(c)