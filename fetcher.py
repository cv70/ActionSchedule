import html
import time
import feedparser
import requests
import arxiv
from bs4 import BeautifulSoup

from llm import translate

article_max_chars = 1500


def trim_article_content(content):
    content = content.strip()
    return content[:article_max_chars] + '...' if len(content) > article_max_chars else content


def send_request(req_url):
    try:
        resp = requests.get(req_url, timeout=20)
        resp.raise_for_status()
        return resp
    except Exception as e:
        print(f'请求{req_url}失败')
    return None


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
        return send_request("https://hacker-news.firebaseio.com/v0/topstories.json").json()

    def get_item_by_id(item_id):
        return send_request(f"https://hacker-news.firebaseio.com/v0/item/{item_id}.json").json()

    def extract_main_content(url):
        try:
            response = send_request(url)
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
    def get_paper(paper_url):
        return send_request(paper_url)

    # 目标URL
    url = "https://huggingface.co/papers"
    
    try:
        # 发送HTTP请求
        response = send_request(url)
        
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
                title_element = element.select_one('h3 a')
                
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
                paper_resp = get_paper(link)
                paper_soup = BeautifulSoup(paper_resp.content, 'html.parser')
                content_element = paper_soup.find(['p'], class_=lambda x: x and any(keyword in str(x).lower() for keyword in ['text-blue']))
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
                
                time.sleep(1)  # 礼貌延迟
                
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


def fetch_github_trending():
    url = "https://github.com/trending?since=daily"
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    try:
        response = requests.get(url, timeout=20, headers=headers)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        trending_items = []
        
        # 查找所有趋势项目卡片
        # GitHub Trending 页面的项目在 article 标签中，class 为 'Box-row'
        articles = soup.select('article.Box-row')
        
        for article in articles:
            try:
                # 提取项目标题（owner/repo）
                title_element = article.select_one('h2.h3.lh-condensed a')
                if not title_element:
                    continue
                full_title = title_element.get_text(strip=True)
                link = "https://github.com" + title_element['href']
                
                # 提取项目描述
                description_element = article.select_one('p.col-9.color-text-secondary.my-1.pr-4')
                description = description_element.get_text(strip=True) if description_element else ""
                
                # 提取编程语言
                language_element = article.select_one('span[itemprop="programmingLanguage"]')
                language = language_element.get_text(strip=True) if language_element else ""
                
                # 提取星标数
                stars_element = article.select_one('a[href$="/stargazers"]')
                stars = stars_element.get_text(strip=True) if stars_element else "0"
                
                # 提取分叉数
                forks_element = article.select_one('a[href$="/forks"]')
                forks = forks_element.get_text(strip=True) if forks_element else "0"
                
                # 创建项目信息字典
                item = {
                    'source': 'GitHub Trending',
                    'title': full_title,
                    'link': link,
                    'title_cn': translate(full_title),
                    'summary': translate(description),
                    'meta': f'language: {language}, stars: {stars}, forks: {forks}',
                }
                
                trending_items.append(item)
                
            except Exception as e:
                print(f"解析 GitHub 趋势项目时出错: {e}")
                continue
        
        return trending_items
        
    except requests.exceptions.RequestException as e:
        print(f"获取 GitHub Trending 数据失败: {e}")
        return []
    except Exception as e:
        print(f"处理 GitHub Trending 数据时出错: {e}")
        return []
