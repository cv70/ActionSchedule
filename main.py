from datetime import datetime
from datetime import datetime, timedelta
from random import random

from fetcher import Fetcher
from output import send_email, build_html_content
from llmanger import LLManager

def main():
    llmanager = LLManager()
    fetcher = Fetcher(llmanager)

    query = "cs.NE OR cs.MA OR cs.LG OR cs.CV OR cs.CL OR cs.AI"

    arxiv_papers = fetcher.fetch_arxiv_papers(query)

    hacknews_storys = fetcher.fetch_hacknews_storys()

    huggingface_papers = fetcher.fetch_huggingface_papers()

    techcrunch_rss = fetcher.fetch_techcrunch_rss()

    github_trending = fetcher.fetch_github_trending()

    all_articles = []
    all_articles.extend(arxiv_papers)
    all_articles.extend(hacknews_storys)
    all_articles.extend(huggingface_papers)
    all_articles.extend(techcrunch_rss)
    all_articles.extend(github_trending)

    # 洞察信息生成
    report = llmanager.analize_datas(all_articles)

    body = build_html_content(all_articles, report)

    # Send email notification
    send_email('Tech Insight', body)

if __name__ == "__main__":
    main()
