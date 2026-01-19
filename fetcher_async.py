import html
import time
import feedparser
import requests
import arxiv
from bs4 import BeautifulSoup
import asyncio
from concurrent.futures import ThreadPoolExecutor
from typing import List, Dict, Any

from llmanger import LLManager

article_max_chars = 3000


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


class AsyncFetcher():
    def __init__(self, llmanager: LLManager):
        self.llmanager = llmanager
        # 使用线程池处理同步的LLM调用
        self.executor = ThreadPoolExecutor(max_workers=10)

    async def fetch_arxiv_papers(self, query, limit=5):
        """异步获取arXiv论文，但翻译仍同步（因OpenAI客户端非异步）"""
        client = arxiv.Client()
        search = arxiv.Search(
            query=query,
            max_results=limit,
            sort_by=arxiv.SortCriterion.SubmittedDate,
            sort_order=arxiv.SortOrder.Descending
        )
        results = list(client.results(search))
        results = results[:min(len(results), limit)]

        # 使用线程池并发执行翻译
        tasks = [
            asyncio.get_event_loop().run_in_executor(
                self.executor, 
                self.llmanager.translate, 
                result.title
            ) for result in results
        ]
        translated_titles = await asyncio.gather(*tasks)
        
        tasks = [
            asyncio.get_event_loop().run_in_executor(
                self.executor,
                self.llmanager.translate,
                result.summary if hasattr(result, 'summary') else ""
            ) for result in results
        ]
        translated_summaries = await asyncio.gather(*tasks)
        
        papers = []
        for i, result in enumerate(results):
            papers.append({
                "title": result.title,
                "pdf_link": result.pdf_url,
                "translated_title": translated_titles[i],
                "translated_summary": translated_summaries[i]
            })
        return papers


    async def fetch_hacknews_storys(self, limit=5):
        def get_top_stories():
            return send_request("https://hacker-news.firebaseio.com/v0/topstories.json").json()

        def get_item_by_id(item_id):
            return send_request(f"https://hacker-news.firebaseio.com/v0/item/{item_id}.json").json()

        def extract_main_content(url):
            try:
                response = send_request(url)
                soup = BeautifulSoup(response.content, 'html.parser')
                
                for tag in soup(['script', 'style', 'nav', 'footer', 'header', 'aside']):
                    tag.decompose()
                
                main_content = soup.find('article') or soup.find('main') or soup.find('body')
                text = main_content.get_text(separator='\n', strip=True) if main_content else soup.get_text()
                
                return trim_article_content(text)
            except Exception as e:
                return f"无法提取内容: {e}"

        try:
            top_story_ids = get_top_stories()
        except Exception as e:
            print(f"获取热门故事ID失败: {e}")
            return []

        top_story_ids = top_story_ids[:min(len(top_story_ids), limit)]

        # 并发获取故事详情和内容
        async def fetch_story(story_id):
            try:
                story_detail = get_item_by_id(story_id)
                if not story_detail:
                    return None
                link = story_detail.get('url', '')
                story_content = extract_main_content(link) if link else ''
                
                # 异步翻译
                title_task = asyncio.get_event_loop().run_in_executor(
                    self.executor, self.llmanager.translate, story_detail.get('title', '')
                )
                summary_task = asyncio.get_event_loop().run_in_executor(
                    self.executor, self.llmanager.translate, story_content
                )
                
                title_cn, summary_cn = await asyncio.gather(title_task, summary_task)
                
                return {
                    'source': 'HackNews',
                    "title": story_detail.get('title', ''),
                    "link": link,
                    "title_cn": title_cn,
                    "summary": summary_cn
                }
            except Exception as e:
                print(f"处理 story_id {story_id} 出错: {e}")
                return None

        tasks = [fetch_story(story_id) for story_id in top_story_ids]
        storys = [story for story in await asyncio.gather(*tasks) if story is not None]
        return storys


    async def fetch_techcrunch_rss(self, limit=5):
        rss_url = "https://techcrunch.com/feed/"
        feed = feedparser.parse(rss_url)
        entries = feed.entries[:min(len(feed.entries), limit)]

        # 并发翻译标题和摘要
        async def process_entry(entry):
            title_task = asyncio.get_event_loop().run_in_executor(
                self.executor, self.llmanager.translate, entry.title
            )
            summary_task = asyncio.get_event_loop().run_in_executor(
                self.executor, self.llmanager.translate, html.unescape(entry.summary)
            )
            title_cn, summary_cn = await asyncio.gather(title_task, summary_task)
            return {
                'source': 'TechCrunch',
                'title': entry.title,
                'link': entry.link,
                'title_cn': title_cn,
                'summary': summary_cn,
            }

        tasks = [process_entry(entry) for entry in entries]
        articles = await asyncio.gather(*tasks)
        return articles


    async def fetch_huggingface_papers(self, limit=5):
        def get_paper(paper_url):
            return send_request(paper_url)

        url = "https://huggingface.co/papers"
        
        try:
            response = send_request(url)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            paper_elements = soup.find_all('article')
            if not paper_elements:
                paper_elements = soup.select('[data-target="paper-card"]')
            if not paper_elements:
                paper_elements = soup.select('div[class*="paper"], div[class*="card"]')
            
            paper_elements = paper_elements[:min(len(paper_elements), limit)]
            
            async def process_paper(element):
                try:
                    title_element = element.select_one('h3 a')
                    title = title_element.get_text(strip=True) if title_element else ""
                    
                    link_element = element.find('a', href=True)
                    link = link_element['href'] if link_element else ""
                    if link.startswith('/'):
                        link = f"https://huggingface.co{link}"
                    
                    paper_resp = get_paper(link)
                    paper_soup = BeautifulSoup(paper_resp.content, 'html.parser')
                    content_element = paper_soup.find(['p'], class_=lambda x: x and any(keyword in str(x).lower() for keyword in ['text-blue']))
                    if not content_element:
                        content_element = element.find('p')
                    content = content_element.get_text(strip=True) if content_element else ""
                    
                    title_task = asyncio.get_event_loop().run_in_executor(
                        self.executor, self.llmanager.translate, title
                    )
                    summary_task = asyncio.get_event_loop().run_in_executor(
                        self.executor, self.llmanager.translate, content
                    )
                    title_cn, summary_cn = await asyncio.gather(title_task, summary_task)
                    
                    return {
                        'source': 'HuggingFace',
                        'title': title,
                        'link': link,
                        'title_cn': title_cn,
                        'summary': summary_cn,
                    }
                except Exception as e:
                    print(f"处理论文元素时出错: {str(e)}")
                    return None

            tasks = [process_paper(element) for element in paper_elements]
            papers = [paper for paper in await asyncio.gather(*tasks) if paper is not None]
            return papers
            
        except Exception as e:
            print(f"程序执行出错: {e}")
            return []


    async def fetch_github_trending(self, limit=5):
        url = "https://github.com/trending?since=daily"
        headers = {'User-Agent': 'Mozilla/5.0'}
        
        try:
            response = requests.get(url, timeout=20, headers=headers)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            articles = soup.select('article.Box-row')[:min(len(soup.select('article.Box-row')), limit)]

            async def process_article(article):
                try:
                    title_element = article.select_one('h2.h3.lh-condensed a')
                    if not title_element:
                        return None
                    full_title = title_element.get_text(strip=True)
                    link = "https://github.com" + title_element['href']
                    
                    description_element = article.select_one('p.col-9.color-text-secondary.my-1.pr-4')
                    description = description_element.get_text(strip=True) if description_element else ""
                    
                    language_element = article.select_one('span[itemprop="programmingLanguage"]')
                    language = language_element.get_text(strip=True) if language_element else ""
                    
                    stars_element = article.select_one('a[href$="/stargazers"]')
                    stars = stars_element.get_text(strip=True) if stars_element else "0"
                    
                    forks_element = article.select_one('a[href$="/forks"]')
                    forks = forks_element.get_text(strip=True) if forks_element else "0"
                    
                    title_task = asyncio.get_event_loop().run_in_executor(
                        self.executor, self.llmanager.translate, full_title
                    )
                    summary_task = asyncio.get_event_loop().run_in_executor(
                        self.executor, self.llmanager.translate, description
                    )
                    title_cn, summary_cn = await asyncio.gather(title_task, summary_task)
                    
                    return {
                        'source': 'GitHub Trending',
                        'title': full_title,
                        'link': link,
                        'title_cn': title_cn,
                        'summary': summary_cn,
                        'meta': f'language: {language}, stars: {stars}, forks: {forks}',
                    }
                except Exception as e:
                    print(f"解析 GitHub 趋势项目时出错: {e}")
                    return None

            tasks = [process_article(article) for article in articles]
            trending_items = [item for item in await asyncio.gather(*tasks) if item is not None]
            return trending_items
            
        except Exception as e:
            print(f"处理 GitHub Trending 数据时出错: {e}")
            return []
